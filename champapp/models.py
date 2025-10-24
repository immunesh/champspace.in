from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ObjectDoesNotExist
from moviepy import VideoFileClip

# Tag Model
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

# CourseCategory Model
class CourseCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

# Cart Model
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart for {self.user.username}"

# CartItem Model
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    course = models.ForeignKey('Course1', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.course.name} (x{self.quantity}) in {self.cart.user.username}'s cart"

    @property
    def total_price(self):
        return self.course.price * self.quantity

# Payment Model
class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey('Course1', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    razorpay_order_id = models.CharField(max_length=100, unique=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=50, default="Pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.course.name} - {self.status}"

# Course Model
class Course(models.Model):
    LEVEL_CHOICES = [
        ('Beginner', 'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('All level', 'All level'),
    ]

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Live', 'Live'),
    ]

    total_lectures = models.PositiveIntegerField()
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(
        CourseCategory, 
        on_delete=models.CASCADE, 
        related_name="courses",
        null=True, 
        blank=True
    )

    instructor = models.ForeignKey(
    User,
    on_delete=models.CASCADE,
    related_name='instructor_courses',
    null=True,  # Add this
    blank=True  # Add this
    )

    title = models.CharField(max_length=200)
    added_date = models.DateField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='Beginner')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=0.0)
    enrolled = models.PositiveIntegerField(default=0)
    thumbnail = models.ImageField(upload_to="course_thumbnails/", blank=True, null=True)
    short_description = models.TextField()
    category = models.ForeignKey(
        CourseCategory, on_delete=models.SET_NULL, null=True, related_name="courses"
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name="courses")
    language = models.CharField(max_length=255, null=True, blank=True)  # Comma-separated values (for multiple languages)
    is_featured = models.BooleanField(default=False)
    time = models.CharField(max_length=255, default="Please add time")
    total_lectures = models.PositiveIntegerField()
    total_lecture = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    # Media fields for course image and video
    image = models.ImageField(upload_to="course_images/", blank=True, null=True)
    video_url = models.URLField(max_length=200, blank=True, null=True)
    video_file = models.FileField(upload_to="course_videos/", blank=True, null=True)
    reviewer_message = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        # Assign default category if none is provided
        if not self.category:
            default_category, _ = CourseCategory.objects.get_or_create(
                name="Default Category",
                defaults={"description": "This is the default category for uncategorized courses."},
            )
            self.category = default_category
        super().save(*args, **kwargs)  # Call the original save method

    def __str__(self):
        return self.title

