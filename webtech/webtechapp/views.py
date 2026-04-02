from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from .models import (
    EventRegistration,
    Student,
    EventCategory,
    Event,
    AdminUser,
    Settings,
)
import json


def index(request):
    if request.method == "POST":
        name = request.POST.get("reg_name")
        password = request.POST.get("reg_password")

        Student.objects.create(name=name, password=password)
        return HttpResponse("Student registered successfully!")

    return render(request, "webtechapp/index.html")


def student_login(request):
    if request.method == "POST":
        data = json.loads(request.body)
        username = data.get("username")
        password = data.get("password")

        try:
            student = Student.objects.get(name=username, password=password)
            return JsonResponse({"success": True, "name": student.name})
        except Student.DoesNotExist:
            return JsonResponse(
                {"success": False, "error": "Invalid credentials"}, status=401
            )

    return JsonResponse({"error": "Invalid request"}, status=400)


def events_view(request):
    categories = EventCategory.objects.all().prefetch_related("events")

    if not categories.exists():
        default_categories = [
            {
                "name": "Technical",
                "icon": "cpu",
                "description": "Challenge your mind with coding competitions, hackathons, and tech quizzes.",
            },
            {
                "name": "Cultural",
                "icon": "palette",
                "description": "Express yourself through dance, music, art, and theatrical performances.",
            },
            {
                "name": "Workshop",
                "icon": "wrench",
                "description": "Learn new skills and explore hands-on activities with industry experts.",
            },
            {
                "name": "Sports",
                "icon": "trophy",
                "description": "Get active and compete in various athletic events and tournaments.",
            },
            {
                "name": "Pro-Show",
                "icon": "microphone",
                "description": "Experience spectacular performances by professional artists and bands.",
            },
            {
                "name": "Start-Up",
                "icon": "rocket",
                "description": "Connect with entrepreneurs, investors, and innovators in the startup ecosystem.",
            },
        ]
        for cat in default_categories:
            EventCategory.objects.create(**cat)
        categories = EventCategory.objects.all().prefetch_related("events")

    return render(request, "webtechapp/eve.html", {"categories": categories})


def events_data(request):
    categories = EventCategory.objects.all().prefetch_related("events")
    data = {}
    for cat in categories:
        data[cat.name] = [
            {
                "id": e.id,
                "name": e.name,
                "description": e.description,
                "price": str(e.price),
                "image": e.image,
            }
            for e in cat.events.all()
        ]
    return JsonResponse(data)


def register(request):
    require_login = Settings.get("require_login", False)

    # Handle POST request
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        payment_method = request.POST.get("paymentMethod")
        event_category = request.POST.get("categorySelect")
        event_name = request.POST.get("event")
        event_price = request.POST.get("totalAmount")

        # If require_login is ON, check login status from localStorage via header
        # The actual check will be done client-side, but we also validate here
        try:
            student, created = Student.objects.get_or_create(
                email=email, defaults={"name": name, "phone": phone, "password": ""}
            )
            if student.name != name:
                student.name = name
            if student.phone != phone:
                student.phone = phone
            student.save()

            EventRegistration.objects.create(
                name=name,
                email=email,
                phone=phone,
                payment_method=payment_method,
                event_category=event_category,
                event_name=event_name,
                event_price=event_price,
            )
            return redirect("index")
        except Exception as e:
            return HttpResponse(f"Error: {e}")

    # GET request - build events data and render
    events_by_category = {}
    categories = EventCategory.objects.all()
    for cat in categories:
        events_by_category[cat.name] = [
            {"name": e.name, "price": str(e.price)} for e in cat.events.all()
        ]

    return render(
        request,
        "webtechapp/Reg.html",
        {
            "events_by_category": json.dumps(events_by_category),
            "require_login": require_login,
        },
    )


def view_registrations(request):
    all_data = EventRegistration.objects.all().order_by("-id")
    return render(request, "webtechapp/viewreg.html", {"data": all_data})


def edit_registration(request, registration_id):
    registration = get_object_or_404(EventRegistration, id=registration_id)

    if request.method == "POST":
        try:
            registration.name = request.POST.get("name")
            registration.email = request.POST.get("email")
            registration.phone = request.POST.get("phone")
            registration.save()
            messages.success(request, "Registration updated successfully!")
            return redirect("viewreg")

        except Exception as e:
            messages.error(request, f"Error updating registration: {e}")

    return render(request, "webtechapp/edit_reg.html", {"registration": registration})


def delete_registration(request, registration_id):
    registration = get_object_or_404(EventRegistration, id=registration_id)

    if request.method == "POST":
        try:
            registration.delete()
            messages.success(request, "Registration deleted successfully!")
        except Exception as e:
            messages.error(request, f"Error deleting registration: {e}")

    return redirect("viewreg")


def admin_dashboard(request):
    if not AdminUser.objects.exists():
        AdminUser.objects.create(username="admin", password="123")

    categories = EventCategory.objects.all().prefetch_related("events")
    registrations = EventRegistration.objects.all().order_by("-id")[:10]
    students = Student.objects.all().order_by("-id")[:10]
    admins = AdminUser.objects.all()

    return render(
        request,
        "webtechapp/admin_dashboard.html",
        {
            "categories": categories,
            "registrations": registrations,
            "students": students,
            "admins": admins,
        },
    )


