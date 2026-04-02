from django.db import models


class Todo(models.Model):
    content = models.TextField()


class EventCategory(models.Model):
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Event(models.Model):
    category = models.ForeignKey(
        EventCategory, on_delete=models.CASCADE, related_name="events"
    )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.category.name})"


class AdminUser(models.Model):
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username


class Student(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    password = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class EventRegistration(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    payment_method = models.CharField(max_length=50)
    event_name = models.CharField(max_length=100)
    event_category = models.CharField(max_length=100)
    event_price = models.DecimalField(max_digits=8, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.event_name}"


class Settings(models.Model):
    key = models.CharField(max_length=100, unique=True)
    value = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.key}: {self.value}"

    @classmethod
    def get(cls, key, default=False):
        try:
            return cls.objects.get(key=key).value
        except cls.DoesNotExist:
            return default

    @classmethod
    def set(cls, key, value):
        cls.objects.update_or_create(key=key, defaults={"value": value})
