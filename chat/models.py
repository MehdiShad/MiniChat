from django.core.management import call_command
from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.
user = get_user_model()


class Chat(models.Model):
    room_name = models.CharField(null=True, blank=True, max_length=75)
    members = models.ManyToManyField(user, null=True, blank=True)

    def __str__(self):
        return self.room_name


class Message(models.Model):
    author = models.ForeignKey(user, on_delete=models.CASCADE)
    content = models.TextField()
    related_chat = models.ForeignKey(Chat, on_delete=models.CASCADE, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def last_message(self, room_name):
        # return Message.objects.order_by("-timestamp").all()
        return Message.objects.filter(related_chat__room_name=room_name)
    
    def __str__(self):
        return self.author.username
