from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count, Sum
from django import forms
from .models import (
    Course, UserCourse, UserProfile, CourseCategory, 
    InstructorClassCourse, Course1, FAQ, Lecture, Topic,
    StudentProfile, InstructorProfile, EnrolledCourse,
    UserTopicProgress, FavoriteCourse, Quiz, Tag,
    Cart, CartItem, Payment,
    # Ad Revenue Models
    AdImpression, AdRevenue, Earning, UserWallet, 
    Withdrawal, RevenueShare
)

# ===========================
# CUSTOMIZED ADMIN SITE
# ===========================
admin.site.site_header = "ChampSpace Admin Dashboard"
admin.site.site_title = "ChampSpace Admin"
admin.site.index_title = "Welcome to ChampSpace Administration"


# ===========================
# USER MANAGEMENT
# ===========================
class CustomUserAdmin(BaseUserAdmin):
    """
    Simplified User admin without profile inlines.
    Student and Instructor profiles are managed separately.
    """
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_user_type',
                    'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    def get_user_type(self, obj):
        if obj.is_superuser:
            return format_html('<span style="background-color: #ff5722; color: white; padding: 3px 8px; border-radius: 3px; font-weight: bold;">ADMIN</span>')
        elif obj.is_staff:
            return format_html('<span style="background-color: #ff9800; color: white; padding: 3px 8px; border-radius: 3px; font-weight: bold;">INSTRUCTOR</span>')
        else:
            return format_html('<span style="background-color: #4caf50; color: white; padding: 3px 8px; border-radius: 3px; font-weight: bold;">STUDENT</span>')
    get_user_type.short_description = 'User Type'
    get_user_type.admin_order_field = 'is_staff'

# Unregister the default User admin and register our custom one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


