from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from django.conf import settings
from admin.access.models import Quiz, Question, Option
from admin.organizations.serializers import QuizSerializer, QuestionSerializer, OptionSerializer
from admin.access.permissions.tenant_permissions import TenantSafeViewSetMixin, IsOrgAdminOrReadOnly

class BaseAssessmentViewSet(TenantSafeViewSetMixin, viewsets.ModelViewSet):
    permission_classes = [IsOrgAdminOrReadOnly]

class OrgQuizViewSet(BaseAssessmentViewSet):
    serializer_class = QuizSerializer

    def get_queryset(self):
        user = self.request.user
        super_admin_email = getattr(settings, 'EMAIL_HOST_USER', 'gpriyadharshini9965@gmail.com')
        
        if user.is_superuser or getattr(user, 'email', '') == super_admin_email:
            queryset = Quiz.objects.all()
        else:
            queryset = Quiz.objects.filter(organization=user.organization)

        lesson_pk = self.kwargs.get('lesson_pk')
        course_pk = self.kwargs.get('course_pk')
        if lesson_pk:
            queryset = queryset.filter(lesson_id=lesson_pk)
        if course_pk:
            queryset = queryset.filter(course_id=course_pk)
        return queryset

    def perform_create(self, serializer):
        lesson_pk = self.kwargs.get('lesson_pk')
        course_pk = self.kwargs.get('course_pk')
        
        # Rule: One quiz for one lesson
        if lesson_pk and Quiz.objects.filter(lesson_id=lesson_pk).exists():
            raise ValidationError("A quiz already exists for this lesson. Only one quiz per lesson is allowed.")

        serializer.save(
            organization=self.request.user.organization,
            lesson_id=lesson_pk,
            course_id=course_pk
        )

class OrgQuestionViewSet(BaseAssessmentViewSet):
    serializer_class = QuestionSerializer

    def get_queryset(self):
        user = self.request.user
        super_admin_email = getattr(settings, 'EMAIL_HOST_USER', 'gpriyadharshini9965@gmail.com')
        
        if user.is_superuser or getattr(user, 'email', '') == super_admin_email:
            queryset = Question.objects.all()
        else:
            queryset = Question.objects.filter(organization=user.organization)

        quiz_pk = self.kwargs.get('quiz_pk')
        if quiz_pk:
             return queryset.filter(quiz_id=quiz_pk)
        return queryset

    def perform_create(self, serializer):
        quiz_pk = self.kwargs.get('quiz_pk')
        serializer.save(
            organization=self.request.user.organization,
            quiz_id=quiz_pk
        )
        
class OrgOptionViewSet(BaseAssessmentViewSet):
    serializer_class = OptionSerializer

    def get_queryset(self):
        user = self.request.user
        super_admin_email = getattr(settings, 'EMAIL_HOST_USER', 'gpriyadharshini9965@gmail.com')
        
        if user.is_superuser or getattr(user, 'email', '') == super_admin_email:
            queryset = Option.objects.all()
        else:
            queryset = Option.objects.filter(organization=user.organization)

        question_pk = self.kwargs.get('question_pk')
        if question_pk:
             return queryset.filter(question_id=question_pk)
        return queryset

    def perform_create(self, serializer):
        question_pk = self.kwargs.get('question_pk')
        is_correct = serializer.validated_data.get('is_correct', False)

        # Rule: Maximum 4 options restricted
        if Option.objects.filter(question_id=question_pk).count() >= 4:
            raise ValidationError("Maximum 4 options allowed per question.")

        # Rule: Only one correct option
        if is_correct and Option.objects.filter(question_id=question_pk, is_correct=True).exists():
            raise ValidationError("A correct option already exists for this question. Only one option can be marked as correct.")

        serializer.save(
            organization=self.request.user.organization,
            question_id=question_pk
        )

    def perform_update(self, serializer):
        instance = self.get_object()
        is_correct = serializer.validated_data.get('is_correct')
        
        # Rule: Only one correct option (check during update)
        if is_correct is True:
             other_correct = Option.objects.filter(
                 question=instance.question, 
                 is_correct=True
             ).exclude(id=instance.id).exists()
             if other_correct:
                 raise ValidationError("Another option is already marked as correct for this question.")
        
        serializer.save()
