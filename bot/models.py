# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import models
#from twostepauth.models import TwoStepAuthBaseProfile
# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, unique=True, null=False, db_index=True)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
#class UserProfile(TwoStepAuthBaseProfile):
#    user = models.OneToOneField('auth.User')
