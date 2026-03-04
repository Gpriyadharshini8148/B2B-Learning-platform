from rest_framework import views, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from django.shortcuts import get_object_or_404

from admin.access.models.enrollment import Enrollment
from admin.access.models.course import Course
from admin.access.models.section import Section
from admin.access.models.lesson import Lesson
from admin.access.models.lesson_progress import LessonProgress
from admin.access.models.course_progress import CourseProgress


def _get_enrollment_or_404(user, course_id):
    """
    Return the most recent enrollment for this user + course.
    Uses .filter().first() instead of .get() to safely handle duplicate
    enrollment rows without raising MultipleObjectsReturned.
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
    """Return an absolute URL for the video file."""
    if not video:
        return None
    if video.video_file:
        return request.build_absolute_uri(video.video_file.url)
    return None


class CourseSectionsAPIView(views.APIView):
    """
    Return all sections of a course (with nested lessons).

    The user must be enrolled in the course.

    GET /api/user/courses/<course_id>/sections/
    Response:
    {
        "course_id": 1,
        "course_title": "Django REST Framework",
        "sections": [
            {
                "id": 1,
                "title": "Introduction",
                "order_number": 1,
                "lessons": [
                    {
                        "id": 1,
                        "title": "Welcome",
                        "duration_seconds": 120,
                        "order_number": 1,
                        "is_preview": true,
                        "is_completed": false
                    }
                ]
            }
        ]
    }
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, course_id):
        enrollment = _get_enrollment_or_404(request.user, course_id)
        course = enrollment.course

        sections = Section.objects.filter(
            course=course
        ).prefetch_related('lessons').order_by('order_number')

        # Collect completed lesson IDs for this enrollment
        completed_lesson_ids = set(
            LessonProgress.objects.filter(
                enrollment=enrollment,
                is_completed=True
            ).values_list('lesson_id', flat=True)
        )

        sections_data = []
        for section in sections:
            lessons_data = []
            for lesson in section.lessons.order_by('order_number'):
                lessons_data.append({
                    "id": lesson.id,
                    "title": lesson.title,
                    "duration_seconds": lesson.duration_seconds,
                    "order_number": lesson.order_number,
                    "is_preview": lesson.is_preview,
                    "is_completed": lesson.id in completed_lesson_ids,
                })
            sections_data.append({
                "id": section.id,
                "title": section.title,
                "order_number": section.order_number,
                "lessons": lessons_data,
            })

        return Response({
            "course_id": course.id,
            "course_title": course.title,
            "sections": sections_data,
        })



