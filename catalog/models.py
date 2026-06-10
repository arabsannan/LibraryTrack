from django.db import models

class Library(models.Model):
    # Represents a physical library branch.
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name