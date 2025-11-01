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

    class Meta:
        verbose_name = "Course"
        verbose_name_plural = "All Courses"

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


############################## AD REVENUE MODELS ##############################

class AdImpression(models.Model):
    """
    Tracks each ad view/impression during course watching
    Similar to how YouTube tracks ad views
    """
    PLATFORM_CHOICES = [
        ('google_adsense', 'Google AdSense'),
        ('facebook_ads', 'Facebook Audience Network'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ad_impressions')
    course = models.ForeignKey('Course1', on_delete=models.CASCADE, related_name='ad_impressions')
    lecture = models.ForeignKey('Lecture', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Ad details
    ad_platform = models.CharField(max_length=50, choices=PLATFORM_CHOICES, default='google_adsense')
    ad_unit_id = models.CharField(max_length=100, blank=True)  # AdSense unit ID
    
    # Revenue data
    estimated_revenue = models.DecimalField(max_digits=10, decimal_places=4, default=0.0000)  # Revenue per impression
    cpm_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Cost per 1000 impressions
    
    # Tracking
    viewed_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Quality metrics
    is_valid = models.BooleanField(default=True)  # Filter out invalid/bot clicks
    view_duration = models.IntegerField(default=0)  # Seconds ad was visible
    
    class Meta:
        ordering = ['-viewed_at']
        indexes = [
            models.Index(fields=['-viewed_at']),
            models.Index(fields=['user', 'course']),
        ]
    
    def __str__(self):
        return f"{self.ad_platform} - {self.user.username} - ₹{self.estimated_revenue}"


class AdRevenue(models.Model):
    """
    Daily aggregated ad revenue for platform
    Syncs with Google AdSense and Facebook Ads API
    """
    date = models.DateField(unique=True)
    
    # Platform-wise revenue
    google_adsense_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    facebook_ads_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    # Metrics
    total_impressions = models.IntegerField(default=0)
    total_clicks = models.IntegerField(default=0)
    average_cpm = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Sync status
    is_synced = models.BooleanField(default=False)
    last_synced_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date']
        verbose_name_plural = "Ad Revenues"
    
    def __str__(self):
        return f"{self.date} - ₹{self.total_revenue}"


class Earning(models.Model):
    """
    Tracks earnings for both students and instructors from ad revenue
    """
    EARNING_TYPE_CHOICES = [
        ('student_watch', 'Student Watch Time'),
        ('instructor_course', 'Instructor Course Content'),
        ('referral_bonus', 'Referral Bonus'),
        ('completion_bonus', 'Course Completion Bonus'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('paid', 'Paid'),
        ('rejected', 'Rejected'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='earnings')
    course = models.ForeignKey('Course1', on_delete=models.CASCADE, related_name='earnings')
    
    # Earning details
    earning_type = models.CharField(max_length=50, choices=EARNING_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    
    # Ad impression reference (if applicable)
    ad_impressions = models.ManyToManyField(AdImpression, blank=True, related_name='earnings')
    
    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    earned_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    
    # Related withdrawal (when paid)
    withdrawal = models.ForeignKey('Withdrawal', on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-earned_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['-earned_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.earning_type} - ₹{self.amount}"


class UserWallet(models.Model):
    """
    Virtual wallet for each user to track their balance
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wallet')
    
    # Balance tracking
    total_earned = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    available_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    pending_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    withdrawn_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    # Statistics
    total_watch_time = models.IntegerField(default=0)  # Minutes
    total_courses_watched = models.IntegerField(default=0)
    total_ad_impressions = models.IntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "User Wallet"
        verbose_name_plural = "User Wallets"
    
    def __str__(self):
        return f"{self.user.username} - Balance: ₹{self.available_balance}"
    
    def update_balance(self):
        """Recalculate balance from approved earnings"""
        from django.db.models import Sum
        
        # Calculate total approved earnings
        approved_earnings = self.user.earnings.filter(status='approved', paid_at__isnull=True).aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        # Calculate pending earnings
        pending_earnings = self.user.earnings.filter(status='pending').aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        # Calculate withdrawn amount
        withdrawn = self.user.earnings.filter(status='paid').aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        self.available_balance = approved_earnings
        self.pending_balance = pending_earnings
        self.withdrawn_amount = withdrawn
        self.total_earned = approved_earnings + pending_earnings + withdrawn
        self.save()


class Withdrawal(models.Model):
    """
    Withdrawal requests from users
    """
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('bank_transfer', 'Bank Transfer'),
        ('upi', 'UPI'),
        ('paytm', 'Paytm'),
        ('paypal', 'PayPal'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='withdrawals')
    
    # Amount details
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    processing_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    net_amount = models.DecimalField(max_digits=10, decimal_places=2)  # After fee
    
    # Payment details
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES)
    bank_name = models.CharField(max_length=100, blank=True)
    account_number = models.CharField(max_length=50, blank=True)
    ifsc_code = models.CharField(max_length=20, blank=True)
    upi_id = models.CharField(max_length=100, blank=True)
    
    # Status and tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=100, blank=True)  # Bank/UPI transaction ID
    
    # Notes
    user_notes = models.TextField(blank=True)
    admin_notes = models.TextField(blank=True)
    rejection_reason = models.TextField(blank=True)
    
    # Timestamps
    requested_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Processed by admin
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='processed_withdrawals')
    
    class Meta:
        ordering = ['-requested_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['-requested_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - ₹{self.amount} - {self.status}"
    
    def save(self, *args, **kwargs):
        # Calculate net amount after processing fee
        if not self.net_amount:
            self.net_amount = self.amount - self.processing_fee
        super().save(*args, **kwargs)


class RevenueShare(models.Model):
    """
    Defines revenue sharing percentages
    Can be customized per course or globally
    """
    # Revenue split configuration
    student_share_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=90.00)  # 90% to students
    instructor_share_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=10.00)  # 10% to instructors
    platform_share_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)  # 0% platform fee
    
    # Optional: Per-course basis
    course = models.OneToOneField('Course1', on_delete=models.CASCADE, null=True, blank=True, related_name='revenue_share')
    
    # Default configuration
    is_default = models.BooleanField(default=False)
    
    # Earnings calculation rules
    minimum_watch_time = models.IntegerField(default=5)  # Minimum minutes to earn
    earnings_per_minute = models.DecimalField(max_digits=10, decimal_places=4, default=0.5000)  # ₹0.50 per minute
    completion_bonus = models.DecimalField(max_digits=10, decimal_places=2, default=100.00)  # ₹100 on completion
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Revenue Share Configuration"
        verbose_name_plural = "Revenue Share Configurations"
    
    def __str__(self):
        if self.course:
            return f"Revenue Share for {self.course.name}"
        return "Default Revenue Share"
    
    def clean(self):
        """Validate that percentages add up to 100"""
        total = self.student_share_percentage + self.instructor_share_percentage + self.platform_share_percentage
        if total != 100:
            from django.core.exceptions import ValidationError
            raise ValidationError(f"Revenue shares must add up to 100%. Currently: {total}%")

