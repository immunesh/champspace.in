from django import forms
from .models import StudentProfile, InstructorProfile, Course, InstructorClassCourse, FAQ, Tag, Course1, Lecture, Topic, Quiz

# Student Edit Profile Form
class StudentEditProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = [
            'profile_image',
            'full_name',
            'username',
            'phone_number',
            'location',
            'about_me',
            'education',
            'facebook_username',
            'twitter_username',
            'instagram_username',
            'youtube_url',
            'email',
        ]
        widgets = {
            'profile_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'about_me': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'education': forms.TextInput(attrs={'class': 'form-control'}),
            'facebook_username': forms.TextInput(attrs={'class': 'form-control'}),
            'twitter_username': forms.TextInput(attrs={'class': 'form-control'}),
            'instagram_username': forms.TextInput(attrs={'class': 'form-control'}),
            'youtube_url': forms.URLInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }


# Instructor Profile Form
class InstructorProfileForm(forms.ModelForm):
    class Meta:
        model = InstructorProfile
        fields = [
            'profile_image',
            'full_name',
            'username',
            'phone_number',
            'location',
            'education',
            'about_me',
            'facebook_username',
            'twitter_username',
            'instagram_username',
            'youtube_url',
            'expertise',
            'courses_created',
            'ratings',
            'email',
        ]
        widgets = {
            'profile_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'education': forms.TextInput(attrs={'class': 'form-control'}),
            'about_me': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'facebook_username': forms.TextInput(attrs={'class': 'form-control'}),
            'twitter_username': forms.TextInput(attrs={'class': 'form-control'}),
            'instagram_username': forms.TextInput(attrs={'class': 'form-control'}),
            'youtube_url': forms.URLInput(attrs={'class': 'form-control'}),
            'expertise': forms.TextInput(attrs={'class': 'form-control'}),
            'courses_created': forms.NumberInput(attrs={'class': 'form-control', 'disabled': True}),
            'ratings': forms.NumberInput(attrs={'class': 'form-control', 'disabled': True}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            
        }


# Course Step One Form
class CourseStepOneForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'short_description', 'category', 'level', 'language', 'is_featured']

class CourseStepTwoForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['time', 'total_lectures', 'price', 'discount_price']

class CourseStepThreeForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['description', 'image', 'video_url', 'video_file']

class CourseStepFourForm(forms.ModelForm):
    reviewer_message = forms.CharField(
        max_length=500,
        widget=forms.Textarea(attrs={"placeholder": "Message to the reviewer"}),
        required=False,
    )
    tags = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "Enter tags separated by commas"}),
        required=False,
    )

    class Meta:
        model = Course
        fields = []  # These fields are managed manually (tags and reviewer_message)

# Instructor Class Course Form
class InstructorClassCourseForm(forms.ModelForm):
    class Meta:
        model = InstructorClassCourse
        fields = [
            'course_title', 'short_description', 'category', 'level', 'languages',
            'description', 'image', 'video_url', 'video_upload', 'is_featured', 
            'course_time', 'total_lecture', 'price', 'discount_price'
        ]

        widgets = {
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'level': forms.Select(attrs={'class': 'form-select'}),
            'languages': forms.Select(attrs={'class': 'form-select'})
        }

#############course1###############
from django import forms
from .models import Course1, Lecture, Topic, FAQ

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course1  # Updated to Course1
        fields = ['name', 'short_description', 'category','level', 'languages', 'is_featured','course_time','total_lecture', 
                  'price', 'discount', 'description']
        exclude = ['creator']
                
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'short_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'level': forms.Select(attrs={'class': 'form-select'}),
            'languages': forms.Select(attrs={'class': 'form-select'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'course_time': forms.NumberInput(attrs={'class': 'form-control'}),
            'total_lecture': forms.NumberInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'discount': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }

class MediaForm(forms.Form):
    image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )
    video_url = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={'class': 'form-control'})
    )
    video_upload = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )

class LectureForm(forms.ModelForm):
    class Meta:
        model = Lecture
        fields = ['title']

class TopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ['name', 'url', 'description', 'is_free','premium']

class FAQForm(forms.ModelForm):
    class Meta:
        model = FAQ
        fields = ['question', 'answer']



#------------------instructor-quiz---------#
# champapp/forms.py

from django import forms
from .models import Quiz

class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['question', 'option_1', 'option_2', 'option_3', 'option_4', 'correct_option']
