from django.db import models

class Product(models.Model):
    class Category(models.TextChoices):
        FRUITS = "fruits", "Fruits"
        VEGETABLES = "vegetables", "Vegetables"
        DAIRY = "dairy", "Dairy"
        MEAT = "meat", "Meat"
        BAKERY = "bakery", "Bakery"
        BEVERAGES = "beverages", "Beverages"
        SNACKS = "snacks", "Snacks"
        HOUSEHOLD = "household", "Household"
        SKINCARE = "skincare", "Skincare"
        OTHER = "other", "Other"

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.OTHER)
    image_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
