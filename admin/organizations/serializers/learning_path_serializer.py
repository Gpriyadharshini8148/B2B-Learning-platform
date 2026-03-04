from rest_framework import serializers
from admin.access.models.learning_path import LearningPath

class LearningPathSerializer(serializers.ModelSerializer):
    class Meta:
        model = LearningPath
        fields = ('id', 'name', 'description', 'organization')


