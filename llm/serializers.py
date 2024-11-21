
from rest_framework import serializers


class CommandSerializer(serializers.Serializer):
    action = serializers.CharField()
