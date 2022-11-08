import string , random
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import School , Channel


def random_string_generator_school(size=15, chars = string.ascii_uppercase + string.digits):
    result = ''.join(random.choice(chars) for _ in range(size))
    if School.objects.filter(identifier=result).exists():
        return random_string_generator_school(size , chars)
    return result


def random_string_generator_channel_invitation_code(size=12, chars = string.ascii_uppercase + string.digits):
    result = ''.join(random.choice(chars) for _ in range(size))
    result = 'IV'+result
    if Channel.objects.filter(invitation_code=result).exists():
        return random_string_generator_channel_invitation_code(size , chars)
    return result

def random_string_generator_channel(size=12, chars = string.ascii_uppercase + string.digits):
    result = ''.join(random.choice(chars) for _ in range(size))
    result = 'CH'+result
    if Channel.objects.filter(identifier=result).exists():
        return random_string_generator_channel(size , chars)  
    return result


@receiver(post_save , sender=School)
def user_profile_signal(sender, instance , created , **kwarg):
    if created:
        instance.identifier = random_string_generator_school()
        instance.save()


@receiver(post_save , sender=Channel)
def user_profile_signal(sender, instance , created , **kwarg):
    if created:
        instance.identifier = random_string_generator_channel()
        instance.invitation_code  = random_string_generator_channel_invitation_code() 
        instance.save() 