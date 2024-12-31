# champapp/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from champapp.models import InstructorProfile

@receiver(post_save, sender=User)
def create_instructor_profile(sender, instance, created, **kwargs):
    if created and instance.is_staff:
        InstructorProfile.objects.get_or_create(user=instance)
