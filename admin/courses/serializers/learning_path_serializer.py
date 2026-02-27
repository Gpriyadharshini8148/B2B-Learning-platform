from rest_framework import serializers
from ..models.learning_path import LearningPath

class LearningPathSerializer(serializers.ModelSerializer):
    class Meta:
        model = LearningPath
        fields = '__all__'
