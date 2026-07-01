from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.
class User(AbstractUser):
    class Role(models.TextChoices):
        CUSTOMER = "customer", "Customer"
        OWNER = "owner", "Owner"
        STAFF = "staff", "Staff"
        DELIVERY_STAFF = "delivery_staff", "Delivery Staff"

    email = models.EmailField(unique=True)  
    phone = models.CharField(
        max_length=16, 
        unique=True
    )
    address = models.CharField(max_length=50, blank=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CUSTOMER)


    class Meta:
        indexes= [models.Index(fields=['role'])]

    def __str__(self):
        return self.username

    