# ===========================
# STUDENT MANAGEMENT
# ===========================
@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('get_student_id', 'full_name', 'email', 'get_user_status',
                    'phone_number', 'points', 'achieved_certificates', 
                    'location', 'education', 'get_profile_image', 'get_joined_date')
    search_fields = ('user__username', 'full_name', 'email', 'phone_number', 'location')
    list_filter = ('location', 'education', 'achieved_certificates', 'points', 
                   'user__is_active', 'user__date_joined')
    readonly_fields = ('user', 'get_profile_image_preview', 'get_enrolled_courses', 
                       'get_completed_courses', 'get_joined_date')
    list_per_page = 25
    date_hierarchy = 'user__date_joined'
    
    fieldsets = (
        ('👤 User Information', {
            'fields': ('user', 'full_name', 'username', 'email', 'get_joined_date')
        }),
        ('📞 Contact Information', {
            'fields': ('phone_number', 'location')
        }),
        ('📋 Profile Details', {
            'fields': ('get_profile_image_preview', 'profile_image', 'about_me', 'education')
        }),
        ('🏆 Achievements & Progress', {
            'fields': ('points', 'achieved_certificates', 'get_enrolled_courses', 'get_completed_courses'),
            'classes': ('wide',)
        }),
        ('🌐 Social Media Links', {
            'fields': ('facebook_username', 'twitter_username', 'instagram_username', 'youtube_url'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['activate_students', 'deactivate_students', 'reset_points', 'award_bonus_points']
    
    def get_student_id(self, obj):
        return f"STU-{obj.user.id:05d}"
    get_student_id.short_description = 'Student ID'
    get_student_id.admin_order_field = 'user__id'
    
    def get_user_status(self, obj):
        if obj.user.is_active:
            return format_html('<span style="color: green; font-weight: bold;">✓ Active</span>')
        return format_html('<span style="color: red; font-weight: bold;">✗ Inactive</span>')
    get_user_status.short_description = 'Status'
    get_user_status.admin_order_field = 'user__is_active'
    
    def get_profile_image(self, obj):
        if obj.profile_image:
            return format_html('<img src="{}" width="40" height="40" style="border-radius: 50%;" />', 
                             obj.profile_image.url)
        return '—'
    get_profile_image.short_description = 'Photo'
    
    def get_profile_image_preview(self, obj):
        if obj.profile_image:
            return format_html('<img src="{}" width="150" height="150" style="border-radius: 10px;" />', 
                             obj.profile_image.url)
        return 'No image uploaded'
    get_profile_image_preview.short_description = 'Profile Picture Preview'
    
    def get_enrolled_courses(self, obj):
        count = EnrolledCourse.objects.filter(student=obj.user).count()
        return format_html('<strong style="color: #2196F3; font-size: 16px;">{}</strong>', count)
    get_enrolled_courses.short_description = 'Enrolled Courses'
    
    def get_completed_courses(self, obj):
        count = EnrolledCourse.objects.filter(student=obj.user, progress=100).count()
        return format_html('<strong style="color: #4CAF50; font-size: 16px;">{}</strong>', count)
    get_completed_courses.short_description = 'Completed Courses'
    
    def get_joined_date(self, obj):
        return obj.user.date_joined.strftime('%B %d, %Y')
    get_joined_date.short_description = 'Joined Date'
    get_joined_date.admin_order_field = 'user__date_joined'
    
    # Admin Actions
    def activate_students(self, request, queryset):
        count = 0
        for student in queryset:
            if not student.user.is_active:
                student.user.is_active = True
                student.user.save()
                count += 1
        self.message_user(request, f'{count} student(s) activated successfully.')
    activate_students.short_description = '✓ Activate selected students'
    
    def deactivate_students(self, request, queryset):
        count = 0
        for student in queryset:
            if student.user.is_active:
                student.user.is_active = False
                student.user.save()
                count += 1
        self.message_user(request, f'{count} student(s) deactivated successfully.')
    deactivate_students.short_description = '✗ Deactivate selected students'
    
    def reset_points(self, request, queryset):
        count = queryset.update(points=0)
        self.message_user(request, f'Points reset for {count} student(s).')
    reset_points.short_description = '🔄 Reset points to 0'
    
    def award_bonus_points(self, request, queryset):
        count = 0
        for student in queryset:
            student.points += 100
            student.save()
            count += 1
        self.message_user(request, f'100 bonus points awarded to {count} student(s).')
    award_bonus_points.short_description = '🎁 Award 100 bonus points'


# ===========================
# INSTRUCTOR MANAGEMENT
# ===========================
@admin.register(InstructorProfile)
class InstructorProfileAdmin(admin.ModelAdmin):
    list_display = ('get_instructor_id', 'full_name', 'email', 'get_user_status', 
                    'expertise', 'courses_created', 'ratings', 'location', 'phone_number',
                    'get_profile_image', 'get_joined_date')
    search_fields = ('user__username', 'full_name', 'email', 'expertise', 'phone_number')
    list_filter = ('expertise', 'location', 'ratings', 'user__is_active', 'user__date_joined')
    readonly_fields = ('user', 'courses_created', 'ratings', 'get_profile_image_preview', 
                       'get_total_students', 'get_joined_date')
    list_per_page = 25
    date_hierarchy = 'user__date_joined'
    
    fieldsets = (
        ('👤 User Information', {
            'fields': ('user', 'full_name', 'username', 'email', 'get_joined_date')
        }),
        ('📞 Contact Information', {
            'fields': ('phone_number', 'location')
        }),
        ('📋 Profile Details', {
            'fields': ('get_profile_image_preview', 'profile_image', 'about_me', 'education', 'expertise')
        }),
        ('📊 Statistics & Performance', {
            'fields': ('courses_created', 'ratings', 'get_total_students'),
            'classes': ('wide',)
        }),
        ('🌐 Social Media Links', {
            'fields': ('facebook_username', 'twitter_username', 'instagram_username', 'youtube_url'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['activate_instructors', 'deactivate_instructors', 'send_welcome_email']
    
    def get_instructor_id(self, obj):
        return f"INST-{obj.user.id:05d}"
    get_instructor_id.short_description = 'Instructor ID'
    get_instructor_id.admin_order_field = 'user__id'
    
    def get_user_status(self, obj):
        if obj.user.is_active:
            return format_html('<span style="color: green; font-weight: bold;">✓ Active</span>')
        return format_html('<span style="color: red; font-weight: bold;">✗ Inactive</span>')
    get_user_status.short_description = 'Status'
    get_user_status.admin_order_field = 'user__is_active'
    
    def get_profile_image(self, obj):
        if obj.profile_image:
            return format_html('<img src="{}" width="40" height="40" style="border-radius: 50%;" />', 
                             obj.profile_image.url)
        return '—'
    get_profile_image.short_description = 'Photo'
    
    def get_profile_image_preview(self, obj):
        if obj.profile_image:
            return format_html('<img src="{}" width="150" height="150" style="border-radius: 10px;" />', 
                             obj.profile_image.url)
        return 'No image uploaded'
    get_profile_image_preview.short_description = 'Profile Picture Preview'
    
    def get_total_students(self, obj):
        # Count total students enrolled in this instructor's courses
        total = EnrolledCourse.objects.filter(course__creator=obj.user).values('student').distinct().count()
        return format_html('<strong style="color: #2196F3; font-size: 16px;">{}</strong>', total)
    get_total_students.short_description = 'Total Students Enrolled'
    
    def get_joined_date(self, obj):
        return obj.user.date_joined.strftime('%B %d, %Y')
    get_joined_date.short_description = 'Joined Date'
    get_joined_date.admin_order_field = 'user__date_joined'
    
    # Admin Actions
    def activate_instructors(self, request, queryset):
        count = 0
        for instructor in queryset:
            if not instructor.user.is_active:
                instructor.user.is_active = True
                instructor.user.save()
                count += 1
        self.message_user(request, f'{count} instructor(s) activated successfully.')
    activate_instructors.short_description = '✓ Activate selected instructors'
    
    def deactivate_instructors(self, request, queryset):
        count = 0
        for instructor in queryset:
            if instructor.user.is_active:
                instructor.user.is_active = False
                instructor.user.save()
                count += 1
        self.message_user(request, f'{count} instructor(s) deactivated successfully.')
    deactivate_instructors.short_description = '✗ Deactivate selected instructors'
    
    def send_welcome_email(self, request, queryset):
        count = queryset.count()
        # Placeholder for email sending logic
        self.message_user(request, f'Welcome email would be sent to {count} instructor(s).')
    send_welcome_email.short_description = '✉ Send welcome email'


# ===========================
# COURSE MANAGEMENT
# ===========================
@admin.register(CourseCategory)
class CourseCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'course_count')
    search_fields = ('name',)
    
    def course_count(self, obj):
        return Course1.objects.filter(category=obj.name).count()
    course_count.short_description = 'Number of Courses'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'course_count')
    search_fields = ('name',)
    
    def course_count(self, obj):
        return obj.courses.count()
    course_count.short_description = 'Courses'


# Custom admin form for Course1
class Course1AdminForm(forms.ModelForm):
    class Meta:
        model = Course1
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter course name'}),
            'short_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'discount': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100}),
            'total_lecture': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'course_time': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 10 hours'}),
        }


# Inline models for Course1
class FAQInline(admin.TabularInline):
    model = FAQ
    extra = 1
    fields = ('question', 'answer')

class TopicInline(admin.TabularInline):
    model = Topic
    extra = 1
    fields = ('name', 'description', 'video_url', 'video_file', 'is_free', 'premium', 'duration')
    readonly_fields = ('duration',)

class LectureInline(admin.StackedInline):
    model = Lecture
    extra = 1
    fields = ('title',)
    show_change_link = True


@admin.register(Course1)
class Course1Admin(admin.ModelAdmin):
    form = Course1AdminForm
    list_display = ('name', 'category', 'level', 'price_display', 'status_badge', 
                    'is_featured', 'enrollment_count', 'created_at')
    search_fields = ('name', 'category', 'tags', 'creator__username')
    list_filter = ('status', 'is_featured', 'category', 'level', 'languages', 'created_at')
    readonly_fields = ('creator', 'created_at')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    
    inlines = [FAQInline, LectureInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'short_description', 'description', 'creator', 'status')
        }),
        ('Course Details', {
            'fields': ('category', 'level', 'languages', 'course_time', 'total_lecture')
        }),
        ('Pricing', {
            'fields': ('price', 'discount', 'is_featured')
        }),
        ('Media', {
            'fields': ('image', 'video_url', 'video_upload'),
            'classes': ('collapse',)
        }),
        ('Additional Information', {
            'fields': ('tags', 'message_to_reviewer', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_courses', 'reject_courses', 'feature_courses', 'unfeature_courses']
    
    def price_display(self, obj):
        if obj.discount > 0:
            discounted_price = float(obj.price) * (1 - float(obj.discount) / 100)
            original_price = f'{float(obj.price):.2f}'
            final_price = f'{discounted_price:.2f}'
            return format_html(
                '<span style="text-decoration: line-through; color: #999;">₹{}</span> <strong style="color: #28a745;">₹{}</strong>',
                original_price, final_price
            )
        price_formatted = f'{float(obj.price):.2f}'
        return format_html('₹{}', price_formatted)
    price_display.short_description = 'Price'
    
    def status_badge(self, obj):
        colors = {
            'Pending': '#ffc107',
            'Live': '#28a745',
            'Rejected': '#dc3545'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            colors.get(obj.status, '#6c757d'), obj.status
        )
    status_badge.short_description = 'Status'
    
    def enrollment_count(self, obj):
        count = EnrolledCourse.objects.filter(course=obj).count()
        return format_html('<strong>{}</strong>', count)
    enrollment_count.short_description = 'Enrollments'
    
    def approve_courses(self, request, queryset):
        updated = queryset.update(status='Live')
        self.message_user(request, f'{updated} course(s) approved successfully.')
    approve_courses.short_description = 'Approve selected courses'
    
    def reject_courses(self, request, queryset):
        updated = queryset.update(status='Rejected')
        self.message_user(request, f'{updated} course(s) rejected.')
    reject_courses.short_description = 'Reject selected courses'
    
    def feature_courses(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} course(s) marked as featured.')
    feature_courses.short_description = 'Mark as featured'
    
    def unfeature_courses(self, request, queryset):
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'{updated} course(s) unmarked as featured.')
    unfeature_courses.short_description = 'Remove from featured'


@admin.register(Lecture)
class LectureAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'topics_count', 'created_at')
    search_fields = ('title', 'course__name')
    list_filter = ('course', 'created_at')
    inlines = [TopicInline]
    
    def topics_count(self, obj):
        return obj.topics.count()
    topics_count.short_description = 'Topics'


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('name', 'lecture', 'duration_display', 'is_free', 'premium', 'created_at')
    search_fields = ('name', 'lecture__title')
    list_filter = ('is_free', 'premium', 'lecture__course', 'created_at')
    readonly_fields = ('duration',)
    
    fieldsets = (
        ('Topic Information', {
            'fields': ('lecture', 'name', 'description')
        }),
        ('Content', {
            'fields': ('video_url', 'video_file', 'duration')
        }),
        ('Access', {
            'fields': ('is_free', 'premium')
        }),
    )
    
    def duration_display(self, obj):
        return obj.get_duration()
    duration_display.short_description = 'Duration'


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'course', 'created_at')
    search_fields = ('question', 'answer', 'course__name')
    list_filter = ('course', 'created_at')


# ===========================
# ENROLLMENT MANAGEMENT
# ===========================
@admin.register(EnrolledCourse)
class EnrolledCourseAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'progress_bar', 'status', 'completed_lectures', 
                    'watch_time_hours', 'date_enrolled')
    search_fields = ('student__username', 'course__name')
    list_filter = ('status', 'date_enrolled', 'course')
    readonly_fields = ('date_enrolled', 'progress_percentage')
    date_hierarchy = 'date_enrolled'
    
    fieldsets = (
        ('Enrollment Information', {
            'fields': ('student', 'course', 'date_enrolled', 'price')
        }),
        ('Progress', {
            'fields': ('status', 'progress', 'progress_percentage', 'completed_lectures', 
                       'completed_topics', 'watch_time')
        }),
    )
    
    def progress_bar(self, obj):
        progress = obj.progress_percentage
        color = '#28a745' if progress >= 80 else '#ffc107' if progress >= 50 else '#dc3545'
        return format_html(
            '<div style="width: 100px; background-color: #e9ecef; border-radius: 4px;">'
            '<div style="width: {}%; background-color: {}; height: 20px; border-radius: 4px; text-align: center; color: white; font-weight: bold; line-height: 20px;">{}</div>'
            '</div>',
            progress, color, f'{progress:.1f}%'
        )
    progress_bar.short_description = 'Progress'
    
    def watch_time_hours(self, obj):
        hours = obj.watch_time // 60
        minutes = obj.watch_time % 60
        return f'{hours}h {minutes}m'
    watch_time_hours.short_description = 'Watch Time'


@admin.register(UserTopicProgress)
class UserTopicProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'topic', 'lecture_name', 'course_name', 'completed_badge')
    search_fields = ('user__username', 'topic__name')
    list_filter = ('completed', 'topic__lecture__course')
    
    def lecture_name(self, obj):
        return obj.topic.lecture.title
    lecture_name.short_description = 'Lecture'
    
    def course_name(self, obj):
        return obj.topic.lecture.course.name
    course_name.short_description = 'Course'
    
    def completed_badge(self, obj):
        if obj.completed:
            return format_html('<span style="color: #28a745;">✓ Completed</span>')
        return format_html('<span style="color: #dc3545;">✗ Incomplete</span>')
    completed_badge.short_description = 'Status'


# ===========================
# OLD COURSE MODELS (Legacy)
# ===========================
# Course admin removed - using Course1 (All courses) as the main course model
# UserCourse admin removed - EnrolledCourse provides comprehensive enrollment management
# UserProfile admin removed - students and instructors have separate profile tables
# InstructorClassCourse admin removed - legacy model, replaced by Course1 (All Courses)


# ===========================
# FAVORITES & CART
# ===========================
@admin.register(FavoriteCourse)
class FavoriteCourseAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'added_at')
    search_fields = ('user__username', 'course__name')
    list_filter = ('added_at',)
    date_hierarchy = 'added_at'


