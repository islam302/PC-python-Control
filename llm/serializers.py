from rest_framework import serializers
from .models import Objective, CommandLog

class ObjectiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Objective
        fields = '__all__'

class CommandLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommandLog
        fields = '__all__'
