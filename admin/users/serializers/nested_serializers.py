from rest_framework import serializers

class NestedCourseListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    description = serializers.CharField()
    level = serializers.CharField()
    language = serializers.CharField()
    thumbnail_url = serializers.URLField()
    sections_url = serializers.URLField()

class NestedCourseDetailSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    description = serializers.CharField()
    level = serializers.CharField()
    language = serializers.CharField()
    thumbnail_url = serializers.URLField()
    progress_percentage = serializers.CharField()
    completed_at = serializers.DateTimeField()
    sections_url = serializers.URLField()

class NestedSectionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    order_number = serializers.IntegerField()
    lessons_url = serializers.URLField()

class NestedSectionListSerializer(serializers.Serializer):
    course_id = serializers.IntegerField()
    course_title = serializers.CharField()
    sections = NestedSectionSerializer(many=True)

class NestedLessonSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    order_number = serializers.IntegerField()
    duration_seconds = serializers.IntegerField()
    is_preview = serializers.BooleanField()
    is_completed = serializers.BooleanField()
    has_video = serializers.BooleanField()
    lesson_url = serializers.URLField()

class NestedLessonListSerializer(serializers.Serializer):
    course_id = serializers.IntegerField()
    section_id = serializers.IntegerField()
    section_title = serializers.CharField()
    total_lessons = serializers.IntegerField()
    lessons = NestedLessonSerializer(many=True)

class NestedLessonDetailSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    order_number = serializers.IntegerField()
    duration_seconds = serializers.IntegerField()
    is_preview = serializers.BooleanField()
    section = serializers.DictField()
    video = serializers.DictField(allow_null=True)
    video_url = serializers.URLField()
    quiz = serializers.DictField(allow_null=True)
    questions_url = serializers.URLField(allow_null=True)
    mark_complete_url = serializers.URLField()
    watch_time_url = serializers.URLField()
    progress = serializers.DictField()

class NestedMarkCompleteResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    lesson_id = serializers.IntegerField()
    lesson_title = serializers.CharField()
    is_completed = serializers.BooleanField()
    watch_time_seconds = serializers.IntegerField()
    course_progress_percentage = serializers.CharField()
