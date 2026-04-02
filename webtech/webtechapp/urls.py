from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", views.index, name="index"),
    path("eve/", views.events_view, name="eve"),
    path("events-data/", views.events_data, name="events_data"),
    path("Reg/", views.register, name="Reg"),
    path("viewreg/", views.view_registrations, name="viewreg"),
    path(
        "edit-registration/<int:registration_id>/",
        views.edit_registration,
        name="edit_registration",
    ),
    path(
        "delete-registration/<int:registration_id>/",
        views.delete_registration,
        name="delete_registration",
    ),
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("api/categories/", views.api_categories, name="api_categories"),
    path("api/events/", views.api_events, name="api_events"),
    path("api/admins/", views.api_admins, name="api_admins"),
    path("api/students/", views.api_students, name="api_students"),
    path("api/registrations/", views.api_registrations, name="api_registrations"),
    path("api/login/", views.api_login, name="api_login"),
    path("api/settings/", views.api_settings, name="api_settings"),
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
