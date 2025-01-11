from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import ObjectDoesNotExist
from .models import UserProfile
from django.http import HttpResponse
from .models import Course  # For instance, if you need to handle Course data
from .forms import StudentEditProfileForm  # Create this form in forms.py
from .models import StudentProfile, UserCourse
from champapp.models import Profile, UserCourse
from .models import CourseCategory
import razorpay
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from .models import Course1, Payment
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET_KEY))

def create_payment(request, course_id):
    course = get_object_or_404(Course1, id=course_id)
    amount = int(course.price * 100)  # Convert to paise

    # Create Razorpay order
    razorpay_order = razorpay_client.order.create({
        'amount': amount,
        'currency': 'INR',
        'payment_capture': '1'
    })

    # Save payment details in the database
    payment = Payment.objects.create(
        user=request.user,
        course=course,
        amount=course.price,
        razorpay_order_id=razorpay_order['id'],
        status="Pending"
    )

    context = {
        'course': course,
        'razorpay_order_id': razorpay_order['id'],
        'razorpay_key': settings.RAZORPAY_KEY_ID,
        'amount': amount,
        'user_email': request.user.email,
        'user_name': request.user.username
    }
    return render(request, 'payments/payment_page.html', context)

@csrf_exempt
def verify_payment(request):
    if request.method == "POST":
        data = request.POST
        razorpay_order_id = data.get('razorpay_order_id')
        razorpay_payment_id = data.get('razorpay_payment_id')
        razorpay_signature = data.get('razorpay_signature')

        # Verify signature
        try:
            razorpay_client.utility.verify_payment_signature({
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            })

            # Update payment status
            payment = Payment.objects.get(razorpay_order_id=razorpay_order_id)
            payment.razorpay_payment_id = razorpay_payment_id
            payment.razorpay_signature = razorpay_signature
            payment.status = "Success"
            payment.save()

            # Enroll the user in the course or any other success action
            return JsonResponse({'status': 'success'})

        except razorpay.errors.SignatureVerificationError:
            return JsonResponse({'status': 'failed', 'message': 'Signature verification failed.'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

def home(request):
    # Fetch all courses and organize them by category
    courses = Course1.objects.filter(status='Live').select_related('creator').prefetch_related('lectures')

    # Get unique categories
    categories = Course1.objects.filter(status='Live').values_list('category', flat=True).distinct()

    # Calculate average rating and other metrics
    for course in courses:
        # You can add rating calculation logic here
        course.avg_rating = 4.0  # Placeholder - replace with actual rating calculation
        
        # Get total lectures count
        course.total_lectures = course.lectures.count()
        
        

    context = {
        'courses': courses,
        'categories': categories,
        'trending_courses': courses[:6]
    }
    
    return render(request, 'champapp/index.html', context)



def sign_up(request):
    """Handle user signup."""
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        terms_accepted = request.POST.get('terms')

        # Validation
        if not terms_accepted:
            messages.error(request, 'You must agree to the terms and conditions.')
        elif password != confirm_password:
            messages.error(request, 'Passwords do not match.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
        else:
            # Create a new user
            user = User.objects.create_user(username=email, email=email, password=password)
            # Ensure profile is created
            profile, created = StudentProfile.objects.get_or_create(user=user)
            if created:
                profile.username = email  # Set the username in the profile if not created yet
                profile.save()
            
            # UserProfile will be created automatically via the signal
            login(request, user)  # Log the user in automatically after sign-up            
            messages.success(request, 'Account created successfully! You are now logged in.')
            return redirect('student-dashboard')  # Redirect to student dashboard
    
    return render(request, 'champapp/sign_up.html')





@login_required
def user_logout(request):
    """Logs out the user and redirects to the sign-in page."""
    logout(request)  # Logs out the user
    messages.success(request, "You have been logged out successfully!")  # Optional success message
    return redirect('champapp/sign_up.html')  # Redirect to the sign-in page (update the URL name as needed)


########## login_redirect #################
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .models import UserProfile

def role_based_redirect(user):
    """Determine redirection based on user role."""
    if user.is_superuser or user.is_staff:
        return 'instructor_dashboard'  # URL name for instructor dashboard
    elif hasattr(user, 'is_student') and user.is_student:
        return 'student-dashboard'  # URL name for student dashboard
    else:
        return 'student-dashboard'  # Default URL name



def sign_in(request):
    """Handle user sign-in."""
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')

        # Authenticate user
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            
            # Explicitly check and create profile if it does not exist
            if not hasattr(user, 'profile'):
                UserProfile.objects.get_or_create(user=user)

            if not remember_me:
                request.session.set_expiry(0)  # Session expires on browser close

            # Redirect to the user dashboard after login
            return redirect(role_based_redirect(user))  # Assuming 'user-dashboard' is the name of the dashboard URL

        else:
            messages.error(request, 'Invalid email or password.')
    return render(request, 'champapp/sign_in.html')


def forgot_password(request):
    """Handle password reset logic."""
    if request.method == 'POST':
        email = request.POST.get('email')
        # Simulate password reset logic (e.g., sending an email)
        if email:
            # Add logic to check if the email exists in the database and send reset instructions.
            messages.success(request, "If this email exists, a password reset link has been sent.")
        else:
            messages.error(request, "Please enter a valid email address.")
    
    return render(request, 'champapp/forgot_password.html')


# Custom 403 error view
def custom_403_view(request, *args, **kwargs):
    return render(request, 'champapp/403.html', status=403)


# Check if the user is a superuser
@user_passes_test(lambda u: u.is_superuser or u.is_staff, login_url='/403/')
def admin_dashboard(request):
    return render(request, 'champapp/admin/admin-dashboard.html')




############### Student dashboard #####################################################
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Course1
from django.urls import reverse
from .models import UserTopicProgress


@login_required
def user_dashboard(request):
    user = request.user
    
    # Try to get the user's profile
    try:
        user_profile = StudentProfile.objects.get(user=user)
    except ObjectDoesNotExist:
        # If the profile does not exist, create one with default values
        user_profile = StudentProfile.objects.create(user=user)

    context = {
        "profile": user_profile,  # Make sure 'profile' is passed to the template
    }

    # Fetch courses associated with the user
    user_courses = UserCourse.objects.filter(user=user)
    
# Fetch courses the user is enrolled in
    enrolled_courses = EnrolledCourse.objects.filter(student=user).select_related('course')


    # Prepare course progression data
    courses_with_progress = []
    for enrollment in enrolled_courses:
        course = enrollment.course
        total_lectures = course.lectures.count()
        total_topics = 0
        completed_topics = 0

        # Calculate total topics and completed topics
        for lecture in course.lectures.all():
            total_topics += lecture.topics.count()
            completed_topics += UserTopicProgress.objects.filter(
                user=user,
                topic__in=lecture.topics.all(),
                completed=True
            ).count()

        # Calculate progression
        progression_percentage = (completed_topics / total_topics) * 100 if total_topics > 0 else 0

        courses_with_progress.append({
            'course': course,
            'progression': round(progression_percentage, 2),
            'total_lectures': total_lectures,
            'total_topics': total_topics,
            'completed_topics': completed_topics,
        })


    # If no courses are enrolled, set default values
    if not enrolled_courses.exists():
        completed_lessons = 0
        achieved_certificates = 0
        points = 0
    else:
        completed_lessons = sum(course.completed_lectures for course in enrolled_courses)
        achieved_certificates = user_profile.achieved_certificates
        points = user_profile.points    
        enrolled_courses = EnrolledCourse.objects.filter(
        student=request.user
    ).select_related('course')

    context = {
        "user": user,
        "profile": user_profile,
        "courses": user_courses,
        "total_courses": enrolled_courses.count(),
        "completed_lessons": completed_lessons,
        "achieved_certificates": achieved_certificates,
        "points": points,
        "enrolled_courses": enrolled_courses,  # Add enrolled courses to context
        "courses_with_progress": courses_with_progress,  # List of courses with progress data

    }
    return render(request, "champapp/student_dashboard/student-dashboard.html", context)

################ student edit profile ###############################################################################
@login_required
def edit_profile(request):
    user = request.user
    
    # Use get_or_create to handle missing profiles
    student_profile, created = StudentProfile.objects.get_or_create(
    user=user)

    # Fetch courses associated with the user (if needed for other purposes)
    user_courses = UserCourse.objects.filter(user=user)

    # Count total courses for context
    total_courses = user_courses.count()

    if request.method == 'POST':
        # Bind the submitted form data
        form = StudentEditProfileForm(request.POST, request.FILES, instance=student_profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('edit_profile')  # Prevents form re-submission
        else:
            # Log form errors for debugging during development
            print("Form errors:", form.errors)
            messages.error(request, "Please correct the errors below.")
    else:
        # Display the form pre-filled with the student's profile data
        form = StudentEditProfileForm(instance=student_profile)

    # Combine form and relevant context
    context = {
        "user": user,
        "profile": student_profile,
        "courses": user_courses,
        "total_courses": total_courses,  # Just show the total courses count
        "profile_image": student_profile.profile_image.url if student_profile.profile_image else None,
        "form": form,  # Add the form to the context
    }

    return render(request, 'champapp/student_dashboard/student-edit-profile.html', context)

############### instructor edit profile ###########################################################################
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import InstructorProfile, Course
from .forms import InstructorProfileForm
import logging
from django.contrib.auth.decorators import login_required




# Get the logger for debugging
logger = logging.getLogger(__name__)

@login_required
def edit_instructor_profile(request):
    user = request.user
    instructor_profile, created = InstructorProfile.objects.get_or_create(user=user)

    if created:
        messages.info(request, "A new profile has been created for you.")

    # Fetch courses created by the instructor (if needed)
    created_courses = Course.objects.filter(instructor=user)

    if request.method == 'POST':
        form = InstructorProfileForm(request.POST, request.FILES, instance=instructor_profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('edit_instructor_profile')
        else:
            logger.warning("Form validation failed. Errors: %s", form.errors)
            messages.error(request, "Please correct the errors below.")
    else:
        form = InstructorProfileForm(instance=instructor_profile)

    context = {
        "user": user,
        "profile": instructor_profile,
        "courses": created_courses,
        "form": form,
    }

    return render(request, 'champapp/instructor/instructor-edit-profile.html', context)






def admin_course_category(request):
    # Fetch all course categories to display in the template
    categories = CourseCategory.objects.all()

    return render(request, 'champapp/admin/admin-course-category.html', {'categories': categories})


########################testtttttttttttttttttt##################
from django.shortcuts import render, redirect, get_object_or_404
from .forms import InstructorClassCourseForm
from .models import InstructorClassCourse
from django.contrib.auth.decorators import user_passes_test
import logging

logger = logging.getLogger(__name__)  # Configure logging

# Decorator to check if the user is a superuser or staff
def superuser_or_staff_required(user):
    return user.is_active and (user.is_superuser or user.is_staff)

@user_passes_test(superuser_or_staff_required)
def instructor_create_class_course(request):
    if request.method == 'POST':
        form = InstructorClassCourseForm(request.POST, request.FILES)
        
        if form.is_valid():
            logger.info("Form is valid! Saving the course.")
            class_course = form.save()
            logger.info(f"Course saved with ID: {class_course.id}")
            return redirect('course_detail_adv', pk=class_course.id)  # Redirect after successful save
        else:
            logger.error(f"Form is invalid. Errors: {form.errors}")
    else:
        form = InstructorClassCourseForm()

    return render(request, 'champapp/create_class_course.html', {'form': form})


############admin-course-list############
from django.core.paginator import Paginator
from django.shortcuts import render
from .models import Course1

def all_courses(request):
    # Fetch all courses with their creators
    courses = Course1.objects.select_related('creator')
    
    # Get the counts for each category
    live_courses_count = Course1.objects.filter(status=Course1.LIVE).count()
    pending_courses_count = Course1.objects.filter(status=Course1.PENDING).count()
    rejected_courses_count = Course1.objects.filter(status=Course1.REJECTED).count()

    # Filter courses based on query parameters
    creator_id = request.GET.get('creator_id')
    status = request.GET.get('status')

    if creator_id:
        courses = courses.filter(creator_id=creator_id)
    if status:
        courses = courses.filter(status=status)

    # Pagination logic: Show 10 courses per page
    paginator = Paginator(courses, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'champapp/admin/admin-course-list.html', {
        'courses': page_obj,
        'live_courses_count': live_courses_count,
        'pending_courses_count': pending_courses_count,
        'rejected_courses_count': rejected_courses_count,
    })


#############class_course_preview###########
from django.shortcuts import render
from .models import Course1  # Import your Course1 model

def class_course_preview(request):
    courses = Course1.objects.all()  # Fetch all courses
    total_courses = courses.count()  # Get the total count
    # Check if the user has a profile before accessing it
    profile = None
    if request.user.is_authenticated:
        try:
            profile = request.user.profile  # Fetch the profile of the logged-in user
        except AttributeError:
            pass  # Handle the case where the user doesn't have a profile (e.g., if it hasn't been created)
    
    return render(request, 'champapp/preview_class_course.html', {
        'courses': courses,
        'total_courses': total_courses,
        'profile': profile,  # Pass the profile to the template (may be None if no profile)
    })

########## Course-detail-adv#################
def course_detail_adv(request, pk):
    class_course = get_object_or_404(InstructorClassCourse, pk=pk)
    return render(request, 'champapp/admin/course-detail-adv.html', {'class_course': class_course})


########## instructor dashboard #################
from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from .models import Course1, StudentProfile, EnrolledCourse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Sum
from django.utils.timesince import timesince
from django.db.models import Count, F


# Check if user is superuser or staff
def superuser_or_staff_required(user):
    return user.is_superuser or user.is_staff

@user_passes_test(superuser_or_staff_required, login_url='/403/')
def instructor_dashboard(request):
    """View for the instructor dashboard."""
    user = request.user

    # Initialize variables
    instructor_courses = Course1.objects.none()  # Default to an empty queryset
    total_students = 0
    enrolled_students_count = 0
    current_month_earnings = 0
    last_month_earnings = 0
    instructor_courses_count = 0
    most_selling_courses = []

    # Count the number of students (users who are not staff)
    total_students = User.objects.filter(is_staff=False).count()

    # Query the courses created by the logged-in instructor
    if user.is_authenticated:
        instructor_courses = Course1.objects.filter(creator=user)  # Only get courses created by the instructor
        instructor_courses_count = instructor_courses.count()  # Count the courses

        # Count the total number of students enrolled in the instructor's courses
        enrolled_students_count = EnrolledCourse.objects.filter(course__in=instructor_courses).count()

        # Calculate earnings for the current month
        current_month_start = timezone.now().replace(day=1)
        current_month_courses = instructor_courses.filter(created_at__gte=current_month_start)
        current_month_earnings = current_month_courses.aggregate(total_earnings=Sum('price'))['total_earnings'] or 0

        # Calculate earnings for the last month
        last_month_start = (timezone.now().replace(day=1) - timedelta(days=1)).replace(day=1)
        last_month_end = current_month_start - timedelta(days=1)
        last_month_courses = instructor_courses.filter(created_at__gte=last_month_start, created_at__lte=last_month_end)
        last_month_earnings = last_month_courses.aggregate(total_earnings=Sum('price'))['total_earnings'] or 0

        # Get data for "Most Selling Courses"
        most_selling_courses = (
            instructor_courses.annotate(
                total_enrollments=Count('enrolledcourse', distinct=True),  # Count distinct enrollments
                total_revenue=F('price') * Count('enrolledcourse', distinct=True),  # Calculate revenue
            )
            .order_by('-total_enrollments')
        )

        # Prepare course data for the template
        course_data = []
        for course in most_selling_courses:
            for enrollment in EnrolledCourse.objects.filter(course=course):
                # Calculate progress for each enrollment
                if course.total_lecture > 0:
                    progress = (enrollment.completed_lectures / course.total_lecture) * 100
                else:
                    progress = 0  # Prevent division by zero
                
                course_data.append({
                    "course_name": course.name,
                    "progress": progress,
                    "course_id": course.id,
                    "enrollment": enrollment,
                    "name": course.name,
                    "image": course.image.url if course.image else None,
                    "total_enrollments": course.total_enrollments or 0,
                    "total_revenue": course.total_revenue or 0,
                    "duration": timesince(course.created_at) if course.created_at else "N/A",

                })

    # Try to get the user's profile (assuming it's a StudentProfile)
    try:
        user_profile = StudentProfile.objects.get(user=user)
    except ObjectDoesNotExist:
        # If the profile does not exist, create one with default values
        user_profile = StudentProfile.objects.create(user=user)

    # Context for the template
    context = {
        "instructor_courses_count": instructor_courses_count,  # Pass the count to the template
        "user": user,
        "profile": user_profile,  # Pass the user's profile to the template
        "total_students": total_students,  # Pass the total students count to the template
        "enrolled_students_count": enrolled_students_count,  # Pass the count of enrolled students to the template
        "current_month_earnings": current_month_earnings,  # Pass the current month's earnings
        "last_month_earnings": last_month_earnings,  # Pass the last month's earnings
        "most_selling_courses": course_data,  # Pass the course data to the template
    }

    return render(request, 'champapp/instructor/instructor-dashboard.html', context)



#########################---------admin-student-list-----------###############################################
from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from .models import StudentProfile  # Import your StudentProfile model if applicable
from django.contrib.auth.models import User  # Import the User model if needed

# Decorator to check if the user is a superuser
def superuser_required(view_func):
    return user_passes_test(lambda u: u.is_superuser)(view_func)

@superuser_required
def admin_student_list(request):
    # Fetch only non-staff users (students)
    students = User.objects.filter(is_staff=False)  # This filters out staff (instructors)
    
    # If you are using StudentProfile, you can also join it like this:
    # students = StudentProfile.objects.filter(user__is_staff=False)

    context = {'students': students}
    return render(request, 'champapp/admin/admin-student-list.html', context)


from django.core.paginator import Paginator

def admin_student_list(request):
    students_list = StudentProfile.objects.all()
    paginator = Paginator(students_list, 6)  # 6 students per page
    page_number = request.GET.get('page')
    students = paginator.get_page(page_number)
    context = {'students': students}
    return render(request, 'champapp/admin/admin-student-list.html', context)


###########course1############

from django.shortcuts import render, redirect
from .models import Course1, Lecture, Topic, FAQ
from .forms import CourseForm, MediaForm, LectureForm, TopicForm, FAQForm
import logging

logger = logging.getLogger(__name__)  # Configure logging

# Decorator to check if the user is a superuser or staff
def superuser_or_staff_required(user):
    return user.is_active and (user.is_superuser or user.is_staff)

@user_passes_test(superuser_or_staff_required)
def create_course_step1(request, course_id=None):
    # Fetch the course if course_id is provided, otherwise it's a new course
    course = Course1.objects.get(id=course_id) if course_id else None
    
    # Create a form instance, passing in the course if editing an existing one
    form = CourseForm(instance=course)
    
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            # Don't save the form yet, assign the logged-in user as the creator
            course = form.save(commit=False)
            course.creator = request.user  # Set the creator as the logged-in user
            course.save()  # Save the course with the assigned creator

            # Log the course creation
            logger.info(f'Course "{course.name}" created by {request.user.email}')
            
            return redirect('step_2', course_id=course.id)  # Redirect to the next step

    # Render the template with the course form
    return render(request, 'champapp/step1.html', {'form': form, 'course': course})

@user_passes_test(superuser_or_staff_required)
def create_course_step2(request, course_id):
    course = Course1.objects.get(id=course_id)
    form = MediaForm()
    if request.method == 'POST':
        form = MediaForm(request.POST, request.FILES)
        if form.is_valid():
            # Handle image upload
            if 'image' in form.cleaned_data:
                course.image = form.cleaned_data['image']
            # Handle video URL
            if 'video_url' in form.cleaned_data:
                course.video_url = form.cleaned_data['video_url']
            # Handle video file upload
            if 'video_upload' in form.cleaned_data:
                course.video_upload = form.cleaned_data['video_upload']
            
            # Save the course
            course.save()
            return redirect('step_3', course_id=course.id)
    return render(request, 'champapp/step2.html', {'form': form, 'course': course})
@user_passes_test(superuser_or_staff_required)
def create_course_step3(request, course_id):
    course = Course1.objects.get(id=course_id)
    lecture_form = LectureForm()
    topic_form = TopicForm()
    if request.method == 'POST':
        if 'add_lecture' in request.POST:
            lecture_form = LectureForm(request.POST)
            if lecture_form.is_valid():
                lecture = lecture_form.save(commit=False)
                lecture.course = course
                lecture.save()
                return redirect('step_3', course_id=course.id)
        # Edit Lecture
        elif 'edit_lecture' in request.POST:
            lecture_id = request.POST.get('lecture_id')
            lecture = Lecture.objects.get(id=lecture_id)
            lecture_form = LectureForm(request.POST, instance=lecture)
            if lecture_form.is_valid():
                lecture_form.save()
                return redirect('step_3', course_id=course.id)
        # Delete Lecture
        elif 'delete_lecture' in request.POST:
            lecture_id = request.POST.get('lecture_id')
            Lecture.objects.filter(id=lecture_id).delete()
            return redirect('step_3', course_id=course.id)
        
        elif 'add_topic' in request.POST:
            topic_form = TopicForm(request.POST)
            if topic_form.is_valid():
                topic = topic_form.save(commit=False)
                topic.lecture_id = request.POST['lecture_id']
                topic.save()
                return redirect('step_3', course_id=course.id)
        # Edit Topic
        elif 'edit_topic' in request.POST:
            topic_id = request.POST.get('topic_id')
            topic = Topic.objects.get(id=topic_id)
            topic_form = TopicForm(request.POST, instance=topic)
            if topic_form.is_valid():
                topic_form.save()
                return redirect('step_3', course_id=course.id)
        # Delete Topic
        elif 'delete_topic' in request.POST:
            topic_id = request.POST.get('topic_id')
            Topic.objects.filter(id=topic_id).delete()
            return redirect('step_3', course_id=course.id)


    return render(request, 'champapp/step3.html', {
        'course': course, 
        'lecture_form': lecture_form, 
        'topic_form': topic_form,
        'lectures': course.lectures.all()
    })
@user_passes_test(superuser_or_staff_required)
def create_course_step4(request, course_id):
    course = Course1.objects.get(id=course_id)
    faq_form = FAQForm()
    if request.method == 'POST':
        if 'add_faq' in request.POST:
            faq_form = FAQForm(request.POST)
            if faq_form.is_valid():
                faq = faq_form.save(commit=False)
                faq.course = course
                faq.save()
                return redirect('step_4', course_id=course.id)
        # Edit FAQ
        elif 'edit_faq' in request.POST:
            faq_id = request.POST.get('faq_id')
            faq = FAQ.objects.get(id=faq_id)
            faq_form = FAQForm(request.POST, instance=faq)
            if faq_form.is_valid():
                faq_form.save()
                return redirect('step_4', course_id=course.id)
        # Delete FAQ
        elif 'delete_faq' in request.POST:
            faq_id = request.POST.get('faq_id')
            FAQ.objects.filter(id=faq_id).delete()
            return redirect('step_4', course_id=course.id)
        
        elif 'submit_course' in request.POST:
            course.tags = request.POST['tags']
            course.message_to_reviewer = request.POST['message_to_reviewer']
            course.save()
            return redirect('course_detail_adv', pk=course.id)


    return render(request, 'champapp/step4.html', {
        'course': course, 
        'faq_form': faq_form,
    })


from .models import Profile  # Adjust the import to match your Profile model

def course_detail_adv(request, pk):
    class_course = get_object_or_404(Course1, pk=pk)
    profile, created = Profile.objects.get_or_create(user=request.user)  # Assuming one-to-one relation with the User model
    course = get_object_or_404(Course1, pk=pk)
    return render(
        request, 
        'champapp/admin/course-detail-adv.html', 
        {'class_course': class_course, 'profile': profile, 'course': course}
    )



############base.htmlfor header###########
from django.shortcuts import render

# View for the base page (base.html)
def base_view(request):
    return render(request, 'champapp/base.html')

from django.shortcuts import render
from .models import Course1

def course_list(request):
    # Fetch all created courses
    courses = Course1.objects.all()
    paginator = Paginator(courses, 10)  # Show 10 courses per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'course_list.html', {'page_obj': page_obj})

#########courselist#######
from django.shortcuts import render
from django.core.paginator import Paginator
from .models import Course1
from django.db.models import Count



def course_list_view(request):
    # Fetch all courses with their creators
    courses = Course1.objects.select_related('creator')
    # Get the counts for each category
    live_courses_count = Course1.objects.filter(status=Course1.LIVE).count()
    pending_courses_count = Course1.objects.filter(status=Course1.PENDING).count()
    rejected_courses_count = Course1.objects.filter(status=Course1.REJECTED).count()
    # Debug: Log or print to check courses
    print(courses)  # Or use logging.debug if preferred
    
    # Get creator_id from query parameters (if provided)
    creator_id = request.GET.get('creator_id')
    status = request.GET.get('status')

    if creator_id:
        courses = courses.filter(creator_id=creator_id)
    if status:
        courses = courses.filter(status=status)
        

    # Pagination logic: Show 10 courses per page
    paginator = Paginator(courses, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Render the course list template with paginated courses
    return render(request, 'champapp/course_list.html', {
        'courses': page_obj,
        'live_courses_count': live_courses_count,
        'pending_courses_count': pending_courses_count,
        'rejected_courses_count': rejected_courses_count,
    })


#########coursedelete###########
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404

@login_required
@user_passes_test(superuser_or_staff_required)
def delete_course_view(request, course_id):
    course = get_object_or_404(Course1, id=course_id)
    if request.method == 'POST':
        course.delete()
        return redirect('course_list')
    return render(request, 'champapp/course_list.html', {'course': course})


############aprove_reject################
from django.shortcuts import render, get_object_or_404, redirect
from .models import Course1  # Change to import Course1 instead of Course

def approve_course(request, course_id):
    course = get_object_or_404(Course1, id=course_id)
    # If the course is either Pending or Rejected, approve it and make it live
    if course.status in [Course1.PENDING, Course1.REJECTED]:
        course.status = Course1.LIVE  # Set status to 'Live'
        course.save()
    return redirect('course_list')  # Redirect back to the course list

def reject_course(request, course_id):
    course = get_object_or_404(Course1, id=course_id)  # Correct model reference here
    course.status = Course1.REJECTED  # Set status to 'Rejected'
    course.save()
    return redirect('course_list')  # Redirect to the course list view or wherever you need

# View to unlive (set Pending)
def unlive_course(request, course_id):
    course = get_object_or_404(Course1, id=course_id)
    course.status = Course1.PENDING  # Set status back to 'Pending'
    course.save()
    return redirect('course_list')  # Redirect to the course list view or wherever you need


#######student enrollment############
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Course1, EnrolledCourse

@login_required
def add_to_cart(request, course_id):
    # Get the course object
    course = get_object_or_404(Course1, id=course_id)
    
    # Ensure the price is passed when creating the EnrolledCourse
    EnrolledCourse.objects.get_or_create(
        student=request.user,  # The currently logged-in user (student)
        course=course,         # The selected course
        defaults={'price': course.price}  # Set the price from the course
    )
    
    return redirect('student-dashboard')  # Redirect to the student dashboard


from django.shortcuts import redirect, get_object_or_404
from .models import Course1

@login_required
def buy_now(request, course_id):
    course = get_object_or_404(Course1, id=course_id)
    # Implement the logic for "Buy Now" (e.g., enrollment, payment redirection, etc.)
    return redirect('student-dashboard')  # Redirect to a relevant page


from django.shortcuts import render, get_object_or_404
from .models import Course1

def continue_course(request, course_id):
    course = get_object_or_404(Course1, id=course_id)
    # Implement the logic for continuing the course
    return render(request, 'champapp/course_detail.html', {'course': course})


# enroll in course######################

from django.shortcuts import render, get_object_or_404
from .models import Course1, EnrolledCourse
from django.contrib.auth.models import User

def enroll_in_course(request, course_id):
    # Get the course object using the course ID
    course = get_object_or_404(Course1, id=course_id)
    student = request.user  # Assuming the logged-in user is the student

    # Create an enrollment for the student in the course
    enrolled_course = EnrolledCourse.objects.create(
        student=student,
        course=course,
        price=course.price,  # Copy the course price here
        status='in_progress'  # Initial status is 'in_progress'
    )
    
    # Redirect or render a success page
    return render(request, 'course_enrolled_success.html', {'course': course})


def mark_lecture_as_completed(request, course_id, lecture_id):
    enrolled_course = EnrolledCourse.objects.get(student=request.user, course_id=course_id)
    lecture = Lecture.objects.get(id=lecture_id, course=enrolled_course.course)

    # Mark lecture as completed and update progress
    enrolled_course.complete_lecture(lecture)
    enrolled_course.update_progress()

    return redirect('course_detail', course_id=course_id)


#-------------dashboard View---------------------#
from django.db.models import Sum
from datetime import datetime, timedelta
from .models import EnrolledCourse

def dashboard_view(request):
    # Current date
    current_date = datetime.now()

    # Define start and end dates for current and last month
    start_of_current_month = current_date.replace(day=1)
    start_of_last_month = (start_of_current_month - timedelta(days=1)).replace(day=1)
    end_of_last_month = start_of_current_month - timedelta(days=1)

    # Current month earnings
    current_month_earnings = (
        EnrolledCourse.objects.filter(date_enrolled__gte=start_of_current_month)
        .aggregate(total=Sum('price'))['total']
        or 0
    )

    # Last month earnings
    last_month_earnings = (
        EnrolledCourse.objects.filter(date_enrolled__range=[start_of_last_month, end_of_last_month])
        .aggregate(total=Sum('price'))['total']
        or 0
    )

    # Percentage change
    if last_month_earnings > 0:
        percentage_change = ((current_month_earnings - last_month_earnings) / last_month_earnings) * 100
    else:
        percentage_change = 0

    # Monthly data for chart
    monthly_data = []
    for month_offset in range(12):
        month_start = start_of_current_month - timedelta(days=30 * month_offset)
        month_end = month_start + timedelta(days=30)
        month_total = (
            EnrolledCourse.objects.filter(date_enrolled__range=[month_start, month_end])
            .aggregate(total=Sum('price'))['total']
            or 0
        )
        monthly_data.append(month_total)

    monthly_data.reverse()  # Reverse to start from the earliest month

    context = {
        "current_month_earnings": current_month_earnings,
        "last_month_earnings": last_month_earnings,
        "percentage_change": percentage_change,
        "monthly_data": monthly_data,
    }
    return render(request, "champapp/student_dashboard/student-dashboard.html", context)


#--------------student whistlist view------------------#
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from champapp.models import StudentProfile  # Adjust this import based on your actual app and models

@login_required
def student_bookmark(request):
    # Fetch the student's profile
    student_profile = request.user.studentprofile  # Assumes a OneToOneField relationship between User and StudentProfile

    # Fetch all favorite courses
    favorite_courses = student_profile.favorites.all()

    # Pass favorite courses to the template
    context = {
        'page_title': 'Student Bookmarks',
        'favorite_courses': favorite_courses,
    }
    return render(request, 'champapp/student_dashboard/student-bookmark.html', context)


from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Course1, FavoriteCourse

@login_required
def toggle_favorite(request, course_id):
    course = get_object_or_404(Course1, id=course_id)
    favorite, created = FavoriteCourse.objects.get_or_create(user=request.user, course=course)
    
    if not created:  # Already favorited, so remove it
        favorite.delete()
        return JsonResponse({'status': 'removed', 'message': f"Removed {course.name} from favorites."})
    
    return JsonResponse({'status': 'added', 'message': f"Added {course.name} to favorites."})

@login_required
def student_bookmarks(request):
    favorites = FavoriteCourse.objects.filter(user=request.user).select_related('course')
    return render(request, 'student/student-bookmark.html', {'favorites': favorites})
