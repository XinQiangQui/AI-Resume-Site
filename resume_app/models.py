from django.db import models

class Resume(models.Model):
    name = models.CharField(max_length=200)
    file = models.FileField(upload_to='resumes')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.CharField(max_length=200)

class Person(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    password = models.CharField(max_length=200)
    isVIP = models.BooleanField(default=False)
    freeChance = models.IntegerField(default=5)