# Cart admin removed - Cart Items provides comprehensive cart management


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart_user', 'course', 'quantity', 'total_price_display')
    search_fields = ('cart__user__username', 'course__name')
    
    def cart_user(self, obj):
        return obj.cart.user.username
    cart_user.short_description = 'User'
    
    def total_price_display(self, obj):
        return f'₹{obj.total_price}'
    total_price_display.short_description = 'Total Price'


# ===========================
# PAYMENTS
# ===========================
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'amount', 'status_badge', 'razorpay_payment_id', 'created_at')
    search_fields = ('user__username', 'course__name', 'razorpay_order_id', 'razorpay_payment_id')
    list_filter = ('status', 'created_at')
    readonly_fields = ('created_at', 'razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature')
    date_hierarchy = 'created_at'
    
    def status_badge(self, obj):
        colors = {
            'Pending': '#ffc107',
            'Completed': '#28a745',
            'Failed': '#dc3545'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            colors.get(obj.status, '#6c757d'), obj.status
        )
    status_badge.short_description = 'Status'


# ===========================
# QUIZ MANAGEMENT
# ===========================
@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('question', 'correct_option', 'created_by')
    search_fields = ('question',)
    list_filter = ('correct_option', 'created_by')


# ===========================
# AD REVENUE & EARNINGS MANAGEMENT
# ===========================

