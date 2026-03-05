from rest_framework import serializers

class OrgStatsSerializer(serializers.Serializer):
    total_learners = serializers.IntegerField()
    active_courses = serializers.IntegerField()
    total_enrollments = serializers.IntegerField()
    pending_invitations = serializers.IntegerField()

class OrgOverviewResponseSerializer(serializers.Serializer):
    organization_name = serializers.CharField()
    stats = OrgStatsSerializer()

class PopularCourseSerializer(serializers.Serializer):
    course_title = serializers.CharField(source='enrollment__course__title')
    count = serializers.IntegerField()

class OrgInsightsResponseSerializer(serializers.Serializer):
    average_org_completion = serializers.FloatField()
    popular_courses = PopularCourseSerializer(many=True)

class MessageResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