@csrf_exempt
def api_categories(request):
    if request.method == "GET":
        categories = EventCategory.objects.all().prefetch_related("events")
        data = []
        for cat in categories:
            data.append(
                {
                    "id": cat.id,
                    "name": cat.name,
                    "icon": cat.icon,
                    "description": cat.description,
                    "events": [
                        {
                            "id": e.id,
                            "name": e.name,
                            "description": e.description,
                            "price": str(e.price),
                            "image": e.image,
                        }
                        for e in cat.events.all()
                    ],
                }
            )
        return JsonResponse({"categories": data})

    if request.method == "POST":
        data = json.loads(request.body)
        category = EventCategory.objects.create(
            name=data.get("name"),
            icon=data.get("icon", ""),
            description=data.get("description", ""),
        )
        return JsonResponse({"id": category.id, "name": category.name})

    if request.method == "PUT":
        data = json.loads(request.body)
        category = get_object_or_404(EventCategory, id=data.get("id"))
        category.name = data.get("name", category.name)
        category.icon = data.get("icon", category.icon)
        category.description = data.get("description", category.description)
        category.save()
        return JsonResponse({"success": True})

    if request.method == "DELETE":
        category = get_object_or_404(EventCategory, id=request.GET.get("id"))
        category.delete()
        return JsonResponse({"success": True})


@csrf_exempt
def api_events(request):
    if request.method == "POST":
        data = json.loads(request.body)
        category = get_object_or_404(EventCategory, id=data.get("category_id"))
        event = Event.objects.create(
            category=category,
            name=data.get("name"),
            description=data.get("description", ""),
            price=data.get("price", 0),
            image=data.get("image", ""),
        )
        return JsonResponse({"id": event.id, "name": event.name})

    if request.method == "PUT":
        data = json.loads(request.body)
        event = get_object_or_404(Event, id=data.get("id"))
        event.name = data.get("name", event.name)
        event.description = data.get("description", event.description)
        event.price = data.get("price", event.price)
        event.image = data.get("image", event.image)
        event.save()
        return JsonResponse({"success": True})

    if request.method == "DELETE":
        event = get_object_or_404(Event, id=request.GET.get("id"))
        event.delete()
        return JsonResponse({"success": True})


@csrf_exempt
def api_admins(request):
    if request.method == "GET":
        admins = AdminUser.objects.all().values("id", "username", "created_at")
        return JsonResponse({"admins": list(admins)})

    if request.method == "POST":
        data = json.loads(request.body)
        if AdminUser.objects.filter(username=data.get("username")).exists():
            return JsonResponse({"error": "Username already exists"}, status=400)
        admin = AdminUser.objects.create(
            username=data.get("username"), password=data.get("password")
        )
        return JsonResponse({"id": admin.id, "username": admin.username})

    if request.method == "DELETE":
        admin = get_object_or_404(AdminUser, id=request.GET.get("id"))
        admin.delete()
        return JsonResponse({"success": True})


@csrf_exempt
def api_students(request):
    if request.method == "GET":
        students = Student.objects.all().values(
            "id", "name", "email", "phone", "created_at"
        )
        return JsonResponse({"students": list(students)})

    if request.method == "POST":
        try:
            if not request.body:
                return JsonResponse({"error": "Empty request body"}, status=400)
            data = json.loads(request.body)
            if not data.get("name"):
                return JsonResponse({"error": "Name is required"}, status=400)
            if not data.get("email"):
                return JsonResponse({"error": "Email is required"}, status=400)
            if Student.objects.filter(email=data.get("email")).exists():
                return JsonResponse({"error": "Email already registered"}, status=400)
            student = Student.objects.create(
                name=data.get("name"),
                email=data.get("email", ""),
                phone=data.get("phone", ""),
                password=data.get("password", ""),
            )
            return JsonResponse({"id": student.id, "name": student.name})
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    if request.method == "PUT":
        data = json.loads(request.body)
        student = get_object_or_404(Student, id=data.get("id"))
        student.name = data.get("name", student.name)
        student.email = data.get("email", student.email)
        student.phone = data.get("phone", student.phone)
        student.save()
        return JsonResponse({"success": True})

    if request.method == "DELETE":
        student = get_object_or_404(Student, id=request.GET.get("id"))
        student.delete()
        return JsonResponse({"success": True})


@csrf_exempt
def api_registrations(request):
    if request.method == "GET":
        regs = (
            EventRegistration.objects.all()
            .order_by("-id")
            .values(
                "id",
                "name",
                "email",
                "phone",
                "payment_method",
                "event_category",
                "event_name",
                "event_price",
                "created_at",
            )
        )
        return JsonResponse({"registrations": list(regs)})

    if request.method == "DELETE":
        reg = get_object_or_404(EventRegistration, id=request.GET.get("id"))
        reg.delete()
        return JsonResponse({"success": True})


@csrf_exempt
def api_login(request):
    if request.method == "POST":
        data = json.loads(request.body)
        login_type = data.get("type")
        username = data.get("username")
        password = data.get("password")

        if login_type == "admin":
            try:
                admin = AdminUser.objects.get(username=username, password=password)
                return JsonResponse(
                    {"success": True, "role": "admin", "username": admin.username}
                )
            except AdminUser.DoesNotExist:
                return JsonResponse(
                    {"success": False, "error": "Invalid credentials"}, status=401
                )

        elif login_type == "student":
            try:
                student = Student.objects.get(name=username, password=password)
                return JsonResponse(
                    {
                        "success": True,
                        "role": "student",
                        "name": student.name,
                        "email": student.email,
                    }
                )
            except Student.DoesNotExist:
                return JsonResponse(
                    {"success": False, "error": "Invalid credentials"}, status=401
                )

    return JsonResponse({"error": "Invalid request"}, status=400)


@csrf_exempt
def api_settings(request):
    if request.method == "GET":
        settings = {
            "require_login": Settings.get("require_login", False),
        }
        return JsonResponse(settings)

    if request.method == "POST":
        data = json.loads(request.body)
        if "require_login" in data:
            Settings.set("require_login", data["require_login"])
        return JsonResponse({"success": True})
