from rest_framework import serializers
from .models import ParishDirectory

class ParishDirectorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ParishDirectory
        fields = '__all__'  # or specify the fields you want to include
