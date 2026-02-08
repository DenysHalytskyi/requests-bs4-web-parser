from django.db import models


class Product(models.Model):
    title = models.CharField(max_length=100, null=False, blank=False)
    color = models.CharField(max_length=50, null=False, blank=False)
    memory = models.CharField(max_length=20, null=True, blank=True)
    producer = models.CharField(max_length=100, null=False, blank=False)
    price = models.FloatField(null=False, blank=False)
    product_code = models.CharField(max_length=100, null=False, blank=False)
    review_count = models.IntegerField(null=True, blank=True, default=0)
    screen_diagonal = models.CharField(max_length=10, null=True, blank=True)
    display_resolution = models.CharField(max_length=50, null=True, blank=True)
    images = models.TextField()
    characteristics = models.JSONField(default=dict)

    def __str__(self) -> str:
        return f"{self.title} (code: {self.product_code})"
