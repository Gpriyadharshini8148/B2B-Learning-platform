from rest_framework import serializers
from admin.access.models.section import Section

class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ('id', 'title', 'order_number', 'organization', 'course')
        read_only_fields = ('id', 'organization', 'course')


