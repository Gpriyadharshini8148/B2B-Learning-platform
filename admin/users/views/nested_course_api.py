

from django.utils import timezone
from django.shortcuts import get_object_or_404

from rest_framework import views, permissions, status
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from admin.access.models.course import Course
from admin.access.models.section import Section
from admin.access.models.lesson import Lesson
from admin.access.models.video import Video
from admin.access.models.quiz import Quiz
from admin.access.models.question import Question
from admin.access.models.option import Option
from admin.access.models.enrollment import Enrollment
from admin.access.models.lesson_progress import LessonProgress
from admin.access.models.course_progress import CourseProgress
from drf_spectacular.utils import extend_schema
from ..serializers.nested_serializers import (
    NestedCourseListSerializer, NestedCourseDetailSerializer,
    NestedSectionListSerializer, NestedSectionSerializer,
    NestedLessonListSerializer, NestedLessonDetailSerializer,
    NestedMarkCompleteResponseSerializer
)


# ─────────────────────────────────────────────────────────────────────────────
# Shared helpers
# ─────────────────────────────────────────────────────────────────────────────

def _get_enrollment(user, course_id):
    """
    Return the most recent enrollment for user+course.
    Raises NotFound (HTTP 404) if not enrolled.
    Uses .filter().first() to avoid MultipleObjectsReturned.
    """
    enrollment = (
        Enrollment.objects
        .filter(user=user, course_id=course_id)
        .order_by('-created_at')
        .first()
    )
    if enrollment is None:
        raise NotFound({"error": "You are not enrolled in this course."})
    return enrollment


def _video_url(request, video):
    if video and video.video_file:
        return request.build_absolute_uri(video.video_file.url)
    return None


def _get_course(course_id):
    """Fetch a course by PK. No is_published guard — enrolled users may
    access their course content regardless of publish state."""
    return get_object_or_404(Course, pk=course_id, is_deleted=False)


def _get_section(course, section_id):
    return get_object_or_404(Section, pk=section_id, course=course)


def _get_lesson(section, lesson_id):
    return get_object_or_404(Lesson, pk=lesson_id, section=section)


def _get_question(lesson, question_id):
    """
    Questions live on a Quiz which is attached to the lesson.
    """
    quiz = Quiz.objects.filter(lesson=lesson).first()
    if not quiz:
        raise NotFound({"error": "No quiz attached to this lesson."})
    return get_object_or_404(Question, pk=question_id, quiz=quiz)

class NestedCourseListAPIView(views.APIView):
    """
    GET /api/users/courses/
    List all published courses available to the user's organisation.
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(responses={200: NestedCourseListSerializer}, operation_id='api_users_courses_list')
    def get(self, request):
        org = getattr(request.user, 'organization', None)
        courses = Course.objects.filter(
            organization=org, is_published=True, is_deleted=False
        )
        data = [
            {
                "id": c.id,
                "title": c.title,
                "description": c.description,
                "level": c.level,
                "language": c.language,
                "thumbnail_url": c.thumbnail_url,
                "sections_url": request.build_absolute_uri(
                    f"/api/users/courses/{c.id}/sections/"
                ),
            }
            for c in courses
        ]
        return Response({"count": len(data), "courses": data})


class NestedCourseDetailAPIView(views.APIView):
    """
    GET /api/users/courses/<course_id>/
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(responses={200: NestedCourseDetailSerializer}, operation_id='api_users_courses_detail')
    def get(self, request, course_id):
        course = _get_course(course_id)
        enrollment = _get_enrollment(request.user, course_id)
        progress, _ = CourseProgress.objects.get_or_create(enrollment=enrollment)

        return Response({
            "id": course.id,
            "title": course.title,
            "description": course.description,
            "level": course.level,
            "language": course.language,
            "thumbnail_url": course.thumbnail_url,
            "progress_percentage": str(progress.progress_percentage),
            "completed_at": progress.completed_at,
            "sections_url": request.build_absolute_uri(
                f"/api/users/courses/{course_id}/sections/"
            ),
        })


