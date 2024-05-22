from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.
class CustomUser(AbstractUser):
    
    email=models.CharField(max_length=80,unique=True)
    profilepic=models.ImageField(upload_to='static/profile_pics',null=True)
    userfor=models.CharField(max_length=20,default='')
    token=models.CharField(default=False,max_length=256)
    def __str__(self):
        return self.username

class BetaUser(models.Model):
    user=models.OneToOneField(CustomUser,on_delete=models.CASCADE)
    state=models.CharField(max_length=40,default='')
    city=models.CharField(max_length=40,default='')
    job_status=models.CharField(max_length=20,default='')
    degree=models.CharField(max_length=30,default='')
    grad_year=models.CharField(max_length=5,default='')
    profile_updated=models.BooleanField(default=False)
    website=models.URLField(default='')
    phone=models.CharField(max_length=10,default='')
    birthday=models.CharField(max_length=20,null=True)
    def __str__(self):
        return self.user.username
class GammaUser(models.Model):
    user=models.OneToOneField(CustomUser,on_delete=models.CASCADE)
    dev=models.BooleanField(default=False)
    def __str__(self):
        return self.user.username

class Course(models.Model):
    COURSE_LEVELS = [
        ('Beginner', 'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Advanced', 'Advanced'),
        ('All Level', 'All level'),
    ]
    ratingChoices=[
        ('0',0),
        ('1',1),
        ('2',2),
        ('3',3),
        ('4',4),
        ('5',5)
        
    ]
    course_level=models.CharField(
        max_length=20,
        choices=COURSE_LEVELS,
        default='all',
    )
    course_createdon=models.DateTimeField(auto_now_add=True)
    video=models.FileField(upload_to='static/course_videos')
    course_category=models.CharField(max_length=200)
    course_name=models.CharField(max_length=200)
    course_instructor=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    course_description=models.TextField()
    course_rating=models.CharField(choices=ratingChoices ,default=5 ,max_length=3)
    course_price=models.FloatField(default=0)
    course_duration=models.CharField(max_length=30)
    course_image=models.ImageField(upload_to='static/course_images')
    lectures=models.IntegerField(default=0)
    

    def __str__(self):
        return self.course_name

class isPurchased(models.Model):
    course=models.ForeignKey(Course,on_delete=models.CASCADE)
    isbuyed=models.BooleanField(default=False)
    purchased_on=models.DateTimeField(auto_now_add=True)
    buyer=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    def __str__(self):
        return self.course.course_name

class Progress(models.Model):
    course=models.ForeignKey(Course,on_delete=models.CASCADE)
    user=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    completed_lectures=models.IntegerField(default=0)
    progress=models.IntegerField(default=0)
    certified=models.BooleanField(default=False)
    def __int__(self):
        return self.progress