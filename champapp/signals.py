# champapp/signals.py
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.utils import timezone
from champapp.models import (
    InstructorProfile, UserWallet, AdImpression, 
    Earning, RevenueShare, EnrolledCourse
)

@receiver(post_save, sender=User)
def create_instructor_profile(sender, instance, created, **kwargs):
    if created and instance.is_staff:
        InstructorProfile.objects.get_or_create(user=instance)


@receiver(post_save, sender=User)
def create_user_wallet(sender, instance, created, **kwargs):
    """Auto-create wallet for every new user"""
    if created:
        UserWallet.objects.get_or_create(user=instance)


@receiver(post_save, sender=AdImpression)
def calculate_ad_earning(sender, instance, created, **kwargs):
    """
    Automatically calculate and create earnings when ad impression is logged
    Revenue is split between student (watching) and instructor (course creator)
    """
    if created and instance.is_valid:
        # Get revenue share configuration
        try:
            if instance.course.revenue_share:
                revenue_share = instance.course.revenue_share
            else:
                revenue_share = RevenueShare.objects.get(is_default=True)
        except RevenueShare.DoesNotExist:
            # Create default revenue share if doesn't exist
            revenue_share = RevenueShare.objects.create(
                is_default=True,
                student_share_percentage=90.00,
                instructor_share_percentage=10.00,
                platform_share_percentage=0.00,
                earnings_per_minute=0.50,
                completion_bonus=100.00
            )
        
        # Calculate earnings for student (watcher)
        student_earning_amount = (instance.estimated_revenue * revenue_share.student_share_percentage) / 100
        
        # Create student earning
        student_earning = Earning.objects.create(
            user=instance.user,
            course=instance.course,
            earning_type='student_watch',
            amount=student_earning_amount,
            description=f"Ad revenue from watching {instance.course.name}",
            status='approved'  # Auto-approve ad earnings
        )
        student_earning.ad_impressions.add(instance)
        
        # Calculate earnings for instructor (course creator)
        instructor_earning_amount = (instance.estimated_revenue * revenue_share.instructor_share_percentage) / 100
        
        # Create instructor earning
        if instance.course.creator:
            instructor_earning = Earning.objects.create(
                user=instance.course.creator,
                course=instance.course,
                earning_type='instructor_course',
                amount=instructor_earning_amount,
                description=f"Ad revenue from course {instance.course.name}",
                status='approved'  # Auto-approve ad earnings
            )
            instructor_earning.ad_impressions.add(instance)
            
            # Update instructor wallet
            instructor_wallet, _ = UserWallet.objects.get_or_create(user=instance.course.creator)
            instructor_wallet.update_balance()
        
        # Update student wallet
        student_wallet, _ = UserWallet.objects.get_or_create(user=instance.user)
        student_wallet.total_ad_impressions += 1
        student_wallet.update_balance()
        student_wallet.save()


@receiver(post_save, sender=EnrolledCourse)
def handle_course_completion_bonus(sender, instance, created, **kwargs):
    """
    Award completion bonus when student completes a course
    """
    if not created and instance.status == 'completed':
        # Check if bonus already awarded
        existing_bonus = Earning.objects.filter(
            user=instance.student,
            course=instance.course,
            earning_type='completion_bonus'
        ).exists()
        
        if not existing_bonus:
            # Get revenue share config
            try:
                if instance.course.revenue_share:
                    revenue_share = instance.course.revenue_share
                else:
                    revenue_share = RevenueShare.objects.get(is_default=True)
            except RevenueShare.DoesNotExist:
                revenue_share = RevenueShare.objects.create(
                    is_default=True,
                    completion_bonus=100.00
                )
            
            # Award completion bonus
            Earning.objects.create(
                user=instance.student,
                course=instance.course,
                earning_type='completion_bonus',
                amount=revenue_share.completion_bonus,
                description=f"Course completion bonus for {instance.course.name}",
                status='approved'
            )
            
            # Update wallet
            wallet, _ = UserWallet.objects.get_or_create(user=instance.student)
            wallet.total_courses_watched += 1
            wallet.update_balance()
            wallet.save()


@receiver(post_save, sender=Earning)
def update_wallet_on_earning(sender, instance, created, **kwargs):
    """
    Update user wallet when new earning is created or status changes
    """
    if instance.user:
        wallet, _ = UserWallet.objects.get_or_create(user=instance.user)
        wallet.update_balance()

