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
    Cart, CartItem, Payment
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
class StudentProfileInline(admin.StackedInline):
    model = StudentProfile
    can_delete = False
    verbose_name_plural = 'Student Profile'
    fk_name = 'user'
    fields = ('full_name', 'username', 'phone_number', 'location', 'education', 
              'profile_image', 'points', 'achieved_certificates', 'email')

class InstructorProfileInline(admin.StackedInline):
    model = InstructorProfile
    can_delete = False
    verbose_name_plural = 'Instructor Profile'
    fk_name = 'user'
    fields = ('full_name', 'username', 'phone_number', 'location', 'education',
              'profile_image', 'courses_created', 'expertise', 'ratings', 'email')

class CustomUserAdmin(BaseUserAdmin):
    inlines = (StudentProfileInline,)
    
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 
                    'is_active', 'date_joined', 'enrolled_courses_count')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    def enrolled_courses_count(self, obj):
        return EnrolledCourse.objects.filter(student=obj).count()
    enrolled_courses_count.short_description = 'Enrolled Courses'

# Unregister the default User admin and register our custom one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


# ===========================
# STUDENT MANAGEMENT
# ===========================
@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'email', 'phone_number', 'points', 
                    'achieved_certificates', 'location', 'education')
    search_fields = ('user__username', 'full_name', 'email', 'phone_number')
    list_filter = ('location', 'education', 'achieved_certificates')
    readonly_fields = ('user',)
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'full_name', 'username', 'email')
        }),
        ('Contact Information', {
            'fields': ('phone_number', 'location')
        }),
        ('Profile Details', {
            'fields': ('profile_image', 'about_me', 'education')
        }),
        ('Achievements', {
            'fields': ('points', 'achieved_certificates')
        }),
        ('Social Media', {
            'fields': ('facebook_username', 'twitter_username', 'instagram_username', 'youtube_url'),
            'classes': ('collapse',)
        }),
    )


# ===========================
# INSTRUCTOR MANAGEMENT
# ===========================
@admin.register(InstructorProfile)
class InstructorProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'email', 'expertise', 'courses_created', 
                    'ratings', 'location')
    search_fields = ('user__username', 'full_name', 'email', 'expertise')
    list_filter = ('expertise', 'location', 'ratings')
    readonly_fields = ('user', 'courses_created', 'ratings')
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'full_name', 'username', 'email')
        }),
        ('Contact Information', {
            'fields': ('phone_number', 'location')
        }),
        ('Profile Details', {
            'fields': ('profile_image', 'about_me', 'education', 'expertise')
        }),
        ('Statistics', {
            'fields': ('courses_created', 'ratings')
        }),
        ('Social Media', {
            'fields': ('facebook_username', 'twitter_username', 'instagram_username', 'youtube_url'),
            'classes': ('collapse',)
        }),
    )


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
            return format_html(
                '<span style="text-decoration: line-through; color: #999;">₹{}</span> <strong style="color: #28a745;">₹{:.2f}</strong>',
                obj.price, discounted_price
            )
        return f'₹{obj.price}'
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
            '<div style="width: {}%; background-color: {}; height: 20px; border-radius: 4px; text-align: center; color: white; font-weight: bold; line-height: 20px;">{:.1f}%</div>'
            '</div>',
            progress, color, progress
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
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'level', 'price', 'status', 'rating', 'enrolled')
    search_fields = ('title', 'description')
    list_filter = ('status', 'level', 'category', 'is_featured')
    ordering = ('-rating',)


@admin.register(UserCourse)
class UserCourseAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'completed_lectures', 'progress_display')
    search_fields = ('user__username', 'course__title')
    
    def progress_display(self, obj):
        return f"{obj.progress}%"
    progress_display.short_description = 'Progress'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'points', 'achieved_certificates')
    search_fields = ('user__username',)


@admin.register(InstructorClassCourse)
class InstructorClassCourseAdmin(admin.ModelAdmin):
    list_display = ('course_title', 'category', 'level', 'course_time', 'total_lecture', 
                    'price', 'discount_price', 'is_featured')
    list_filter = ('category', 'level', 'is_featured')
    search_fields = ('course_title', 'short_description')


# ===========================
# FAVORITES & CART
# ===========================
@admin.register(FavoriteCourse)
class FavoriteCourseAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'added_at')
    search_fields = ('user__username', 'course__name')
    list_filter = ('added_at',)
    date_hierarchy = 'added_at'


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'items_count', 'created_at')
    search_fields = ('user__username',)
    readonly_fields = ('created_at',)
    
    def items_count(self, obj):
        return obj.items.count()
    items_count.short_description = 'Items'


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
