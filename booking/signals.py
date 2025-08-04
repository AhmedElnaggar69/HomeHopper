    # booking/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile, OwnerProfile # Import OwnerProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
            # Only create UserProfile if no OwnerProfile exists for this user
            # This assumes an owner signup process would create OwnerProfile first
            # or that you'll explicitly manage which profile type is created.
            # A more robust solution might involve a 'user_type' field on UserProfile/OwnerProfile
            # or a custom User model.
        if not hasattr(instance, 'owner_profile'):
            UserProfile.objects.get_or_create(user=instance)

    # You might also need a signal for OwnerProfile if it's not created directly in signup view
    # @receiver(post_save, sender=User)
    # def create_owner_profile(sender, instance, created, **kwargs):
    #     if created:
    #         # This would be triggered for ALL new users, so you need a way to differentiate
    #         # if the user is intended to be an owner at creation time.
    #         # For now, rely on the owner_signup_view to create OwnerProfile explicitly.
    #         pass
    