# UserCourse Model
class UserCourse(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_courses')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    completed_lectures = models.PositiveIntegerField(default=0)

    @property
    def progress(self):
        # Calculate progress as percentage
        if self.course.total_lectures > 0:
            return (self.completed_lectures / self.course.total_lectures) * 100
        return 0  # Avoid division by zero

    def __str__(self):
        return f"{self.user.username} - {self.course.title}"

# Profile Model
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_image = models.ImageField(upload_to="profile_images/", default="profile_images/default.jpg", blank=True)
    points = models.IntegerField(default=0)
    achieved_certificates = models.IntegerField(default=0)
    favorites = models.ManyToManyField(
        'Course',
        related_name='profile_favorites',  # Unique reverse accessor
        blank=True
    )

    def __str__(self):
        return self.user.username


# UserProfile Model
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_image = models.ImageField(upload_to="profile_images/", default="default.jpg")
    points = models.IntegerField(default=0)
    achieved_certificates = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username

class Lesson(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)  # Assuming you have a Course model
    title = models.CharField(max_length=255)
    completed = models.BooleanField(default=False)  # Tracks if the user has completed the lesson
    # Other fields as necessary

    def __str__(self):
        return self.title


# Signal to create UserProfile when a User is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Create the profile only if it doesn't already exist
        UserProfile.objects.get_or_create(user=instance)

# Signal to save UserProfile when the User is saved
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        # Ensure that the profile is created and saved
        user_profile, created = UserProfile.objects.get_or_create(user=instance)
        user_profile.save()  # Make sure the profile is saved properly
    except ObjectDoesNotExist:
        # If profile doesn't exist, create it
        UserProfile.objects.create(user=instance)

# StudentProfile Model
class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Linking to the User model
    full_name = models.CharField(max_length=100, blank=True)  # Combining first_name and last_name into full_name
    username = models.CharField(max_length=50, unique=True, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True)
    location = models.CharField(max_length=100, blank=True)
    about_me = models.TextField(blank=True)
    facebook_username = models.CharField(max_length=50, blank=True)
    twitter_username = models.CharField(max_length=50, blank=True)
    instagram_username = models.CharField(max_length=50, blank=True)
    youtube_url = models.URLField(max_length=200, blank=True)
    profile_image = models.ImageField(upload_to='students/profile_images/', null=True, blank=True)
    achieved_certificates = models.IntegerField(default=0)
    education = models.CharField(max_length=255, blank=True)
    points = models.IntegerField(default=0)
    email = models.EmailField(max_length=255, blank=True, null=True)
    favorites = models.ManyToManyField(
        'Course',
        related_name='studentprofile_favorites',  # Unique reverse accessor
        blank=True
    )


    def __str__(self):
        return self.user.email  # Display user email in the profile representation
    
# InstructorProfile Model
class InstructorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Linking to the User model
    full_name = models.CharField(max_length=100, blank=True)
    username = models.CharField(max_length=50, unique=True, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True)
    location = models.CharField(max_length=100, blank=True)
    education = models.CharField(max_length=255, blank=True, null=True)
    about_me = models.TextField(blank=True)
    facebook_username = models.CharField(max_length=50, blank=True)
    twitter_username = models.CharField(max_length=50, blank=True)
    instagram_username = models.CharField(max_length=50, blank=True)
    youtube_url = models.URLField(max_length=200, blank=True)
    profile_image = models.ImageField(upload_to='instructors/profile_images/', null=True, blank=True)
    courses_created = models.IntegerField(default=0)  # Specific field for instructors
    expertise = models.CharField(max_length=255, blank=True)
    ratings = models.FloatField(default=0.0)
    email = models.EmailField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.user.email  # Display user email in the profile representation
    
# --- Signal to Create Profiles ---
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Create StudentProfile by default
        StudentProfile.objects.get_or_create(user=instance)
        # Optionally create InstructorProfile
        if instance.is_staff:  # Assuming staff users are instructors
            InstructorProfile.objects.get_or_create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        # Ensure that StudentProfile is created and saved
        student_profile, _ = StudentProfile.objects.get_or_create(user=instance)
        student_profile.save()

        # Ensure that InstructorProfile is created and saved for staff users
        if instance.is_staff:
            instructor_profile, _ = InstructorProfile.objects.get_or_create(user=instance)
            instructor_profile.save()
    except ObjectDoesNotExist:
        pass  # Fallback for unexpected edge cases

# InstructorClassCourse Model
class InstructorClassCourse(models.Model):
    COURSE_CATEGORY_CHOICES = [
        ('Engineer', 'Engineer'),
        ('Medical', 'Medical'),
        ('Information technology', 'Information technology'),
        ('Finance', 'Finance'),
        ('Marketing', 'Marketing'),
    ]

    COURSE_LEVEL_CHOICES = [
        ('All level', 'All level'),
        ('Beginner', 'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Advance', 'Advance'),
    ]

    LANGUAGE_CHOICES = [
        ('English', 'English'),
        ('German', 'German'),
        ('French', 'French'),
        ('Hindi', 'Hindi'),
    ]

    course_title = models.CharField(max_length=255)
    short_description = models.TextField()
    category = models.CharField(max_length=50, choices=COURSE_CATEGORY_CHOICES)
    level = models.CharField(max_length=50, choices=COURSE_LEVEL_CHOICES)
    languages = models.CharField(max_length=10, choices=LANGUAGE_CHOICES)
    is_featured = models.BooleanField(default=False)
    course_time = models.CharField(max_length=50)  # Could use DurationField for time duration
    total_lecture = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    description = models.TextField()  # Full description of the course
    image = models.ImageField(upload_to='course_images/', null=True, blank=True)  # Image upload
    video_url = models.URLField(null=True, blank=True)  # URL for video
    video_upload = models.FileField(upload_to='course_videos/', null=True, blank=True)  # Upload video
    

    def __str__(self):
        return self.course_title
    
# Course1 Model (Main Course Model)
class Course1(models.Model):  # Renamed to Course1
    COURSE_CATEGORY_CHOICES = [
        ('Engineer', 'Engineer'),
        ('Medical', 'Medical'),
        ('Information technology', 'Information technology'),
        ('Finance', 'Finance'),
        ('Marketing', 'Marketing'),
    ]

    COURSE_LEVEL_CHOICES = [
        ('All level', 'All level'),
        ('Beginner', 'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Advance', 'Advance'),
    ]
    LANGUAGE_CHOICES = [
        ('English', 'English'),
        ('German', 'German'),
        ('French', 'French'),
        ('Hindi', 'Hindi'),
    ]

    PENDING = 'Pending'
    LIVE = 'Live'
    REJECTED = 'Rejected'
    
    COURSE_STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (LIVE, 'Live'),
        (REJECTED, 'Rejected'),
    ]


    name = models.CharField(max_length=100)
    short_description = models.TextField()
    category = models.CharField(max_length=50, choices=COURSE_CATEGORY_CHOICES)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_courses')
    level = models.CharField(max_length=50, choices=COURSE_LEVEL_CHOICES,  default="Select")
    languages = models.CharField(max_length=10, choices=LANGUAGE_CHOICES)
    is_featured = models.BooleanField(default=False)
    course_time = models.CharField(max_length=50)
    total_lecture = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=5, decimal_places=2)
    description = models.TextField()
    image = models.ImageField(upload_to='courses/', null=True, blank=True)
    video_url = models.URLField(null=True, blank=True)
    video_upload = models.FileField(upload_to='course_videos/', null=True, blank=True)  # Upload video    
    tags = models.CharField(max_length=255, null=True, blank=True)
    message_to_reviewer = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)  # Add this field
    status = models.CharField(
        max_length=10,
        choices=COURSE_STATUS_CHOICES,
        default=PENDING,
    )


    def __str__(self):
        return self.name