class NestedSectionListAPIView(views.APIView):
    """
    GET /api/users/courses/<course_id>/sections/
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(responses={200: NestedSectionListSerializer}, operation_id='api_users_courses_sections_list')
    def get(self, request, course_id):
        _get_enrollment(request.user, course_id)
        course = _get_course(course_id)

        sections = Section.objects.filter(course=course).order_by('order_number')
        data = [
            {
                "id": s.id,
                "title": s.title,
                "order_number": s.order_number,
                "lessons_url": request.build_absolute_uri(
                    f"/api/users/courses/{course_id}/sections/{s.id}/lessons/"
                ),
            }
            for s in sections
        ]
        return Response({
            "course_id": course.id,
            "course_title": course.title,
            "sections": data,
        })


class NestedSectionDetailAPIView(views.APIView):
    """
    GET /api/users/courses/<course_id>/sections/<section_id>/
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(responses={200: dict}, operation_id='api_users_courses_sections_detail')
    def get(self, request, course_id, section_id):
        _get_enrollment(request.user, course_id)
        course = _get_course(course_id)
        section = _get_section(course, section_id)

        lessons_count = Lesson.objects.filter(section=section).count()
        return Response({
            "id": section.id,
            "title": section.title,
            "order_number": section.order_number,
            "total_lessons": lessons_count,
            "lessons_url": request.build_absolute_uri(
                f"/api/users/courses/{course_id}/sections/{section_id}/lessons/"
            ),
        })



class NestedLessonListAPIView(views.APIView):
    """
    GET /api/users/courses/<course_id>/sections/<section_id>/lessons/
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(responses={200: NestedLessonListSerializer}, operation_id='api_users_courses_sections_lessons_list')
    def get(self, request, course_id, section_id):
        enrollment = _get_enrollment(request.user, course_id)
        course = _get_course(course_id)
        section = _get_section(course, section_id)

        completed_ids = set(
            LessonProgress.objects.filter(
                enrollment=enrollment, is_completed=True
            ).values_list('lesson_id', flat=True)
        )

        lessons = Lesson.objects.filter(section=section).select_related('video').order_by('order_number')
        data = [
            {
                "id": l.id,
                "title": l.title,
                "order_number": l.order_number,
                "duration_seconds": l.duration_seconds,
                "is_preview": l.is_preview,
                "is_completed": l.id in completed_ids,
                "has_video": bool(l.video_id),
                "lesson_url": request.build_absolute_uri(
                    f"/api/users/courses/{course_id}/sections/{section_id}/lessons/{l.id}/"
                ),
            }
            for l in lessons
        ]
        return Response({
            "course_id": course_id,
            "section_id": section_id,
            "section_title": section.title,
            "total_lessons": len(data),
            "lessons": data,
        })


class NestedLessonDetailAPIView(views.APIView):
    """
    GET /api/users/courses/<course_id>/sections/<section_id>/lessons/<lesson_id>/
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(responses={200: NestedLessonDetailSerializer}, operation_id='api_users_courses_sections_lessons_detail')
    def get(self, request, course_id, section_id, lesson_id):
        enrollment = _get_enrollment(request.user, course_id)
        course = _get_course(course_id)
        section = _get_section(course, section_id)
        lesson = _get_lesson(section, lesson_id)

        progress, _ = LessonProgress.objects.get_or_create(
            enrollment=enrollment,
            lesson=lesson,
            defaults={"is_completed": False, "watch_time_seconds": 0},
        )

        video_data = None
        if lesson.video:
            video_data = {
                "id": lesson.video.id,
                "title": lesson.video.title,
                "url": _video_url(request, lesson.video),
                "duration_seconds": lesson.video.duration_seconds,
            }

        # Check if there's a quiz on this lesson
        quiz = Quiz.objects.filter(lesson=lesson).first()

        return Response({
            "id": lesson.id,
            "title": lesson.title,
            "order_number": lesson.order_number,
            "duration_seconds": lesson.duration_seconds,
            "is_preview": lesson.is_preview,
            "section": {"id": section.id, "title": section.title},
            "video": video_data,
            "video_url": request.build_absolute_uri(
                f"/api/users/courses/{course_id}/sections/{section_id}/lessons/{lesson_id}/video/"
            ),
            "quiz": {"id": quiz.id, "title": quiz.title} if quiz else None,
            "questions_url": request.build_absolute_uri(
                f"/api/users/courses/{course_id}/sections/{section_id}/lessons/{lesson_id}/questions/"
            ) if quiz else None,
            "mark_complete_url": request.build_absolute_uri(
                f"/api/users/courses/{course_id}/sections/{section_id}/lessons/{lesson_id}/mark-complete/"
            ),
            "watch_time_url": request.build_absolute_uri(
                f"/api/users/courses/{course_id}/sections/{section_id}/lessons/{lesson_id}/watch-time/"
            ),
            "progress": {
                "is_completed": progress.is_completed,
                "watch_time_seconds": progress.watch_time_seconds,
            },
        })


