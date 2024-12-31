from django.contrib import admin
from .models import Course, UserCourse, UserProfile


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'total_lectures')

@admin.register(UserCourse)
class UserCourseAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'completed_lectures')

    # Optional: Add read-only progress property
    def progress(self, obj):
        return f"{obj.progress}%"
    progress.short_description = 'Progress'

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'points', 'achieved_certificates')

from django.contrib import admin
from .models import CourseCategory, Course

admin.site.register(CourseCategory)

# CourseCategory Admin
class CourseCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

# Course Admin
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'instructor', 'rating', 'enrolled')
    search_fields = ('title', 'instructor')
    list_filter = ('category', 'rating')
    ordering = ('-rating',)


#####################testttttttttttttttt################
from django.contrib import admin
from .models import InstructorClassCourse

@admin.register(InstructorClassCourse)
class InstructorClassCourseAdmin(admin.ModelAdmin):
    list_display = (
        'course_title', 'category', 'level', 'course_time', 'total_lecture', 'price', 'discount_price', 'is_featured'
    )
    list_filter = ('category', 'level', 'is_featured')
    search_fields = ('course_title', 'short_description')



#############course1##############
from django.contrib import admin
from django import forms
from .models import Course1, FAQ, Lecture, Topic

# Custom admin form for Course1
class Course1AdminForm(forms.ModelForm):
    class Meta:
        model = Course1
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'short_description': forms.Textarea(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
        }

# Inline models
class FAQInline(admin.TabularInline):
    model = FAQ
    extra = 1

class LectureInline(admin.TabularInline):
    model = Lecture
    extra = 1

class TopicInline(admin.TabularInline):
    model = Topic
    extra = 1

# Course1 Admin
@admin.register(Course1)
class Course1Admin(admin.ModelAdmin):
    form = Course1AdminForm
    list_display = ('name', 'category', 'price', 'is_featured', 'created_at')
    search_fields = ('name', 'category')
    list_filter = ('is_featured', 'category', 'created_at')
    inlines = [FAQInline, LectureInline]

# FAQ Admin
@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'course', 'created_at')
    search_fields = ('question',)
    list_filter = ('course', 'created_at')

# Lecture Admin
@admin.register(Lecture)
class LectureAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'created_at')
    search_fields = ('title',)
    list_filter = ('course', 'created_at')

# Topic Admin
@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('name', 'lecture', 'created_at')  # Changed `title` to `name`
    search_fields = ('name',)
    list_filter = ('lecture', 'created_at')
