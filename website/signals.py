import os

from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete, pre_save
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver
from PIL import Image
from django.conf import settings
from .models import Profile, UserAuthAuditEntry

@receiver(post_save, sender=User)
def createUserProfile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def saveUserProfile(sender, instance, **kwargs):
    instance.profile.save()

@receiver(post_save, sender=Profile)
def updatePhoto(sender, instance, **kwargs):
    image = Image.open(instance.photo.file)
    image.thumbnail(settings.THUMBNAIL_SIZE, Image.ANTIALIAS)
    image.save(instance.photo.path)

def removeProfilePhoto(photo):
    if os.path.basename(photo.name) != "defaultuser.png":
        if os.path.isfile(photo.path):
            try:
                os.remove(photo.path)
                return True
            except:
                return False
    return False

@receiver(post_delete, sender=Profile)
def deleteOnDelete(sender, instance, **kwargs):
    if instance.photo:
        removeProfilePhoto(instance.photo)
        return True
    return False

@receiver(pre_save, sender=Profile)
def deleteOnChange(sender, instance, **kwargs):
    if not instance.pk:
        return False

    try:
        oldPhoto = Profile.objects.get(pk=instance.pk).photo
    except Profile.DoesNotExist:
        return False

    newPhoto = instance.photo
    if not newPhoto == oldPhoto:
        removeProfilePhoto(oldPhoto)
        return True
    return False

@receiver(user_logged_in)
def user_logged_in_callback(sender, request, user, **kwargs):
    ip = request.META.get('REMOTE_ADDR')
    UserAuthAuditEntry.objects.create(action='logged_in', ip=ip, user=user)

@receiver(user_logged_out)
def user_logged_out_callback(sender, request, user, **kwargs):
    ip = request.META.get('REMOTE_ADDR')
    UserAuthAuditEntry.objects.create(action='logged_out', ip=ip, user=user)

@receiver(user_login_failed)
def user_login_failed_callback(sender, credentials, request, **kwargs):
    ip = request.META.get('REMOTE_ADDR')
    UserAuthAuditEntry.objects.create(action='invalid_login', ip=ip, username=credentials.get('username', None))
