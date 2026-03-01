from rest_framework import views, status, permissions
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from admin.courses.models.course import Course
from admin.courses.models.category import Category
from admin.enrollments.models.enrollment import Enrollment

from admin.access.models.user import User as CustomUser
from admin.access.models.user_role import UserRole

class UserDashboardView(views.APIView):
    """
    Returns data for the user dashboard including user details, 
    their organization, categories, recommended courses, and enrolled courses.
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(responses={200: dict})
    def get(self, request):
        user = request.user

        # Provide a fallback if user is coming from Swagger/Session auth (standard Django user)
        if not isinstance(user, CustomUser):
            try:
                user = CustomUser.objects.get(email=user.email)
            except CustomUser.DoesNotExist:
                return Response({"error": "User profile not found in custom User registry."}, status=status.HTTP_404_NOT_FOUND)
        
        # Enrolled Courses
        enrollments = Enrollment.objects.filter(user=user, is_active=True).select_related('course')
        enrolled_courses = []
        enrolled_course_ids = []
        
        for env in enrollments:
            enrolled_course_ids.append(env.course.id)
            
            status_mapped = "in_progress" if env.status == "active" else env.status
            progress_pct = 0
            if hasattr(env, 'progress') and env.progress:
                progress_pct = env.progress.progress_percentage
                
            enrolled_courses.append({
                "id": env.course.id,
                "title": env.course.title,
                "progress": progress_pct,
                "status": status_mapped,
                "thumbnail_url": env.course.thumbnail_url
            })

        # Determine actual role properly from the database or logic
        from django.conf import settings
        super_admin_email = getattr(settings, 'EMAIL_HOST_USER', 'gpriyadharshini9965@gmail.com')

        role = "user"  # Default fallback
        if user.is_superuser or user.email == super_admin_email:
            role = "super_admin"
        else:
            user_role = UserRole.objects.filter(user=user).select_related('role').first()
            if user_role and user_role.role:
                role = user_role.role.name.lower()
            elif len(enrolled_courses) > 0:
                role = "learner"  # Upgrade to learner automatically if they have enrollments

        user_name = f"{user.first_name} {user.last_name}".strip()
        if not user_name:
            user_name = user.email.split('@')[0]
            
        user_data = {
            "id": user.id,
            "name": user_name,
            "email": user.email,
            "role": role,
            "organization": user.organization.name if user.organization else None
        }

        # Organization Details
        org_data = None
        if user.organization:
            org_data = {
                "id": user.organization.id,
                "name": user.organization.name
            }

        response_payload = {
            "user": user_data,
        }
        
        if role not in ["user", "learner"]:
            response_payload["organization"] = org_data

        if role == "super_admin":
            from admin.organizations.models.organization import Organization
            
            # exclude the super admin from user queries
            admin_qs = CustomUser.objects.exclude(email=super_admin_email).exclude(is_superuser=True)
            
            # For learners, we can check how many users have the learner role or have matching criteria
            # But roughly, developers might map learners. For now, we'll try to calculate learners by total generic users minus admins
            # Let's count users with enrollments as learners for simplicity
            learners_count = admin_qs.filter(enrollments__isnull=False).distinct().count()

            response_payload["stats"] = {
                "organizations": Organization.objects.count(),
                "users": admin_qs.count(),
                "learners": learners_count
            }

            recent_orgs = []
            all_orgs = []
            for org in Organization.objects.order_by('-created_at'):
                org_data = {
                    "id": org.id,
                    "name": org.name,
                    "subdomain": org.subdomain,
                    "status": org.approval_status
                }
                all_orgs.append(org_data)
                if len(recent_orgs) < 5:
                    recent_orgs.append(org_data)
                    
            response_payload["all_organizations"] = all_orgs
            response_payload["recent_organizations"] = recent_orgs

            all_users = []
            for u in admin_qs.order_by('-created_at'):
                all_users.append({
                    "id": u.id,
                    "email": u.email,
                    "name": f"{u.first_name} {u.last_name}".strip() or u.email.split('@')[0],
                    "status": u.approval_status,
                    "organization": u.organization.name if u.organization else None
                })
            response_payload["all_users"] = all_users

            pending_items = []
            # Pending Orgs
            for org in Organization.objects.filter(approval_status='pending'):
                pending_items.append({
                    "id": org.id,
                    "type": "organization",
                    "name": org.name,
                    "status": "pending"
                })
            # Pending Users
            for u in admin_qs.filter(approval_status='pending'):
                pending_items.append({
                    "id": u.id,
                    "type": "user",
                    "email": u.email,
                    "name": f"{u.first_name} {u.last_name}".strip() or u.email.split('@')[0],
                    "status": "pending"
                })
            response_payload["pending_approvals"] = pending_items

            # Management URLs
            response_payload["manage_users_url"] = request.build_absolute_uri('/api/access/users/')
            response_payload["manage_organizations_url"] = request.build_absolute_uri('/api/super_admin/manage_organizations/')
        
        elif role in ["organization_admin", "admin", "org_admin", "user"] and user.organization:
            org = user.organization
            org_users = CustomUser.objects.filter(organization=org)
            
            total_users = org_users.count()
            total_learners = org_users.filter(enrollments__isnull=False).distinct().count()
            
            total_admins_count = UserRole.objects.filter(
                user__organization=org, 
                role__name__in=['admin', 'org_admin', 'organization_admin']
            ).count()
            total_admins = total_admins_count if total_admins_count > 0 else 1
            
            org_courses = Course.objects.filter(instructor__organization=org)
            total_courses = org_courses.count()
            active_courses = org_courses.filter(is_active=True).count()
            
            recent_users_list = []
            for u in org_users.order_by('-created_at')[:5]:
                recent_users_list.append({
                    "id": u.id,
                    "name": f"{u.first_name} {u.last_name}".strip() or u.email.split('@')[0],
                    "email": u.email,
                    "status": "active" if u.is_active else u.approval_status
                })
                
            recent_courses_list = []
            for c in org_courses.order_by('-created_at')[:5]:
                recent_courses_list.append({
                    "id": c.id,
                    "title": c.title,
                    "status": "active" if c.is_active else "inactive"
                })

            response_payload = {
                "user": user_data,
                "organization": {
                    "id": org.id,
                    "name": org.name,
                    "subdomain": org.subdomain,
                    "email": user.email  # Fallback to user email if organization has no distinct email field
                },
                "stats": {
                    "total_users": total_users,
                    "total_learners": total_learners,
                    "total_admins": total_admins,
                    "total_courses": total_courses,
                    "active_courses": active_courses
                },
                "recent_users": recent_users_list,
                "recent_courses": recent_courses_list
            }
        
        else:
            # Regular learner data
            enrolled_count = len(enrolled_courses)
            completed_count = sum(1 for c in enrolled_courses if c["status"] == "completed")
            in_progress_count = sum(1 for c in enrolled_courses if c["status"] in ["in_progress", "active"])
            
            response_payload["stats"] = {
                "enrolled_courses": enrolled_count,
                "completed_courses": completed_count,
                "in_progress_courses": in_progress_count
            }
            
            response_payload["enrolled_courses"] = enrolled_courses
            
            # Fetch recent activity (lessons)
            try:
                from admin.enrollments.models.lesson_progress import LessonProgress
                recent_lessons = LessonProgress.objects.filter(
                    enrollment__user=user
                ).select_related('lesson', 'enrollment__course').order_by('-updated_at')[:5]
            except Exception:
                recent_lessons = []

            recent_activities = []
            for rp in recent_lessons:
                date_val = getattr(rp, 'updated_at', getattr(rp, 'created_at', None))
                recent_activities.append({
                    "course": rp.enrollment.course.title,
                    "lesson": rp.lesson.title,
                    "date": date_val.strftime("%Y-%m-%d") if date_val else "2026-02-27"
                })
            
            response_payload["recent_activity"] = recent_activities

        return Response(response_payload, status=status.HTTP_200_OK)