@admin.register(AdImpression)
class AdImpressionAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'ad_platform', 'estimated_revenue_display', 'viewed_at', 'is_valid')
    list_filter = ('ad_platform', 'is_valid', 'viewed_at')
    search_fields = ('user__username', 'course__name', 'ad_unit_id')
    date_hierarchy = 'viewed_at'
    readonly_fields = ('viewed_at',)
    
    def estimated_revenue_display(self, obj):
        return format_html('<span style="color: green; font-weight: bold;">₹{}</span>', f'{float(obj.estimated_revenue):.4f}')
    estimated_revenue_display.short_description = 'Revenue'
    
    fieldsets = (
        ('User & Course', {
            'fields': ('user', 'course', 'lecture')
        }),
        ('Ad Details', {
            'fields': ('ad_platform', 'ad_unit_id', 'cpm_rate', 'estimated_revenue')
        }),
        ('Tracking', {
            'fields': ('viewed_at', 'ip_address', 'user_agent', 'view_duration', 'is_valid')
        }),
    )


@admin.register(AdRevenue)
class AdRevenueAdmin(admin.ModelAdmin):
    list_display = ('date', 'total_revenue_display', 'google_revenue', 'facebook_revenue', 
                    'total_impressions', 'average_cpm', 'is_synced')
    list_filter = ('is_synced', 'date')
    search_fields = ('date',)
    date_hierarchy = 'date'
    readonly_fields = ('created_at', 'updated_at', 'last_synced_at')
    
    def total_revenue_display(self, obj):
        revenue_formatted = f'{obj.total_revenue:,.2f}'
        return format_html('<span style="color: green; font-weight: bold;">₹{}</span>', revenue_formatted)
    total_revenue_display.short_description = 'Total Revenue'
    
    def google_revenue(self, obj):
        revenue_formatted = f'{obj.google_adsense_revenue:,.2f}'
        return format_html('₹{}', revenue_formatted)
    google_revenue.short_description = 'Google AdSense'
    
    def facebook_revenue(self, obj):
        revenue_formatted = f'{obj.facebook_ads_revenue:,.2f}'
        return format_html('₹{}', revenue_formatted)
    facebook_revenue.short_description = 'Facebook Ads'


