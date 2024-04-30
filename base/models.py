from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.
class CustomUser(AbstractUser):
    profilepic=models.ImageField(upload_to='static/profile_pics',null=True)
    def __str__(self):
        return self.username

class BetaUser(models.Model):
    user=models.OneToOneField(CustomUser,on_delete=models.CASCADE)
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
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('all', 'All level'),
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
    course_category=models.CharField(max_length=200)
    course_name=models.CharField(max_length=200)
    course_instructor=models.ForeignKey('CustomUser',on_delete=models.CASCADE)
    purchased=models.ManyToManyField(CustomUser,related_name='purchased',blank=True)
    course_description=models.TextField()
    course_rating=models.CharField(choices=ratingChoices ,default=0 ,max_length=3)
    course_price=models.FloatField(default=0)
    course_duration=models.CharField(max_length=30)
    course_image=models.ImageField(upload_to='static/course_images')
    

    def __str__(self):
        return self.course_name

class isPurchased(models.Model):
    course=models.ForeignKey(Course,on_delete=models.CASCADE)
    isbuyed=models.BooleanField(default=False)
    purchased_on=models.DateTimeField(auto_created=True)
    buyer=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    def __str__(self):
        return self.course.course_name