class NestedLessonVideoAPIView(views.APIView):
    """
    GET /api/users/courses/<course_id>/sections/<section_id>/lessons/<lesson_id>/video/
    Preview lessons (is_preview=True) skip the enrollment check.
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(responses={200: dict, 404: dict})
    def get(self, request, course_id, section_id, lesson_id):
        course = _get_course(course_id)
        section = _get_section(course, section_id)
        lesson = _get_lesson(section, lesson_id)

        if not lesson.is_preview:
            _get_enrollment(request.user, course_id)

        if not lesson.video:
            return Response(
                {"error": "No video attached to this lesson."},
                status=status.HTTP_404_NOT_FOUND
            )

        video = lesson.video
        return Response({
            "lesson_id": lesson.id,
            "lesson_title": lesson.title,
            "video": {
                "id": video.id,
                "title": video.title,
                "url": _video_url(request, video),
                "duration_seconds": video.duration_seconds,
            },
        })


# ─────────────────────────────────────────────────────────────────────────────
# POST /api/users/courses/<course_id>/sections/<section_id>/lessons/<lesson_id>/mark-complete/
# ─────────────────────────────────────────────────────────────────────────────

class NestedMarkCompleteAPIView(views.APIView):
    """
    POST /api/users/courses/<course_id>/sections/<section_id>/lessons/<lesson_id>/mark-complete/
    Body (optional): { "watch_time_seconds": 300 }
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        request=None, 
        responses={200: NestedMarkCompleteResponseSerializer}
    )
    def post(self, request, course_id, section_id, lesson_id):
        enrollment = _get_enrollment(request.user, course_id)
        course = _get_course(course_id)
        section = _get_section(course, section_id)
        lesson = _get_lesson(section, lesson_id)

        watch_time = request.data.get('watch_time_seconds', 0)

        progress, _ = LessonProgress.objects.get_or_create(
            enrollment=enrollment, lesson=lesson,
            defaults={"is_completed": False, "watch_time_seconds": 0},
        )
        progress.is_completed = True
        if watch_time:
            progress.watch_time_seconds = watch_time
        progress.save()

        # Recalculate course %
        total = Lesson.objects.filter(section__course=enrollment.course).count()
        done = LessonProgress.objects.filter(enrollment=enrollment, is_completed=True).count()
        pct = round((done / total * 100), 2) if total else 0.0

        cp, _ = CourseProgress.objects.get_or_create(enrollment=enrollment)
        cp.progress_percentage = pct
        if done == total and total > 0:
            cp.completed_at = timezone.now()
            enrollment.status = 'completed'
            enrollment.save()
        cp.save()

        return Response({
            "message": "Lesson marked as complete",
            "lesson_id": lesson.id,
            "lesson_title": lesson.title,
            "is_completed": True,
            "watch_time_seconds": progress.watch_time_seconds,
            "course_progress_percentage": str(cp.progress_percentage),
        }, status=status.HTTP_200_OK)