class Lecture(models.Model):
    course = models.ForeignKey(Course1, related_name='lectures', on_delete=models.CASCADE)  # Updated foreign key
    title = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)  # Add this field

    def __str__(self):
        return self.title
    
class Topic(models.Model):
    lecture = models.ForeignKey(Lecture, related_name='topics', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    url = models.URLField(null=True, blank=True)
    video_file = models.FileField(upload_to='videos/', null=True, blank=True)
    description = models.TextField()
    is_free = models.BooleanField(default=True)
    premium = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)  # Add this field
    duration = models.PositiveIntegerField(null=True, blank=True)  # Duration in seconds

    def save(self, *args, **kwargs):
        # Calculate duration only for uploaded videos
        if self.video_file and not self.duration:
            video_path = self.video_file.path
            video = VideoFileClip(video_path)
            self.duration = int(video.duration)

        super().save(*args, **kwargs)

    def get_duration(self):
        if self.duration:
            minutes = self.duration // 60
            seconds = self.duration % 60
            return f"{minutes}m {seconds}s"
        return "N/A"

    def __str__(self):
        return self.name

class FAQ(models.Model):
    course = models.ForeignKey(Course1, related_name='faqs', on_delete=models.CASCADE)  # Updated foreign key
    question = models.CharField(max_length=200)
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)  # Add this field
    
    def __str__(self):
        return self.question

# --- Signal to Create or Save User Profiles ---
@receiver(post_save, sender=User)
def create_or_save_user_profile(sender, instance, created, **kwargs):
    if created:
        # Create StudentProfile by default
        StudentProfile.objects.get_or_create(user=instance)
        # Optionally create InstructorProfile for staff
        if instance.is_staff:
            InstructorProfile.objects.get_or_create(user=instance)
    else:
        # Ensure profiles are updated when user data changes
        instance.studentprofile.save()  # Save student profile
        if instance.is_staff:
            instance.instructorprofile.save()  # Save instructor profile if staff

# EnrolledCourse Model
class EnrolledCourse(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course1, on_delete=models.CASCADE)
    progress = models.IntegerField(default=0)
    completed_lectures = models.IntegerField(default=0)
    completed_topics = models.IntegerField(default=0)  # New field for completed topics
    date_enrolled = models.DateTimeField(auto_now_add=True)
    watch_time = models.PositiveIntegerField(default=0)  # Time in minutes
    price = models.DecimalField(max_digits=10, decimal_places=2)
  # Or use course.price if price is inherited
    status = models.CharField(max_length=20, choices=[ 
        ('in_progress', 'In Progress'), 
        ('completed', 'Completed') 
    ], default='in_progress')

    class Meta:
        unique_together = ['student', 'course']

    @property
    def progress_percentage(self):
        """
        Calculate the course completion progress.
        50% of the progress will be based on completed lectures
        and 50% on completed topics.
        """
        total_lectures = self.course.lectures.count()
        total_topics = sum(lecture.topics.count() for lecture in self.course.lectures.all())

        progress_lectures = (self.completed_lectures / total_lectures) * 50 if total_lectures else 0
        progress_topics = (self.completed_topics / total_topics) * 50 if total_topics else 0

        total_progress = progress_lectures + progress_topics
        return total_progress

    def update_progress(self):
        """
        Update the progress percentage based on completed lectures and topics.
        """
        self.progress = self.progress_percentage
        self.save()

    def complete_lecture(self, lecture):
        """
        Mark a lecture as completed and update progress.
        """
        if lecture in self.course.lectures.all() and self.completed_lectures < self.course.lectures.count():
            self.completed_lectures += 1
            self.save()
            self.update_progress()  # Update progress after marking the lecture as completed

    def complete_topic(self, topic):
        """
        Mark a topic as completed and update progress.
        """
        if topic in self.course.topics.all() and self.completed_topics < sum(lecture.topics.count() for lecture in self.course.lectures.all()):
            self.completed_topics += 1
            self.save()
            self.update_progress()  # Update progress after marking the topic as completed


# UserTopicProgress Model
class UserTopicProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.topic.name} - {'Completed' if self.completed else 'Incomplete'}"

# FavoriteCourse Model
class FavoriteCourse(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favorite_courses")
    course = models.ForeignKey(Course1, on_delete=models.CASCADE, related_name="favorited_by")
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.course.name}"

# Quiz Model
class Quiz(models.Model):
    question = models.CharField(max_length=255)
    option_1 = models.CharField(max_length=255)
    option_2 = models.CharField(max_length=255)
    option_3 = models.CharField(max_length=255)
    option_4 = models.CharField(max_length=255)
    correct_option = models.CharField(max_length=1, choices=[
        ('A', 'Option 1'),
        ('B', 'Option 2'),
        ('C', 'Option 3'),
        ('D', 'Option 4'),
    ])
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.question
