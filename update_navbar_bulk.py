import os
import re

# Base directory
BASE_DIR = r"c:\Users\mukushwa\OneDrive - Capgemini\Documents\Projects\champspace\champapp\templates\champapp"

# Files to update
files_to_update = [
    "step1.html",
    "step2.html",
    "step3.html",
    "step4.html",
    "instructor/instructor-dashboard.html",
    "instructor/instructor-edit-profile.html",
    "instructor/instructor-manage-course.html",
    "instructor/instructor-quiz.html",
    "instructor/instructor-studentlist.html",
    "student_dashboard/student-dashboard.html",
    "student_dashboard/student-edit-profile.html",
    "student_dashboard/student-bookmark.html",
    "student_dashboard/student-mycourses.html",
    "student_dashboard/student-delete-account.html",
    "admin/course-detail-adv.html",
    "admin/instructor-create-course.html",
]

# Pattern 1: Replace Demos dropdown with Home link
demos_pattern = r'<!-- Nav item 1 Demos -->\s*<li class="nav-item dropdown">\s*<a class="nav-link dropdown-toggle[^"]*" href="#" id="demoMenu"[^>]*>Demos</a>\s*<ul class="dropdown-menu"[^>]*>\s*<li>\s*<a class="dropdown-item[^"]*" href="{% url \'index\' %}">Home Default</a></li>\s*</ul>\s*</li>'
demos_replacement = '''<!-- Nav item 1 Home -->
                        <li class="nav-item">
                            <a class="nav-link" href="{% url 'index' %}">Home</a>
                        </li>'''

# Pattern 2: Simplify Accounts dropdown (remove Instructor/Student dropdowns, keep only Admin)
accounts_pattern = r'(<!-- Nav item 3 Account -->.*?<a class="nav-link dropdown-toggle"[^>]*>Accounts</a>\s*<ul class="dropdown-menu"[^>]*>).*?(<li>\s*<a class="dropdown-item" href="[^"]*"><i class="fas fa-user-cog[^>]*>Admin</a>\s*</li>).*?(</ul>\s*</li>)'

accounts_replacement = r'\1\n                                    \2\n                                \3'

def update_file(filepath):
    """Update a single file with navbar changes"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Replace Demos with Home
        content = re.sub(demos_pattern, demos_replacement, content, flags=re.DOTALL)
        
        # Simplify Accounts dropdown
        content = re.sub(accounts_pattern, accounts_replacement, content, flags=re.DOTALL)
        
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ Updated: {filepath}")
            return True
        else:
            print(f"✗ No changes needed: {filepath}")
            return False
            
    except Exception as e:
        print(f"✗ Error updating {filepath}: {str(e)}")
        return False

def main():
    """Main function to update all files"""
    print("Starting navbar updates across all template files...\n")
    
    updated_count = 0
    for file_path in files_to_update:
        full_path = os.path.join(BASE_DIR, file_path)
        if os.path.exists(full_path):
            if update_file(full_path):
                updated_count += 1
        else:
            print(f"✗ File not found: {full_path}")
    
    print(f"\n{'='*60}")
    print(f"Update complete! {updated_count} files updated successfully.")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
