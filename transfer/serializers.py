from rest_framework import serializers
from .models import ParishRestructure

class ParishRestructureSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParishRestructure
        fields = '__all__'  # or specify the fields you want to include
