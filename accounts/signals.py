import string , random
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User , Student , Parent , ChannelUser
from rest_framework.authtoken.models import Token

def random_string_generator_user(size=15, chars = string.ascii_uppercase + string.digits):
    result = ''.join(random.choice(chars) for _ in range(size))
    result = 'US'+result
    if User.objects.filter(identifier=result).exists():
        return random_string_generator_user(size , chars)
    return result


def random_string_generator_student(size=13, chars = string.ascii_uppercase + string.digits):
    result = ''.join(random.choice(chars) for _ in range(size))
    result = 'ST'+result
    if Student.objects.filter(identifier=result).exists():
        return random_string_generator_student(size , chars)
    return result



def random_string_generator_channel_user(size=13, chars = string.ascii_uppercase + string.digits):
    result = ''.join(random.choice(chars) for _ in range(size))
    result = 'CU'+result
    if ChannelUser.objects.filter(identifier=result).exists():
        return random_string_generator_student(size , chars)
    return result



@receiver(post_save , sender=User)
def user_profile_signal(sender, instance , created , **kwarg):
    if created:
        instance.identifier = random_string_generator_user()
        instance.save()
        Token.objects.create(user=instance)

        


@receiver(post_save , sender=Student)
def user_profile_signal(sender, instance , created , **kwarg):
    if created:
        instance.identifier = random_string_generator_student()
        instance.save()
 

#  This signal generate unique identifier for the channel user object
@receiver(post_save , sender=ChannelUser) 
def channel_user_signal(sender, instance , created , **kwarg):
    if created:
        instance.identifier = random_string_generator_channel_user()
        instance.save()