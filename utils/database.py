# utils/database.py - COMPLETE FIXED VERSION
import csv
import os
import hashlib
from datetime import datetime, date
import pandas as pd
import numpy as np

# CSV file paths
STUDENTS_CSV = 'data/students.csv'
STAFF_CSV = 'data/staff.csv'
ATTENDANCE_CSV = 'data/attendance.csv'
OD_REQUESTS_CSV = 'data/od_requests.csv'
HOSTEL_PASS_CSV = 'data/hostel_pass.csv'
BUS_ATTENDANCE_CSV = 'data/bus_attendance.csv'
PASSWORD_RESETS_CSV = 'data/password_resets.c# utils/database.py - COMPLETE FIXED VERSION WITH VERIFICATION'
import csv
import os
import hashlib
from datetime import datetime, date
import pandas as pd
import numpy as np

# CSV file paths
STUDENTS_CSV = 'data/students.csv'
STAFF_CSV = 'data/staff.csv'
ATTENDANCE_CSV = 'data/attendance.csv'
OD_REQUESTS_CSV = 'data/od_requests.csv'
HOSTEL_PASS_CSV = 'data/hostel_pass.csv'
BUS_ATTENDANCE_CSV = 'data/bus_attendance.csv'
PASSWORD_RESETS_CSV = 'data/password_resets.csv'

def ensure_data_directory():
    """Ensure data directory exists"""
    os.makedirs('data', exist_ok=True)
    os.makedirs('static/uploads/student_faces', exist_ok=True)
    os.makedirs('static/uploads/od_proofs', exist_ok=True)


def init_csv_files():
    """Initialize CSV files with proper headers"""
    files_structure = {
        STUDENTS_CSV: ['user_id', 'name', 'email', 'parent_email', 'password', 'class', 'roll_no', 'department', 'semester', 'created_at'],
        STAFF_CSV: ['user_id', 'name', 'email', 'password', 'department', 'designation', 'created_at'],
        ATTENDANCE_CSV: ['student_id', 'date', 'time', 'status', 'subject', 'period', 'department', 'semester', 'class', 'marked_by', 'marked_at'],
        OD_REQUESTS_CSV: ['request_id', 'student_id', 'date', 'start_time', 'end_time', 'reason', 'od_type', 'supporting_doc',
                         'class', 'department', 'student_name', 'status', 'submitted_at', 'approved_by', 'approved_at', 'remarks'],
        HOSTEL_PASS_CSV: ['pass_id', 'student_id', 'out_date', 'out_time', 'in_date', 'in_time', 
                         'destination', 'reason', 'emergency_contact', 'status', 'created_at', 'approved_by'],
        BUS_ATTENDANCE_CSV: ['student_id', 'date', 'time', 'bus_number', 'route', 'status'],
        PASSWORD_RESETS_CSV: ['email', 'token', 'created_at', 'used']
    }
    
    ensure_data_directory()
    
    for file_path, headers in files_structure.items():
        if not os.path.exists(file_path):
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
            print(f"✅ Created {file_path}")

# Initialize files on import
init_csv_files()


def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()


def get_user_by_id(user_id, role='student'):
    """Get user details by ID"""
    file_path = STAFF_CSV if role in ['staff', 'admin'] else STUDENTS_CSV
    
    try:
        if not os.path.exists(file_path):
            print(f"❌ CSV file does not exist: {file_path}")
            return None
        
        df = pd.read_csv(file_path)
        user = df[df['user_id'] == user_id]
        
        if not user.empty:
            return user.iloc[0].to_dict()
        else:
            return None
            
    except Exception as e:
        print(f"❌ ERROR in get_user_by_id: {e}")
        return None


def check_duplicate_attendance(student_id, subject, period, date):
    """Check if attendance already marked"""
    try:
        if not os.path.exists(ATTENDANCE_CSV):
            return False
        
        df = pd.read_csv(ATTENDANCE_CSV)
        date_str = date.strftime('%Y-%m-%d') if hasattr(date, 'strftime') else str(date)
        
        duplicate = df[
            (df['student_id'] == student_id) & 
            (df['subject'] == subject) & 
            (df['period'] == str(period)) & 
            (df['date'] == date_str)
        ]
        
        if not duplicate.empty:
            print(f"⚠️ Duplicate attendance found for {student_id} - {subject} Period {period}")
            return True
            
        return False
        
    except Exception as e:
        print(f"❌ Error checking duplicate: {e}")
        return False


