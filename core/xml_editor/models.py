from django.db import models

class Settings(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=100, unique=True)
    value = models.CharField(max_length=255)
    category = models.CharField(max_length=100)
    
    class Meta:
        verbose_name = "Setting"
        verbose_name_plural = "Settings"
        
    def __str__(self):
        return f"{self.name} ({self.category})"