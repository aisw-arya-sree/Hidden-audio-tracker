from django.db import models
from django.contrib.auth.models import AbstractUser
from django.forms import CharField


# Create your models here.


class Login(AbstractUser):
    userType = models.CharField(max_length=100)
    viewPass = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.username


class Person(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    phone = models.IntegerField()
    address = models.CharField(max_length=300)
    gender = models.CharField(max_length=300)
    dob = models.CharField(max_length=300)
    image = models.FileField()
    status = models.CharField(max_length=100, default="View")
    loginid = models.ForeignKey(Login, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Message(models.Model):
    sender = models.ForeignKey(
        Person, on_delete=models.CASCADE, related_name="sent_messages"
    )
    receiver = models.ForeignKey(
        Person, on_delete=models.CASCADE, related_name="received_messages"
    )
    subject = models.TextField()
    msg = models.TextField()
    date = models.DateField(auto_now=True)
    password = models.CharField(max_length=100)
    file = models.FileField()
    attachment = models.FileField(null=True, blank=True)
    status = models.CharField(max_length=100)


class Feedback(models.Model):
    uid = models.ForeignKey(Person, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    feedback = models.TextField()
    date = models.DateField(auto_now=True)
