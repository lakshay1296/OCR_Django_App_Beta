# -*- coding: utf-8 -*-
from django.db import models

# Create your models here.

class FileName(models.Model):
    file_name = models.CharField(max_length=500)
    file_extension = models.CharField(max_length=100)