def mark_attendance(student_id, status, subject, period, department, semester, class_name='', marked_by='System'):
    """Mark attendance - FIXED VERSION WITH VERIFICATION"""
    try:
        ensure_data_directory()
        
        now = datetime.now()
        date_str = now.strftime('%Y-%m-%d')
        time_str = now.strftime('%H:%M:%S')
        marked_at = now.strftime('%Y-%m-%d %H:%M:%S')
        
        print(f"\n{'='*60}")
        print(f"📝 MARKING ATTENDANCE")
        print(f"{'='*60}")
        print(f"Student ID: {student_id}")
        print(f"Status: {status}")
        print(f"Subject: {subject}")
        print(f"Period: {period}")
        print(f"Department: {department}")
        print(f"Date: {date_str}")
        print(f"Time: {time_str}")
        
        # Check for duplicate
        if check_duplicate_attendance(student_id, subject, period, date_str):
            print(f"⚠️ Attendance already marked for {student_id}")
            print(f"{'='*60}\n")
            return True  # Return True but don't add duplicate
        
        # Get student info for class
        student = get_user_by_id(student_id, 'student')
        if student and not class_name:
            class_name = student.get('class', 'N/A')
        
        # Prepare attendance record
        attendance_record = [
            student_id,      # student_id
            date_str,        # date
            time_str,        # time
            status,          # status
            subject,         # subject
            str(period),     # period
            department,      # department
            str(semester),   # semester
            class_name,      # class
            marked_by,       # marked_by
            marked_at        # marked_at
        ]
        
        print(f"\n📋 Record to save: {attendance_record}")
        
        # Check if file exists and has correct headers
        file_exists = os.path.exists(ATTENDANCE_CSV)
        
        if not file_exists:
            print(f"⚠️ Creating new attendance CSV file...")
            with open(ATTENDANCE_CSV, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['student_id', 'date', 'time', 'status', 'subject', 'period', 
                               'department', 'semester', 'class', 'marked_by', 'marked_at'])
            print(f"✅ Created {ATTENDANCE_CSV} with headers")
        
        # Write to CSV with error handling
        try:
            with open(ATTENDANCE_CSV, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(attendance_record)
            
            print(f"✅ Successfully written to CSV")
            
            # VERIFICATION: Read back to confirm
            df = pd.read_csv(ATTENDANCE_CSV)
            last_row = df.iloc[-1]
            
            if (last_row['student_id'] == student_id and 
                last_row['subject'] == subject and 
                last_row['period'] == str(period)):
                print(f"✅ VERIFIED: Record confirmed in CSV")
                print(f"   Total records in CSV: {len(df)}")
                print(f"{'='*60}\n")
                return True
            else:
                print(f"❌ VERIFICATION FAILED: Record not found in CSV after write")
                print(f"{'='*60}\n")
                return False
                
        except PermissionError:
            print(f"❌ PERMISSION ERROR: Cannot write to {ATTENDANCE_CSV}")
            print(f"   Check file permissions!")
            print(f"{'='*60}\n")
            return False
        except Exception as write_error:
            print(f"❌ WRITE ERROR: {write_error}")
            import traceback
            traceback.print_exc()
            print(f"{'='*60}\n")
            return False
        
    except Exception as e:
        print(f"❌ ERROR in mark_attendance: {e}")
        import traceback
        traceback.print_exc()
        print(f"{'='*60}\n")
        return False


def get_attendance(student_id=None, date_filter=None):
    """Get attendance records"""
    try:
        if not os.path.exists(ATTENDANCE_CSV):
            print(f"⚠️ Attendance CSV not found: {ATTENDANCE_CSV}")
            return []
        
        df = pd.read_csv(ATTENDANCE_CSV)
        df = df.fillna('')
        
        # Apply filters
        if student_id:
            df = df[df['student_id'] == student_id]
        
        if date_filter:
            df = df[df['date'] == date_filter]
        
        print(f"📊 Retrieved {len(df)} attendance records")
        return df.to_dict('records')
        
    except Exception as e:
        print(f"❌ Error getting attendance: {e}")
        import traceback
        traceback.print_exc()
        return []


# Keep all other functions from your original database.py
# ... (rest of the functions remain the same)sv'

def ensure_data_directory():
    """Ensure data directory exists"""
    os.makedirs('data', exist_ok=True)
    os.makedirs('static/uploads/student_faces', exist_ok=True)
    os.makedirs('static/uploads/od_proofs', exist_ok=True)


def init_csv_files():
    """Initialize CSV files with proper headers"""
    files_structure = {
        STUDENTS_CSV: ['user_id', 'name', 'email', 'parent_email', 'password', 'class', 'roll_no', 'department', 'semester', 'created_at'],
        STAFF_CSV: ['user_id', 'name', 'email', 'password', 'department', 'designation', 'created_at'],
        ATTENDANCE_CSV: ['student_id', 'date', 'time', 'status', 'subject', 'period', 'department', 'semester', 'class', 'marked_by', 'marked_at'],
        OD_REQUESTS_CSV: ['request_id', 'student_id', 'date', 'start_time', 'end_time', 'reason', 'od_type', 'supporting_doc',
                         'class', 'department', 'status', 'submitted_at', 'approved_by', 'approved_at', 'remarks'],
        HOSTEL_PASS_CSV: ['pass_id', 'student_id', 'out_date', 'out_time', 'in_date', 'in_time', 
                         'destination', 'reason', 'emergency_contact', 'status', 'created_at', 'approved_by'],
        BUS_ATTENDANCE_CSV: ['student_id', 'date', 'time', 'bus_number', 'route', 'status'],
        PASSWORD_RESETS_CSV: ['email', 'token', 'created_at', 'used']
    }
    
    ensure_data_directory()
    
    for file_path, headers in files_structure.items():
        if not os.path.exists(file_path):
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
            print(f"✅ Created {file_path}")

# Initialize files on import
init_csv_files()


def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_user(user_id, password, role):
    """Verify user credentials"""
    file_path = STAFF_CSV if role in ['staff', 'admin'] else STUDENTS_CSV
    
    try:
        if not os.path.exists(file_path):
            return None
            
        df = pd.read_csv(file_path)
        user = df[df['user_id'] == user_id]
        
        if not user.empty:
            stored_password = str(user.iloc[0]['password'])
            
            # Try hashed password first
            hashed_password = hash_password(password)
            if stored_password == hashed_password:
                return user.iloc[0].to_dict()
            
            # Try plain text for demo accounts (backwards compatibility)
            if stored_password == password:
                return user.iloc[0].to_dict()
                
    except Exception as e:
        print(f"❌ Error verifying user: {e}")
    
    return None


def get_user_by_id(user_id, role='student'):
    """Get user details by ID"""
    file_path = STAFF_CSV if role in ['staff', 'admin'] else STUDENTS_CSV
    
    try:
        if not os.path.exists(file_path):
            print(f"❌ CSV file does not exist: {file_path}")
            return None
        
        df = pd.read_csv(file_path)
        user = df[df['user_id'] == user_id]
        
        if not user.empty:
            return user.iloc[0].to_dict()
        else:
            return None
            
    except Exception as e:
        print(f"❌ ERROR in get_user_by_id: {e}")
        return None


def get_user_by_email(email, role='student'):
    """Get user details by email"""
    file_path = STAFF_CSV if role in ['staff', 'admin'] else STUDENTS_CSV
    
    try:
        if not os.path.exists(file_path):
            return None
        
        df = pd.read_csv(file_path)
        user = df[df['email'] == email]
        
        if not user.empty:
            return user.iloc[0].to_dict()
    except Exception as e:
        print(f"Error getting user by email: {e}")
    
    return None


def update_password(email, new_password, role='student'):
    """Update user password"""
    file_path = STAFF_CSV if role in ['staff', 'admin'] else STUDENTS_CSV
    
    try:
        df = pd.read_csv(file_path)
        hashed_password = hash_password(new_password)
        
        df.loc[df['email'] == email, 'password'] = hashed_password
        df.to_csv(file_path, index=False)
        
        print(f"✅ Password updated for {email}")
        return True
        
    except Exception as e:
        print(f"❌ Error updating password: {e}")
        return False


def add_student(student_data):
    """Add new student"""
    try:
        ensure_data_directory()
        
        # Read existing students
        if os.path.exists(STUDENTS_CSV):
            df = pd.read_csv(STUDENTS_CSV)
            
            # Check if user already exists
            if student_data['user_id'] in df['user_id'].values:
                print(f"ℹ️ Student {student_data['user_id']} already exists")
                return True, "Student already exists"
            
            # Check if email already exists
            if student_data['email'] in df['email'].values:
                return False, "Email already registered"
        
        # Add new student
        with open(STUDENTS_CSV, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                student_data['user_id'],
                student_data['name'],
                student_data['email'],
                student_data.get('parent_email', ''),
                student_data['password'],
                student_data.get('class', ''),
                student_data.get('roll_no', ''),
                student_data.get('department', 'Computer Science'),
                student_data.get('semester', '3'),
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        print(f"✅ Student added: {student_data['user_id']}")
        return True, "Student added successfully"
        
    except Exception as e:
        print(f"❌ Error adding student: {e}")
        import traceback
        traceback.print_exc()
        return False, str(e)


def check_duplicate_attendance(student_id, subject, period, date):
    """Check if attendance already marked"""
    try:
        if not os.path.exists(ATTENDANCE_CSV):
            return False
        
        df = pd.read_csv(ATTENDANCE_CSV)
        date_str = date.strftime('%Y-%m-%d') if hasattr(date, 'strftime') else str(date)
        
        duplicate = df[
            (df['student_id'] == student_id) & 
            (df['subject'] == subject) & 
            (df['period'] == str(period)) & 
            (df['date'] == date_str)
        ]
        
        if not duplicate.empty:
            print(f"⚠️ Duplicate attendance found for {student_id} - {subject} Period {period}")
            return True
            
        return False
        
    except Exception as e:
        print(f"❌ Error checking duplicate: {e}")
        return False


def mark_attendance(student_id, status, subject, period, department, semester, class_name='', marked_by='System'):
    """Mark attendance - FIXED VERSION"""
    try:
        ensure_data_directory()
        
        now = datetime.now()
        date_str = now.strftime('%Y-%m-%d')
        time_str = now.strftime('%H:%M:%S')
        marked_at = now.strftime('%Y-%m-%d %H:%M:%S')
        
        # Check for duplicate
        if check_duplicate_attendance(student_id, subject, period, date_str):
            print(f"⚠️ Attendance already marked for {student_id}")
            return True  # Return True but don't add duplicate
        
        # Write to CSV
        with open(ATTENDANCE_CSV, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                student_id,
                date_str,
                time_str,
                status,
                subject,
                str(period),
                department,
                str(semester),
                class_name,
                marked_by,
                marked_at
            ])
        
        print(f"✅ Attendance marked: {student_id} - {status} - {subject} Period {period}")
        return True
        
    except Exception as e:
        print(f"❌ Error marking attendance: {e}")
        import traceback
        traceback.print_exc()
        return False


def get_attendance(student_id, detailed=False):
    """
    Get attendance for a student - FIXED VERSION WITH OD SUPPORT
    
    Args:
        student_id: Student's user ID
        detailed: If True, return detailed records. If False, return summary stats.
    
    Returns:
        If detailed=False: dict with keys: total, present, absent, percentage
        If detailed=True: list of attendance records
    """
    try:
        if not os.path.exists(ATTENDANCE_CSV):
            print(f"⚠️ Attendance file not found")
            if detailed:
                return []
            return {'total': 0, 'present': 0, 'absent': 0, 'percentage': 0}
        
        # Read attendance data
        df = pd.read_csv(ATTENDANCE_CSV)
        df = df.fillna('')
        
        # Filter by student ID
        student_df = df[df['student_id'] == student_id]
        
        if detailed:
            # Return detailed records as list of dicts
            return student_df.to_dict('records')
        else:
            # Return summary statistics - FIXED TO INCLUDE OD
            total = len(student_df)
            
            if total == 0:
                return {'total': 0, 'present': 0, 'absent': 0, 'percentage': 0}
            
            # Count present AND OD as present
            present = len(student_df[(student_df['status'] == 'present') | (student_df['status'] == 'od')])
            absent = len(student_df[student_df['status'] == 'absent'])
            percentage = round((present / total) * 100) if total > 0 else 0
            
            print(f"📊 Attendance for {student_id}: {present}/{total} = {percentage}%")
            
            return {
                'total': total,
                'present': present,
                'absent': absent,
                'percentage': percentage
            }
    
    except Exception as e:
        print(f"❌ Error getting attendance: {e}")
        import traceback
        traceback.print_exc()
        
        if detailed:
            return []
        return {'total': 0, 'present': 0, 'absent': 0, 'percentage': 0}


def get_student_attendance_summary(student_id):
    """
    Get attendance summary for a student with subject-wise breakdown - FIXED VERSION
    
    Returns:
        dict with overall and subject-wise attendance
    """
    try:
        if not os.path.exists(ATTENDANCE_CSV):
            return None
        
        df = pd.read_csv(ATTENDANCE_CSV)
        df = df.fillna('')
        
        # Filter by student
        student_df = df[df['student_id'] == student_id]
        
        if len(student_df) == 0:
            return None
        
        # Overall stats - FIXED TO INCLUDE OD
        total = len(student_df)
        present = len(student_df[(student_df['status'] == 'present') | (student_df['status'] == 'od')])
        absent = len(student_df[student_df['status'] == 'absent'])
        percentage = round((present / total) * 100, 2)
        
        # Subject-wise stats
        subject_wise = []
        subjects = student_df['subject'].unique()
        
        for subject in subjects:
            if not subject:
                continue
            
            subject_df = student_df[student_df['subject'] == subject]
            sub_total = len(subject_df)
            # Count present AND OD as present
            sub_present = len(subject_df[(subject_df['status'] == 'present') | (subject_df['status'] == 'od')])
            sub_absent = sub_total - sub_present
            sub_percentage = round((sub_present / sub_total) * 100, 2) if sub_total > 0 else 0
            
            subject_wise.append({
                'subject': subject,
                'total': sub_total,
                'present': sub_present,
                'absent': sub_absent,
                'percentage': sub_percentage
            })
        
        return {
            'overall': {
                'total': total,
                'present': present,
                'absent': absent,
                'percentage': percentage
            },
            'subject_wise': subject_wise
        }
    
    except Exception as e:
        print(f"❌ Error getting student attendance summary: {e}")
        import traceback
        traceback.print_exc()
        return None


def get_class_attendance(class_name, date=None):
    """Get attendance for a specific class"""
    try:
        if not os.path.exists(ATTENDANCE_CSV):
            return []
        
        df = pd.read_csv(ATTENDANCE_CSV)
        df = df.fillna('')
        
        # Filter by class
        class_df = df[df['class'] == class_name]
        
        # Filter by date if provided
        if date:
            date_str = date.strftime('%Y-%m-%d') if hasattr(date, 'strftime') else str(date)
            class_df = class_df[class_df['date'] == date_str]
        
        return class_df.to_dict('records')
    
    except Exception as e:
        print(f"❌ Error getting class attendance: {e}")
        return []


def get_department_attendance(department, date=None):
    """Get attendance for a department"""
    try:
        if not os.path.exists(ATTENDANCE_CSV):
            return []
        
        df = pd.read_csv(ATTENDANCE_CSV)
        df = df.fillna('')
        
        # Filter by department
        dept_df = df[df['department'] == department]
        
        # Filter by date if provided
        if date:
            date_str = date.strftime('%Y-%m-%d') if hasattr(date, 'strftime') else str(date)
            dept_df = dept_df[dept_df['date'] == date_str]
        
        return dept_df.to_dict('records')
    
    except Exception as e:
        print(f"❌ Error getting department attendance: {e}")
        return []


def generate_attendance_report(start_date, end_date, department=None, class_name=None):
    """
    Generate attendance report for a date range - FIXED VERSION
    
    Returns comprehensive attendance statistics
    """
    try:
        if not os.path.exists(ATTENDANCE_CSV) or not os.path.exists(STUDENTS_CSV):
            return None
        
        # Read data
        att_df = pd.read_csv(ATTENDANCE_CSV)
        att_df = att_df.fillna('')
        stu_df = pd.read_csv(STUDENTS_CSV)
        
        # Filter by date range
        att_df = att_df[(att_df['date'] >= start_date) & (att_df['date'] <= end_date)]
        
        # Apply filters
        if department:
            att_df = att_df[att_df['department'] == department]
            stu_df = stu_df[stu_df['department'] == department]
        
        if class_name:
            att_df = att_df[att_df['class'] == class_name]
            stu_df = stu_df[stu_df['class'] == class_name]
        
        # Calculate overall statistics - FIXED TO INCLUDE OD
        total_records = len(att_df)
        present_count = len(att_df[(att_df['status'] == 'present') | (att_df['status'] == 'od')])
        absent_count = len(att_df[att_df['status'] == 'absent'])
        avg_percentage = round((present_count / total_records * 100), 2) if total_records > 0 else 0
        
        # Per-student statistics
        student_data = []
        above_75 = 0
        below_75 = 0
        
        for _, student in stu_df.iterrows():
            student_id = student['user_id']
            student_att = att_df[att_df['student_id'] == student_id]
            
            if len(student_att) > 0:
                total = len(student_att)
                present = len(student_att[(student_att['status'] == 'present') | (student_att['status'] == 'od')])
                absent = total - present
                percentage = round((present / total) * 100, 2)
                
                if percentage >= 75:
                    above_75 += 1
                else:
                    below_75 += 1
                
                student_data.append({
                    'student_id': student_id,
                    'name': student['name'],
                    'class': student.get('class', 'N/A'),
                    'total': total,
                    'present': present,
                    'absent': absent,
                    'percentage': percentage
                })
        
        return {
            'summary': {
                'total_students': len(stu_df),
                'total_records': total_records,
                'present_count': present_count,
                'absent_count': absent_count,
                'avg_percentage': avg_percentage,
                'above_75': above_75,
                'below_75': below_75,
                'start_date': start_date,
                'end_date': end_date
            },
            'students': student_data
        }
    
    except Exception as e:
        print(f"❌ Error generating report: {e}")
        import traceback
        traceback.print_exc()
        return None


def submit_od_request(od_data):
    """Submit OD request - FIXED VERSION"""
    try:
        ensure_data_directory()
        
        request_id = f"OD_{int(datetime.now().timestamp())}"
        submitted_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        with open(OD_REQUESTS_CSV, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                request_id,
                od_data['student_id'],
                od_data['date'],
                od_data['start_time'],
                od_data['end_time'],
                od_data['reason'],
                od_data.get('od_type', 'other'),
                od_data.get('supporting_doc', ''),
                od_data.get('class', 'N/A'),
                od_data.get('department', 'N/A'),
                'pending',
                submitted_at,
                '',  # approved_by
                '',  # approved_at
                ''   # remarks
            ])

        print(f"✅ OD request submitted: {request_id}")
        return True

    except Exception as e:  
        print(f"❌ Error submitting OD: {e}")
        import traceback
        traceback.print_exc()
        return False