class CourseLessonsAPIView(views.APIView):
    """
    List all lessons for an enrolled course, or retrieve a single lesson.

    GET /api/user/courses/<course_id>/lessons/
    GET /api/user/courses/<course_id>/lessons/<lesson_id>/
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, course_id, lesson_id=None):
        enrollment = _get_enrollment_or_404(request.user, course_id)

        completed_lesson_ids = set(
            LessonProgress.objects.filter(
                enrollment=enrollment,
                is_completed=True
            ).values_list('lesson_id', flat=True)
        )

        if lesson_id:
            return self._get_lesson_detail(request, enrollment, lesson_id, completed_lesson_ids)

        return self._list_lessons(request, enrollment, completed_lesson_ids)
    
    def _get_lesson_detail(self, request, enrollment, lesson_id, completed_ids):
        lesson = get_object_or_404(
            Lesson,
            id=lesson_id,
            section__course=enrollment.course
        )

        video_data = None
        if lesson.video:
            video = lesson.video
            video_data = {
                "id": video.id,
                "title": video.title,
                "url": _video_url(request, video),
                "duration_seconds": video.duration_seconds,
            }

        # Get or create a progress record
        progress, _ = LessonProgress.objects.get_or_create(
            enrollment=enrollment,
            lesson=lesson,
            defaults={"is_completed": False, "watch_time_seconds": 0},
        )

        return Response({
            "id": lesson.id,
            "title": lesson.title,
            "duration_seconds": lesson.duration_seconds,
            "order_number": lesson.order_number,
            "is_preview": lesson.is_preview,
            "section": {
                "id": lesson.section.id,
                "title": lesson.section.title,
            },
            "video": video_data,
            "progress": {
                "is_completed": progress.is_completed,
                "watch_time_seconds": progress.watch_time_seconds,
            },
        })

    # ------------------------------------------------------------------
    # All lessons for a course (flat list)
    # ------------------------------------------------------------------
    def _list_lessons(self, request, enrollment, completed_ids):
        lessons = Lesson.objects.filter(
            section__course=enrollment.course
        ).select_related('section', 'video').order_by(
            'section__order_number', 'order_number'
        )

        data = []
        for lesson in lessons:
            data.append({
                "id": lesson.id,
                "title": lesson.title,
                "duration_seconds": lesson.duration_seconds,
                "order_number": lesson.order_number,
                "is_preview": lesson.is_preview,
                "is_completed": lesson.id in completed_ids,
                "section": {
                    "id": lesson.section.id,
                    "title": lesson.section.title,
                },
                "video_id": lesson.video_id,
            })

        return Response({
            "course_id": enrollment.course.id,
            "course_title": enrollment.course.title,
            "total_lessons": len(data),
            "lessons": data,
        })


# ---------------------------------------------------------------------------
# POST /api/user/courses/{course_id}/lessons/{lesson_id}/mark-complete/
# ---------------------------------------------------------------------------

class MarkLessonCompleteAPIView(views.APIView):
    """
    Mark a lesson as completed and update overall course progress.

    POST /api/user/courses/<course_id>/lessons/<lesson_id>/mark-complete/
    Body (optional):
    {
        "watch_time_seconds": 300
    }

    Response:
    {
        "message": "Lesson marked as complete",
        "lesson_id": 1,
        "is_completed": true,
        "watch_time_seconds": 300,
        "course_progress_percentage": "40.00"
    }
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, course_id, lesson_id):
        enrollment = _get_enrollment_or_404(request.user, course_id)

        lesson = get_object_or_404(
            Lesson,
            id=lesson_id,
            section__course=enrollment.course
        )

        watch_time = request.data.get('watch_time_seconds', 0)

        progress, _ = LessonProgress.objects.get_or_create(
            enrollment=enrollment,
            lesson=lesson,
            defaults={"is_completed": False, "watch_time_seconds": 0},
        )

        progress.is_completed = True
        if watch_time:
            progress.watch_time_seconds = watch_time
        progress.save()

        # Recalculate course progress percentage
        total_lessons = Lesson.objects.filter(
            section__course=enrollment.course
        ).count()

        completed_count = LessonProgress.objects.filter(
            enrollment=enrollment,
            is_completed=True
        ).count()

        course_pct = (completed_count / total_lessons * 100) if total_lessons else 0

        course_progress, _ = CourseProgress.objects.get_or_create(enrollment=enrollment)
        course_progress.progress_percentage = round(course_pct, 2)

        # Auto-complete course if all lessons done
        if completed_count == total_lessons and total_lessons > 0:
            from django.utils import timezone
            course_progress.completed_at = timezone.now()
            enrollment.status = 'completed'
            enrollment.save()

        course_progress.save()

        return Response({
            "message": "Lesson marked as complete",
            "lesson_id": lesson.id,
            "lesson_title": lesson.title,
            "is_completed": True,
            "watch_time_seconds": progress.watch_time_seconds,
            "course_progress_percentage": str(course_progress.progress_percentage),
        }, status=status.HTTP_200_OK)


class LessonVideoAPIView(views.APIView):
    """
    Return the video streaming URL for a specific lesson.

    The user must be enrolled in the course.
    Preview lessons (is_preview=True) are accessible without enrollment.

    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, course_id, lesson_id):
        # Allow preview lessons without enrollment check
        lesson = get_object_or_404(
            Lesson,
            id=lesson_id,
            section__course_id=course_id
        )

        if not lesson.is_preview:
            # Enforce enrollment for non-preview lessons
            _get_enrollment_or_404(request.user, course_id)

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


# ---------------------------------------------------------------------------
# PATCH /api/user/courses/{course_id}/lessons/{lesson_id}/watch-time/
# ---------------------------------------------------------------------------

class UpdateWatchTimeAPIView(views.APIView):
    """
    Update the watch time for a lesson (without marking it complete).
    Useful for periodic progress saves while the video is playing.

    PATCH /api/user/courses/<course_id>/lessons/<lesson_id>/watch-time/
    Body:
    {
        "watch_time_seconds": 150
    }

    Response:
    {
        "lesson_id": 1,
        "watch_time_seconds": 150,
        "is_completed": false
    }
    """
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, course_id, lesson_id):
        enrollment = _get_enrollment_or_404(request.user, course_id)

        lesson = get_object_or_404(
            Lesson,
            id=lesson_id,
            section__course=enrollment.course
        )

        watch_time = request.data.get('watch_time_seconds')
        if watch_time is None:
            return Response(
                {"error": "watch_time_seconds is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        progress, _ = LessonProgress.objects.get_or_create(
            enrollment=enrollment,
            lesson=lesson,
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
