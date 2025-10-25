from django.urls import path
from . import views
from django.shortcuts import redirect
from django.contrib.auth.views import LogoutView
from champapp.views import user_dashboard
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from .views import role_based_redirect
from .views import instructor_dashboard
from .views import admin_student_list
from .views import course_list_view
from champapp.views import course_list_view, delete_course_view, course_detail_adv
from champapp.views import edit_quiz, instructor_quiz
from .views import create_payment, verify_payment
from .views import get_course_content
from .views import add_to_cart, cart_detail, create_payment_from_cart, verify_payment




urlpatterns = [
    path('cart/', cart_detail, name='cart_detail'),
    path('cart/add/<int:course_id>/', add_to_cart, name='add_to_cart'),
    path('cart/checkout/', create_payment_from_cart, name='create_payment_from_cart'),
    path('verify-payment/', verify_payment, name='verify_payment'),
    path('', views.home, name='index'),
    path('how-it-works/', views.how_it_works, name='how_it_works'),
    path('join-now/', views.join_now, name='join_now'),
    path('403/', views.custom_403_view, name='403'),
    path('sign-up/', views.sign_up, name='sign-up'),
    path('sign-in/', views.sign_in, name='sign-in'),  
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('forgot-password/', views.forgot_password, name='forgot-password'),
    path('admin-dashboard/', lambda request: redirect('admin-dashboard', permanent=True)),
    path('dashboard/admin-dashboard/', views.admin_dashboard, name='admin-dashboard'),
    path('dashboard/all-courses/', views.all_courses, name='all-courses'),
    path('student/edit-profile/', views.edit_profile, name='edit_profile'),
    path('dashboard/all-courses/admin-course-category.html', views.admin_course_category, name='admin_course_category'),
    #############################testttttttttttttttt##############
    path('dashboard/class-course-preview/', views.class_course_preview, name='class-course-preview'),    
    path('course-detail-adv/<int:pk>/', views.course_detail_adv, name='course_detail_adv'),
    path('role-based-redirect/', role_based_redirect, name='role_based_redirect'),
    path('instructor/dashboard/', instructor_dashboard, name='instructor_dashboard'),
    path('student/edit-profile/', views.edit_instructor_profile, name='edit_profile'),
    path('custom-admin/student-list/', admin_student_list, name='admin-student-list'),
    ###############course1#####################
    path('create_course/step1/', views.create_course_step1, name='step_1'),
    path('create_course/step1/<int:course_id>/', views.create_course_step1, name='step_1'),
    path('create_course/step2/<int:course_id>/', views.create_course_step2, name='step_2'),
    path('create_course/step3/<int:course_id>/', views.create_course_step3, name='step_3'),
    path('create_course/step4/<int:course_id>/', views.create_course_step4, name='step_4'),
    path('base/', views.base_view, name='base'),
    path('courses/', course_list_view, name='course_list'),
    path('courses/<int:pk>/', views.course_detail_adv, name='course_detail'),  # Use the correct view and name
    path('delete_course/<int:course_id>/', views.delete_course_view, name='delete_course'),
    path('approve/<int:course_id>/', views.approve_course, name='approve_course'),
    path('reject/<int:course_id>/', views.reject_course, name='reject_course'),
    path('unlive/<int:course_id>/', views.unlive_course, name='unlive_course'),
    path('add-to-cart/<int:course_id>/', views.add_to_cart, name='add_to_cart'),
    path('dashboard/', views.user_dashboard, name='student-dashboard'),
    path('dashboard/my-earnings/', views.my_earnings, name='my_earnings'),
    path('dashboard/withdraw-funds/', views.withdraw_funds, name='withdraw_funds'),
    path('dashboard/revenue-stats/', views.revenue_stats, name='revenue_stats'),
    path('dashboard/certificates/', views.certificates, name='certificates'),
    path('dashboard/settings/', views.student_settings, name='student_settings'),
    path('courses/<int:course_id>/buy/', views.buy_now, name='buy_now'),
    path('courses/<int:course_id>/add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('student/bookmarks/', views.student_bookmark, name='student_bookmarks'),
    path('toggle-favorite/<int:course_id>/', views.toggle_favorite, name='toggle_favorite'),
    path("student/mycourses/", views.student_mycourses, name="student_mycourses"),
    path('student/delete-account/', views.student_delete_account, name='student_delete_account'),
    path('instructor/manage-course/', views.instructor_manage_course, name='instructor_manage_course'),
    path('instructor/quiz/', views.instructor_quiz, name='instructor_quiz'),
    path('quiz/edit/<int:quiz_id>/', views.edit_quiz, name='edit_quiz'),
    path('course-grid/', views.course_grid, name='course_grid'),
    path('dashboard/admin-instructor-requests/', views.admin_instructor_request, name='admin_instructor_request'),
    path('management/instructor-list/', views.admin_instructor_list, name='admin_instructor_list'),
    path('course/<int:course_id>/', views.course_complete, name='course_complete'),
    path('instructor/student-list/', views.instructor_student_list, name='instructor-student-list'),
    path('course-details/<int:course_id>/', views.course_details, name='course_details'),
    path('get-course-content/<int:course_id>/', get_course_content, name='get_course_content'),

    path('courses/<int:course_id>/pay/', create_payment, name='create_payment'),
    path('verify-payment/', verify_payment, name='verify_payment'),


] 

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


    