@admin.register(Earning)
class EarningAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'earning_type', 'amount_display', 'status', 'earned_at')
    list_filter = ('earning_type', 'status', 'earned_at')
    search_fields = ('user__username', 'course__name', 'description')
    date_hierarchy = 'earned_at'
    readonly_fields = ('earned_at', 'approved_at', 'paid_at')
    actions = ['approve_earnings', 'mark_as_paid']
    
    def amount_display(self, obj):
        color = 'green' if obj.status == 'paid' else 'orange' if obj.status == 'approved' else 'gray'
        return format_html('<span style="color: {}; font-weight: bold;">₹{}</span>', color, f'{float(obj.amount):.2f}')
    amount_display.short_description = 'Amount'
    
    def approve_earnings(self, request, queryset):
        from django.utils import timezone
        updated = queryset.filter(status='pending').update(status='approved', approved_at=timezone.now())
        self.message_user(request, f'{updated} earnings approved successfully.')
    approve_earnings.short_description = 'Approve selected earnings'
    
    def mark_as_paid(self, request, queryset):
        from django.utils import timezone
        updated = queryset.filter(status='approved').update(status='paid', paid_at=timezone.now())
        self.message_user(request, f'{updated} earnings marked as paid.')
    mark_as_paid.short_description = 'Mark as paid'
    
    fieldsets = (
        ('User & Course', {
            'fields': ('user', 'course', 'earning_type')
        }),
        ('Amount', {
            'fields': ('amount', 'description')
        }),
        ('Status', {
            'fields': ('status', 'earned_at', 'approved_at', 'paid_at', 'withdrawal')
        }),
    )