def get_od_requests(status=None, student_id=None):
    """Get OD requests from CSV - FIXED VERSION"""
    try:
        if not os.path.exists(OD_REQUESTS_CSV):
            return []

        df = pd.read_csv(OD_REQUESTS_CSV)
        df = df.fillna('')

        # Apply filters
        if status:
            df = df[df['status'] == status]
        
        if student_id:
            df = df[df['student_id'] == student_id]

        return df.to_dict('records')

    except Exception as e:
        print(f"❌ Error loading OD requests: {e}")
        import traceback
        traceback.print_exc()
        return []


def approve_od_request(request_id, staff_id, staff_name, remarks=''):
    """
    Approve an OD request and update attendance - FIXED VERSION
    
    When OD is approved:
    1. Update OD request status
    2. Mark attendance as 'od' for the approved period
    """
    try:
        if not os.path.exists(OD_REQUESTS_CSV):
            print(f"❌ OD requests file not found")
            return False
        
        # Load OD requests
        df = pd.read_csv(OD_REQUESTS_CSV)
        
        # Find the request
        mask = df['request_id'].astype(str) == str(request_id)
        
        if not mask.any():
            print(f"❌ Request {request_id} not found")
            return False
        
        # Get OD details
        od_request = df[mask].iloc[0]
        student_id = od_request['student_id']
        od_date = od_request['date']
        
        # Update OD status
        df.loc[mask, 'status'] = 'approved'
        df.loc[mask, 'approved_by'] = f"{staff_name} ({staff_id})"
        df.loc[mask, 'approved_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        df.loc[mask, 'remarks'] = remarks if remarks else 'Approved'
        
        # Save OD updates
        df.to_csv(OD_REQUESTS_CSV, index=False)
        
        # Mark attendance as OD for the period
        # You may need to adjust this based on your period structure
        try:
            # Get student info for department/class
            student = get_user_by_id(student_id, 'student')
            if student:
                # Mark OD attendance (you can customize periods based on start/end time)
                mark_attendance(
                    student_id=student_id,
                    status='od',
                    subject='On-Duty',
                    period='0',  # You may want to calculate actual periods
                    department=student.get('department', 'N/A'),
                    semester=student.get('semester', '0'),
                    class_name=student.get('class', 'N/A'),
                    marked_by=staff_name
                )
                print(f"✅ Attendance marked as OD for {student_id} on {od_date}")
        except Exception as att_error:
            print(f"⚠️ Warning: Could not mark attendance: {att_error}")
            # Don't fail the approval if attendance marking fails
        
        print(f"✅ OD request {request_id} approved by {staff_name}")
        return True
        
    except Exception as e:
        print(f"❌ Error approving OD request: {e}")
        import traceback
        traceback.print_exc()
        return False


def reject_od_request(request_id, staff_id, staff_name, remarks=''):
    """Reject an OD request - FIXED VERSION"""
    try:
        if not os.path.exists(OD_REQUESTS_CSV):
            print(f"❌ OD requests file not found")
            return False
        
        df = pd.read_csv(OD_REQUESTS_CSV)
        
        # Find the request
        mask = df['request_id'].astype(str) == str(request_id)
        
        if not mask.any():
            print(f"❌ Request {request_id} not found")
            return False
        
        # Update status
        df.loc[mask, 'status'] = 'rejected'
        df.loc[mask, 'approved_by'] = f"{staff_name} ({staff_id})"
        df.loc[mask, 'approved_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        df.loc[mask, 'remarks'] = remarks if remarks else 'Rejected'
        
        # Save
        df.to_csv(OD_REQUESTS_CSV, index=False)
        
        print(f"✅ OD request {request_id} rejected by {staff_name}")
        return True
        
    except Exception as e:
        print(f"❌ Error rejecting OD request: {e}")
        import traceback
        traceback.print_exc()
        return False


def submit_hostel_pass(pass_data):
    """Submit hostel pass request - FIXED VERSION"""
    try:
        ensure_data_directory()
        
        pass_id = f"HP_{int(datetime.now().timestamp())}"
        
        with open(HOSTEL_PASS_CSV, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                pass_id,
                pass_data['student_id'],
                pass_data['out_date'],
                pass_data['out_time'],
                pass_data['in_date'],
                pass_data['in_time'],
                pass_data.get('destination', ''),
                pass_data['reason'],
                pass_data.get('emergency_contact', ''),
                'pending',
                pass_data['created_at'],
                ''  # approved_by
            ])
        
        print(f"✅ Hostel pass submitted: {pass_id}")
        return True
        
    except Exception as e:
        print(f"❌ Error submitting hostel pass: {e}")
        import traceback
        traceback.print_exc()
        return False


def get_hostel_pass(student_id):
    """Get hostel passes for a student"""
    try:
        if not os.path.exists(HOSTEL_PASS_CSV):
            return []
            
        df = pd.read_csv(HOSTEL_PASS_CSV)
        df = df.fillna('')
        passes = df[df['student_id'] == student_id]
        
        return passes.to_dict('records')
        
    except Exception as e:
        print(f"❌ Error getting hostel passes: {e}")
        return []


def generate_bus_pass(student_id):
    """Generate QR code for bus pass"""
    try:
        import qrcode
        from io import BytesIO
        import base64
        
        # Get student info
        student = get_user_by_id(student_id, 'student')
        if not student:
            return None
        
        qr_data = f"BUS_PASS:{student_id}:{student.get('name', '')}:{datetime.now().strftime('%Y-%m-%d')}"
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
        
    except Exception as e:
        print(f"❌ Error generating bus pass: {e}")
        import traceback
        traceback.print_exc()
        return None


def mark_bus_attendance(student_id, timestamp):
    """Mark bus attendance when student boards"""
    try:
        ensure_data_directory()
        
        dt = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
        
        with open(BUS_ATTENDANCE_CSV, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                student_id,
                dt.strftime('%Y-%m-%d'),
                dt.strftime('%H:%M:%S'),
                'Unknown',
                'Unknown',
                'Boarded'
            ])
        
        print(f"✅ Bus attendance marked for {student_id}")
        return True
        
    except Exception as e:
        print(f"❌ Error marking bus attendance: {e}")
        return False