from django.db import models

class User(models.Model):
    email = models.EmailField(unique=True)
    nom = models.CharField(max_length=100)
    telephone = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