@admin.register(UserWallet)
class UserWalletAdmin(admin.ModelAdmin):
    list_display = ('user', 'available_balance_display', 'pending_balance_display', 
                    'withdrawn_display', 'total_earned_display', 'total_watch_time', 
                    'total_ad_impressions')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at')
    actions = ['update_all_balances']
    
    def available_balance_display(self, obj):
        balance_formatted = f'{obj.available_balance:,.2f}'
        return format_html('<span style="color: green; font-weight: bold;">₹{}</span>', balance_formatted)
    available_balance_display.short_description = 'Available'
    
    def pending_balance_display(self, obj):
        balance_formatted = f'{obj.pending_balance:,.2f}'
        return format_html('<span style="color: orange;">₹{}</span>', balance_formatted)
    pending_balance_display.short_description = 'Pending'
    
    def withdrawn_display(self, obj):
        amount_formatted = f'{obj.withdrawn_amount:,.2f}'
        return format_html('<span style="color: gray;">₹{}</span>', amount_formatted)
    withdrawn_display.short_description = 'Withdrawn'
    
    def total_earned_display(self, obj):
        earned_formatted = f'{obj.total_earned:,.2f}'
        return format_html('<span style="color: blue; font-weight: bold;">₹{}</span>', earned_formatted)
    total_earned_display.short_description = 'Total Earned'
    
    def update_all_balances(self, request, queryset):
        for wallet in queryset:
            wallet.update_balance()
        self.message_user(request, f'{queryset.count()} wallets updated successfully.')
    update_all_balances.short_description = 'Update balances'


