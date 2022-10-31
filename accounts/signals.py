import string , random
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User , Student , Parent
from rest_framework.authtoken.models import Token

def random_string_generator(size=15, chars = string.ascii_uppercase + string.digits):
    result = ''.join(random.choice(chars) for _ in range(size))
    if User.objects.filter(identifier=result).exists():
        return random_string_generator(size , chars)
    return result


def random_string_generator_student(size=15, chars = string.ascii_uppercase + string.digits):
    result = ''.join(random.choice(chars) for _ in range(size))
    if Student.objects.filter(identifier=result).exists():
        return random_string_generator_student(size , chars)
    return result



@receiver(post_save , sender=User)
def user_profile_signal(sender, instance , created , **kwarg):
    if created:
        instance.identifier = random_string_generator()
        instance.save()
        Token.objects.create(user=instance)
        if instance.is_parent :
            Parent.objects.create(user=instance)

        




@receiver(post_save , sender=Student)
def user_profile_signal(sender, instance , created , **kwarg):
    if created:
        instance.identifier = random_string_generator_student()
        instance.save()
