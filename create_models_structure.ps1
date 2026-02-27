$paths = @(
    "udemy\courses\models\category.py",
    "udemy\courses\models\course.py",
    "udemy\courses\models\organization_course.py",
    "udemy\courses\models\section.py",
    "udemy\courses\models\lesson.py",
    "udemy\courses\models\skill.py",
    "udemy\courses\models\course_skill.py",
    "udemy\courses\models\learning_path.py",
    "udemy\courses\models\learning_path_course.py",
    "udemy\courses\models\__init__.py",
    
    "udemy\courses\serializers\category_serializer.py",
    "udemy\courses\serializers\course_serializer.py",
    "udemy\courses\serializers\section_serializer.py",
    "udemy\courses\serializers\lesson_serializer.py",
    "udemy\courses\serializers\skill_serializer.py",
    "udemy\courses\serializers\learning_path_serializer.py",
    "udemy\courses\serializers\__init__.py",
    
    "udemy\courses\views\course_views.py",
    "udemy\courses\views\category_views.py",
    "udemy\courses\views\section_views.py",
    "udemy\courses\views\lesson_views.py",
    "udemy\courses\views\skill_views.py",
    "udemy\courses\views\learning_path_views.py",
    "udemy\courses\views\__init__.py",
    
    "udemy\courses\services\_keep.txt",
    "udemy\courses\selectors\_keep.txt",
    "udemy\courses\urls.py",
    "udemy\courses\admin.py",

    "udemy\enrollments\models\enrollment.py",
    "udemy\enrollments\models\lesson_progress.py",
    "udemy\enrollments\models\course_progress.py",
    "udemy\enrollments\models\certificate.py",
    "udemy\enrollments\models\course_assignment.py",
    "udemy\enrollments\models\__init__.py",
    
    "udemy\enrollments\serializers\enrollment_serializer.py",
    "udemy\enrollments\serializers\lesson_progress_serializer.py",
    "udemy\enrollments\serializers\course_progress_serializer.py",
    "udemy\enrollments\serializers\certificate_serializer.py",
    "udemy\enrollments\serializers\__init__.py",
    
    "udemy\enrollments\views\enrollment_views.py",
    "udemy\enrollments\views\progress_views.py",
    "udemy\enrollments\views\certificate_views.py",
    "udemy\enrollments\views\__init__.py",
    
    "udemy\enrollments\services\_keep.txt",
    "udemy\enrollments\selectors\_keep.txt",
    "udemy\enrollments\urls.py",
    
    "udemy\quizzes\models\quiz.py",
    "udemy\quizzes\models\question.py",
    "udemy\quizzes\models\option.py",
    "udemy\quizzes\models\quiz_attempt.py",
    "udemy\quizzes\models\__init__.py",
    
    "udemy\quizzes\serializers\quiz_serializer.py",
    "udemy\quizzes\serializers\question_serializer.py",
    "udemy\quizzes\serializers\option_serializer.py",
    "udemy\quizzes\serializers\__init__.py",
    
    "udemy\quizzes\views\quiz_views.py",
    "udemy\quizzes\views\question_views.py",
    "udemy\quizzes\views\option_views.py",
    "udemy\quizzes\views\__init__.py",
    
    "udemy\quizzes\services\_keep.txt",
    "udemy\quizzes\selectors\_keep.txt",
    "udemy\quizzes\urls.py",

    "udemy\subscriptions\models\subscription.py",
    "udemy\subscriptions\models\payment.py",
    "udemy\subscriptions\models\__init__.py",
    
    "udemy\subscriptions\serializers\subscription_serializer.py",
    "udemy\subscriptions\serializers\payment_serializer.py",
    "udemy\subscriptions\serializers\__init__.py",
    
    "udemy\subscriptions\views\subscription_views.py",
    "udemy\subscriptions\views\payment_views.py",
    "udemy\subscriptions\views\__init__.py",
    
    "udemy\subscriptions\services\_keep.txt",
    "udemy\subscriptions\selectors\_keep.txt",
    "udemy\subscriptions\urls.py",

    "udemy\notifications\models\notification.py",
    "udemy\notifications\models\user_notification.py",
    "udemy\notifications\models\__init__.py",
    
    "udemy\notifications\serializers\notification_serializer.py",
    "udemy\notifications\serializers\user_notification_serializer.py",
    "udemy\notifications\serializers\__init__.py",
    
    "udemy\notifications\views\notification_views.py",
    "udemy\notifications\views\user_notification_views.py",
    "udemy\notifications\views\__init__.py",
    
    "udemy\notifications\services\_keep.txt",
    "udemy\notifications\selectors\_keep.txt",
    "udemy\notifications\urls.py"
)

foreach ($path in $paths) {
    if ($path.EndsWith(".txt") -or $path.EndsWith(".py")) {
        $fullPath = Join-Path "d:\Udemy\udemy" $path
        $dir = Split-Path $fullPath -Parent
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Force -Path $dir | Out-Null
        }
        if (-not (Test-Path $fullPath)) {
            New-Item -ItemType File -Force -Path $fullPath | Out-Null
        }
    }
}
Write-Output "Complete structure created successfully."