@admin.register(Withdrawal)
class WithdrawalAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount_display', 'payment_method', 'status_badge', 'requested_at', 'completed_at')
    list_filter = ('status', 'payment_method', 'requested_at')
    search_fields = ('user__username', 'transaction_id', 'upi_id', 'account_number')
    date_hierarchy = 'requested_at'
    readonly_fields = ('requested_at', 'processed_at', 'completed_at', 'net_amount')
    actions = ['approve_withdrawals', 'reject_withdrawals', 'mark_as_completed']
    
    def amount_display(self, obj):
        return format_html('<span style="font-weight: bold;">₹{}</span>', f'{float(obj.amount):,.2f}')
    amount_display.short_description = 'Amount'
    
    def status_badge(self, obj):
        colors = {
            'pending': '#ffc107',
            'processing': '#17a2b8',
            'completed': '#28a745',
            'rejected': '#dc3545',
            'cancelled': '#6c757d'
        }
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            colors.get(obj.status, '#6c757d'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def approve_withdrawals(self, request, queryset):
        from django.utils import timezone
        updated = queryset.filter(status='pending').update(status='processing', processed_at=timezone.now(), processed_by=request.user)
        self.message_user(request, f'{updated} withdrawals approved and set to processing.')
    approve_withdrawals.short_description = 'Approve and process'
    
    def reject_withdrawals(self, request, queryset):
        updated = queryset.filter(status='pending').update(status='rejected')
        self.message_user(request, f'{updated} withdrawals rejected.')
    reject_withdrawals.short_description = 'Reject selected'
    
    def mark_as_completed(self, request, queryset):
        from django.utils import timezone
        updated = queryset.filter(status='processing').update(status='completed', completed_at=timezone.now())
        self.message_user(request, f'{updated} withdrawals marked as completed.')
    mark_as_completed.short_description = 'Mark as completed'
    
    fieldsets = (
        ('User & Amount', {
            'fields': ('user', 'amount', 'processing_fee', 'net_amount')
        }),
        ('Payment Details', {
            'fields': ('payment_method', 'bank_name', 'account_number', 'ifsc_code', 'upi_id', 'transaction_id')
        }),
        ('Status & Notes', {
            'fields': ('status', 'user_notes', 'admin_notes', 'rejection_reason', 'processed_by')
        }),
        ('Timestamps', {
            'fields': ('requested_at', 'processed_at', 'completed_at')
        }),
    )


@admin.register(RevenueShare)
class RevenueShareAdmin(admin.ModelAdmin):
    list_display = ('get_name', 'student_share', 'instructor_share', 'platform_share', 
                    'earnings_per_minute', 'completion_bonus', 'is_default')
    list_filter = ('is_default',)
    search_fields = ('course__name',)
    
    def get_name(self, obj):
        if obj.course:
            return f"Revenue Share: {obj.course.name}"
        return "Default Revenue Share"
    get_name.short_description = 'Configuration'
    
    def student_share(self, obj):
        return format_html('<span style="color: blue; font-weight: bold;">{}%</span>', obj.student_share_percentage)
    student_share.short_description = 'Student Share'
    
    def instructor_share(self, obj):
        return format_html('<span style="color: green; font-weight: bold;">{}%</span>', obj.instructor_share_percentage)
    instructor_share.short_description = 'Instructor Share'
    
    def platform_share(self, obj):
        return format_html('<span style="color: orange; font-weight: bold;">{}%</span>', obj.platform_share_percentage)
    platform_share.short_description = 'Platform Fee'
    
    fieldsets = (
        ('Revenue Split', {
            'fields': ('student_share_percentage', 'instructor_share_percentage', 'platform_share_percentage')
        }),
        ('Earning Rules', {
            'fields': ('minimum_watch_time', 'earnings_per_minute', 'completion_bonus')
        }),
        ('Configuration', {
            'fields': ('course', 'is_default')
        }),
    )

