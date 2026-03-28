from django.db import models

class Notification(models.Model):
    type = models.CharField(max_length=50)
    message = models.TextField()
    envoye = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.type
