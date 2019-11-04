from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField


class CustomUser(AbstractUser):

    cc = models.BigIntegerField(primary_key=True, null=False, blank=False)
    first_name = models.CharField(max_length=512, unique=True, null=False, blank=False)
    last_name = models.CharField(max_length=512, unique=True, null=False, blank=False)
    phone = PhoneNumberField(null=True, blank=True, unique=True, region="PT")
    budget = models.BigIntegerField(null=False)
    hierarchy = models.IntegerField(null=False)
    image = models.FileField(upload_to="users/%Y/%m/%d/", null=True, blank=True)
    # position = models.ManyToManyField(position, on_delete=models.PROTECT)

    class Meta:
        db_table = "CustomUser"
        verbose_name = "Utilizador"
        verbose_name_plural = "Utilizadores"
        ordering = ["-username"]

    def __str__(self):
        return self.username
