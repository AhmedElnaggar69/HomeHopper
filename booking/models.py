from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator  # Correct import

class Owner(models.Model):  # Class names should be capitalized
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    reviews = models.FloatField(validators=[MinValueValidator(1), MaxValueValidator(5)], null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} - {self.last_name}"

class LocationForApartment(models.Model): # Class names should be capitalized
    title = models.CharField(max_length=50)
    owner_name = models.ForeignKey(Owner, on_delete=models.CASCADE) # Corrected model name
    description = models.CharField(max_length=400)
    price = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(1000000)])
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return f"{self.title} - {self.owner_name} - ${self.price} - ({self.latitude}, {self.longitude})"

class region(models.Model):
    name = models.CharField(max_length=50)
    books_from = models.ManyToManyField(LocationForApartment) # Corrected model name

    def __str__(self):
        return f"{self.name}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_profile')
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Profile for {self.user.username}"

class OwnerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='owner_profile')
    company_name = models.CharField(max_length=100, blank=True, null=True)


class Apartment(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='apartments')
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    apartment = models.ForeignKey(Apartment, on_delete=models.SET_NULL, null=True, blank=True, related_name='messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"From {self.sender.username} to {self.receiver.username} ({self.timestamp.strftime('%Y-%m-%d %H:%M')})"
