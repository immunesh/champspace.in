from .models import StudentProfile, InstructorProfile

def user_profile(request):
    if request.user.is_authenticated:
        try:
            profile = StudentProfile.objects.get(user=request.user)
        except StudentProfile.DoesNotExist:
            profile = None
        return {'profile': profile}
    return {}


from .models import InstructorProfile

def instructor_profile_context(request):
    if request.user.is_authenticated:
        try:
            profile = InstructorProfile.objects.get(user=request.user)
        except InstructorProfile.DoesNotExist:
            profile = None
        return {'instructor_profile': profile}
    return {}

