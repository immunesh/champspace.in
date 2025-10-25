import re
import os

# List of files to update
files = [
    'champapp/templates/champapp/course-grid.html',
    'champapp/templates/champapp/step1.html',
    'champapp/templates/champapp/step2.html',
    'champapp/templates/champapp/step3.html',
    'champapp/templates/champapp/step4.html',
    'champapp/templates/champapp/instructor/instructor-dashboard.html',
    'champapp/templates/champapp/instructor/instructor-edit-profile.html',
    'champapp/templates/champapp/instructor/instructor-manage-course.html',
    'champapp/templates/champapp/instructor/instructor-studentlist.html',
    'champapp/templates/champapp/instructor/instructor-quiz.html',
    'champapp/templates/champapp/student_dashboard/student-edit-profile.html',
    'champapp/templates/champapp/student_dashboard/student-bookmark.html',
    'champapp/templates/champapp/student_dashboard/student-mycourses.html',
    'champapp/templates/champapp/student_dashboard/student-delete-account.html',
    'champapp/templates/champapp/student_dashboard/student-dashboard.html',
    'champapp/templates/champapp/admin/course-detail-adv.html',
    'champapp/templates/champapp/admin/instructor-create-course.html'
]

for file_path in files:
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Pattern to match the entire Pages dropdown section
        pattern = r'<!-- Nav item 3 Pages -->.*?</li>\s*\n\s*<!-- Nav item 3 Account -->'
        replacement = '<!-- Nav item 3 Account -->'
        
        new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        
        if new_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f'Updated: {file_path}')
        else:
            print(f'No changes needed: {file_path}')
    else:
        print(f'File not found: {file_path}')

print('\nAll files processed!')
