from rest_framework import serializers
from admin.access.models.certificate import Certificate

class CertificateSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='enrollment.user.email', read_only=True)
    course_title = serializers.CharField(source='enrollment.course.title', read_only=True)

    class Meta:
        model = Certificate
        fields = ('id', 'certificate_url', 'enrollment', 'user_email', 'course_title')
        read_only_fields = ('certificate_url',)
