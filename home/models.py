from django.db import models

# Create your models here.

class NormalUser(models.Model):
    userid = models.CharField(max_length=250, primary_key=True)
    user_first_name = models.CharField(max_length=250)
    user_last_name = models.CharField(max_length=250)
    user_email = models.CharField(max_length=250)
    user_password = models.CharField(max_length=250)

