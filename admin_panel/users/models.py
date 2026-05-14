from django.db import models
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    passphrase = models.CharField('Кодовая фраза', max_length=255, blank=True, default='')

    class Meta:
        db_table = 'user_profile'
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'

    def __str__(self):
        return f'Profile({self.user.username})'


@receiver(post_save, sender=User)
def assign_admin_group_to_superuser(sender, instance, created, **kwargs):
    if created and instance.is_superuser:
        group, _ = Group.objects.get_or_create(name='admin')
        instance.groups.add(group)