class NestedWatchTimeAPIView(views.APIView):
    """
    PATCH /api/users/courses/<course_id>/sections/<section_id>/lessons/<lesson_id>/watch-time/
    Body: { "watch_time_seconds": 150 }
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        request={'watch_time_seconds': int},
        responses={200: dict, 400: dict}
    )
    def patch(self, request, course_id, section_id, lesson_id):
        enrollment = _get_enrollment(request.user, course_id)
        course = _get_course(course_id)
        section = _get_section(course, section_id)
        lesson = _get_lesson(section, lesson_id)

        watch_time = request.data.get('watch_time_seconds')
        if watch_time is None:
            return Response(
                {"error": "watch_time_seconds is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        progress, _ = LessonProgress.objects.get_or_create(
            enrollment=enrollment, lesson=lesson,
            defaults={"is_completed": False, "watch_time_seconds": 0},
        )
        progress.watch_time_seconds = watch_time
        progress.save()

        return Response({
            "lesson_id": lesson.id,
            "lesson_title": lesson.title,
            "watch_time_seconds": progress.watch_time_seconds,
            "is_completed": progress.is_completed,
        })


class NestedQuestionListAPIView(views.APIView):
    """
    GET /api/users/courses/<course_id>/sections/<section_id>/lessons/<lesson_id>/questions/
    Returns the quiz and all its questions (with options) for a lesson.
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(responses={200: dict, 404: dict}, operation_id='api_users_courses_sections_lessons_questions_list')
    def get(self, request, course_id, section_id, lesson_id):
        _get_enrollment(request.user, course_id)
        course = _get_course(course_id)
        section = _get_section(course, section_id)
        lesson = _get_lesson(section, lesson_id)

        quiz = Quiz.objects.filter(lesson=lesson).first()
        if not quiz:
            return Response(
                {"error": "No quiz attached to this lesson."},
                status=status.HTTP_404_NOT_FOUND
            )

        questions = Question.objects.filter(quiz=quiz).prefetch_related('options')
        data = []
        for q in questions:
            data.append({
                "id": q.id,
                "text": q.text,
                "question_type": q.question_type,
                "marks": q.marks,
                "options_url": request.build_absolute_uri(
                    f"/api/users/courses/{course_id}/sections/{section_id}"
                    f"/lessons/{lesson_id}/questions/{q.id}/options/"
                ),
                "options": [
                    {"id": o.id, "text": o.text}   # is_correct hidden until answered
                    for o in q.options.all()
                ],
            })

        return Response({
            "quiz_id": quiz.id,
            "quiz_title": quiz.title,
            "passing_score": quiz.passing_score,
            "total_questions": len(data),
            "questions": data,
        })


class NestedQuestionDetailAPIView(views.APIView):
    """
    GET /api/users/courses/<course_id>/sections/<section_id>/lessons/<lesson_id>/questions/<question_id>/
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(responses={200: dict, 404: dict}, operation_id='api_users_courses_sections_lessons_questions_detail')
    def get(self, request, course_id, section_id, lesson_id, question_id):
        _get_enrollment(request.user, course_id)
        course = _get_course(course_id)
        section = _get_section(course, section_id)
        lesson = _get_lesson(section, lesson_id)
        question = _get_question(lesson, question_id)

        options = [
            {"id": o.id, "text": o.text}
            for o in question.options.all()
        ]

        return Response({
            "id": question.id,
            "text": question.text,
            "question_type": question.question_type,
            "marks": question.marks,
            "options": options,
            "options_url": request.build_absolute_uri(
                f"/api/users/courses/{course_id}/sections/{section_id}"
                f"/lessons/{lesson_id}/questions/{question_id}/options/"
            ),
        })


class NestedOptionListAPIView(views.APIView):
    """
    GET /api/users/courses/<course_id>/sections/<section_id>/lessons/<lesson_id>/questions/<question_id>/options/
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(responses={200: dict, 404: dict}, operation_id='api_users_courses_sections_lessons_questions_options_list')
    def get(self, request, course_id, section_id, lesson_id, question_id):
        _get_enrollment(request.user, course_id)
        course = _get_course(course_id)
        section = _get_section(course, section_id)
        lesson = _get_lesson(section, lesson_id)
        question = _get_question(lesson, question_id)

        options = [
            {
                "id": o.id,
                "text": o.text,
                # Do not expose is_correct here; only reveal after submission
            }
            for o in question.options.all()
        ]

        return Response({
            "question_id": question.id,
            "question_text": question.text,
            "question_type": question.question_type,
            "total_options": len(options),
            "options": options,
        })


class NestedOptionDetailAPIView(views.APIView):
    """
    GET /api/users/courses/<course_id>/sections/<section_id>/lessons/<lesson_id>/questions/<question_id>/options/<option_id>/
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(responses={200: dict, 404: dict}, operation_id='api_users_courses_sections_lessons_questions_options_detail')
    def get(self, request, course_id, section_id, lesson_id, question_id, option_id):
        _get_enrollment(request.user, course_id)
        course = _get_course(course_id)
        section = _get_section(course, section_id)
        lesson = _get_lesson(section, lesson_id)
        question = _get_question(lesson, question_id)
        option = get_object_or_404(Option, pk=option_id, question=question)

        return Response({
            "id": option.id,
            "text": option.text,
            "question_id": question.id,
        })
