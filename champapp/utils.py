def get_instructor_details(course):
    instructor_profile = course.instructor.instructorprofile
    full_name = instructor_profile.full_name
    profile_image = instructor_profile.profile_image.url if instructor_profile.profile_image else None
    return full_name, profile_image
