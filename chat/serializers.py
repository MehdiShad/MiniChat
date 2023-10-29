from rest_framework import serializers
from .models import Message

class Messageserializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['__str__', 'content', 'timestamp']