# auto_attendance_scheduler.py - AUTOMATIC ATTENDANCE SYSTEM
"""
This scheduler automatically:
1. Checks every 1 minute if any class has started
2. Marks students absent if they haven't marked attendance within 5 minutes
3. Sends email to parents when student is marked absent
4. Updates CSV file with attendance records
"""

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, time, timedelta, date
import pandas as pd
import os
import csv
from flask import current_app

# Import your existing modules
from utils.database import get_user_by_id, STUDENTS_CSV, ATTENDANCE_CSV
from utils.email_service import send_email

# ==================== CONFIGURATION ====================
ATTENDANCE_WINDOW_MINUTES = 5  # Students must mark within 5 minutes
CHECK_INTERVAL_SECONDS = 60  # Check every 1 minute

# ==================== CLASS SCHEDULE ====================
CLASS_SCHEDULE = {
    'Computer Science': {
        'Monday': [
            {'period': 1, 'start': time(9, 0), 'end': time(10, 00), 'subject': 'Data Structures', 'semester': 3},
            {'period': 2, 'start': time(10, 0), 'end': time(10, 50), 'subject': 'Operating Systems', 'semester': 3},
            {'period': 3, 'start': time(11, 0), 'end': time(11, 50), 'subject': 'Database Management', 'semester': 3},
            {'period': 4, 'start': time(12, 0), 'end': time(12, 50), 'subject': 'Computer Networks', 'semester': 3},
            {'period': 5, 'start': time(14, 0), 'end': time(14, 50), 'subject': 'Algorithm Lab', 'semester': 3},
            {'period': 6, 'start': time(15, 0), 'end': time(15, 50), 'subject': 'Web Development', 'semester': 3},
            {'period': 7, 'start': time(16, 0), 'end': time(16, 50), 'subject': 'Python Programming', 'semester': 3},
        ],
        'Tuesday': [
            {'period': 1, 'start': time(9, 0), 'end': time(9, 50), 'subject': 'Software Engineering', 'semester': 3},
            {'period': 2, 'start': time(10, 0), 'end': time(10, 50), 'subject': 'Web Technologies', 'semester': 3},
            {'period': 3, 'start': time(11, 0), 'end': time(11, 50), 'subject': 'Data Structures', 'semester': 3},
            {'period': 4, 'start': time(12, 0), 'end': time(12, 50), 'subject': 'Computer Networks', 'semester': 3},
            {'period': 5, 'start': time(14, 0), 'end': time(14, 50), 'subject': 'DBMS Lab', 'semester': 3},
        ],
        'Wednesday': [
            {'period': 1, 'start': time(9, 0), 'end': time(9, 50), 'subject': 'AI', 'semester': 3},  
            {'period': 2, 'start': time(10, 0), 'end': time(10, 50), 'subject': 'Operating Systems', 'semester': 3},
            {'period': 3, 'start': time(11, 00), 'end': time(11, 50), 'subject': 'Computer Networks', 'semester': 3},
            {'period': 4, 'start': time(13, 0), 'end': time(13, 50), 'subject': 'Software Engineering', 'semester': 3},
        ],
        'Thursday': [
            {'period': 1, 'start': time(9, 0), 'end': time(9, 50), 'subject': 'Machine Learning', 'semester': 3},
            {'period': 2, 'start': time(10, 0), 'end': time(10, 50), 'subject': 'Database Management', 'semester': 3},
            {'period': 3, 'start': time(11, 0), 'end': time(11, 50), 'subject': 'Software Testing', 'semester': 3},
            {'period': 4, 'start': time(13, 0), 'end': time(13, 50), 'subject': 'Software Engineering', 'semester': 3},
        ],
        'Friday': [
            {'period': 1, 'start': time(9, 0), 'end': time(9, 50), 'subject': 'Cloud Computing', 'semester': 3},
            {'period': 2, 'start': time(10, 0), 'end': time(10, 50), 'subject': 'AI', 'semester': 3},
            {'period': 3, 'start': time(11, 0), 'end': time(11, 50), 'subject': 'Cryptography', 'semester': 3},
            {'period': 4, 'start': time(12, 0), 'end': time(12, 50), 'subject': 'Computer Graphics', 'semester': 3},
        ],
        'Saturday': [
            {'period': 1, 'start': time(9, 0), 'end': time(9, 50), 'subject': 'Project Work', 'semester': 3},
             {'period': 2, 'start': time(10, 0), 'end': time(10, 50), 'subject': 'Seminar', 'semester': 3},
        ],
        'Sunday': [
              {'period': 1, 'start': time(16, 21), 'end': time(16, 50), 'subject': 'Seminar', 'semester': 3}
        ]
    },
    'Electrical Engineering': {
        'Monday': [
            {'period': 1, 'start': time(16, 0), 'end': time(17, 00), 'subject': 'Analog Circuits', 'semester': 3},
            {'period': 2, 'start': time(10, 0), 'end': time(10, 50), 'subject': 'Digital Electronics', 'semester': 3},
            {'period': 3, 'start': time(11, 0), 'end': time(11, 50), 'subject': 'Signals & Systems', 'semester': 3},
            {'period': 4, 'start': time(12, 0), 'end': time(12, 50), 'subject': 'Network Analysis', 'semester': 3},
            {'period': 5, 'start': time(13, 0), 'end': time(14, 50), 'subject': 'Digital Logic', 'semester': 3},
            {'period': 6, 'start': time(15, 0), 'end': time(15, 50), 'subject': 'Programming', 'semester': 3},
            {'period': 7, 'start': time(16, 0), 'end': time(16, 50), 'subject': 'Miocrowave', 'semester': 3},
        ],
        'Tuesday': [
            {'period': 1, 'start': time(9, 0), 'end': time(9, 50), 'subject': 'Analog Circuits', 'semester': 3},
            {'period': 2, 'start': time(10, 0), 'end': time(10, 50), 'subject': 'Digital Logic', 'semester': 3},
            {'period': 3, 'start': time(11, 0), 'end': time(11, 50), 'subject': 'Embedded System', 'semester': 3},
            {'period': 4, 'start': time(12, 0), 'end': time(12, 50), 'subject': 'Computer Networks', 'semester': 3},
            {'period': 5, 'start': time(14, 0), 'end': time(14, 50), 'subject': 'Programming', 'semester': 3},
        ],
        'Wednesday': [
            {'period': 1, 'start': time(9, 0), 'end': time(9, 50), 'subject': 'Aptitude', 'semester': 3},  
            {'period': 2, 'start': time(10, 0), 'end': time(10, 50), 'subject': 'Operating Systems', 'semester': 3},
            {'period': 3, 'start': time(11, 0), 'end': time(11, 50), 'subject': 'Signals & System', 'semester': 3},
            {'period': 4, 'start': time(12, 0), 'end': time(12, 50), 'subject': 'Miocrowave', 'semester': 3},
        ],
        'Thursday': [
            {'period': 1, 'start': time(9, 0), 'end': time(9, 50), 'subject': 'Library', 'semester': 3},
            {'period': 2, 'start': time(10, 0), 'end': time(10, 50), 'subject': 'Analog Circuits', 'semester': 3},
            {'period': 3, 'start': time(11, 0), 'end': time(11, 50), 'subject': 'Hardware Testing', 'semester': 3},
            {'period': 4, 'start': time(12, 0), 'end': time(12, 50), 'subject': 'PCB Design', 'semester': 3},
        ],
        'Friday': [
            {'period': 1, 'start': time(9, 0), 'end': time(9, 50), 'subject': 'Embedded System', 'semester': 3},
            {'period': 2, 'start': time(10, 0), 'end': time(10, 50), 'subject': 'Digital Logic', 'semester': 3},
            {'period': 3, 'start': time(11, 0), 'end': time(11, 50), 'subject': 'Libraray', 'semester': 3},
            {'period': 4, 'start': time(12, 0), 'end': time(12, 50), 'subject': 'Computer Graphics', 'semester': 3},
        ],
        'Saturday': [
            {'period': 1, 'start': time(9, 0), 'end': time(9, 50), 'subject': 'Project Work', 'semester': 3},
            {'period': 2, 'start': time(10, 0), 'end': time(10, 50), 'subject': 'Seminar', 'semester': 3},
        ],
        'Sunday': []
    },
    'Mechanical Engineering': {
    'Monday': [
        {'period': 1, 'start': time(9, 0), 'end': time(9, 50), 'subject': 'Engineering Mathematics – III', 'semester': 3},
        {'period': 2, 'start': time(10, 0), 'end': time(10, 50), 'subject': 'Strength of Materials', 'semester': 3},
        {'period': 3, 'start': time(11, 0), 'end': time(11, 50), 'subject': 'Thermodynamics', 'semester': 3},
        {'period': 4, 'start': time(12, 0), 'end': time(12, 50), 'subject': 'Manufacturing Processes', 'semester': 3},
        {'period': 5, 'start': time(14, 0), 'end': time(14, 50), 'subject': 'Fluid Mechanics', 'semester': 3},
        {'period': 6, 'start': time(15, 0), 'end': time(15, 50), 'subject': 'Programming for Engineers', 'semester': 3},
        {'period': 7, 'start': time(16, 0), 'end': time(16, 50), 'subject': 'Material Science', 'semester': 3},
    ],

    'Tuesday': [
        {'period': 1, 'start': time(9, 0), 'end': time(9, 50), 'subject': 'Strength of Materials', 'semester': 3},
        {'period': 2, 'start': time(10, 0), 'end': time(10, 50), 'subject': 'Fluid Mechanics', 'semester': 3},
        {'period': 3, 'start': time(11, 0), 'end': time(11, 50), 'subject': 'Engineering Thermodynamics', 'semester': 3},
        {'period': 4, 'start': time(12, 0), 'end': time(12, 50), 'subject': 'Manufacturing Technology', 'semester': 3},
        {'period': 5, 'start': time(14, 0), 'end': time(14, 50), 'subject': 'Programming for Engineers', 'semester': 3},
    ],

    'Wednesday': [
        {'period': 1, 'start': time(9, 0), 'end': time(9, 50), 'subject': 'Aptitude', 'semester': 3},
        {'period': 2, 'start': time(10, 0), 'end': time(10, 50), 'subject': 'Engineering Drawing', 'semester': 3},
        {'period': 3, 'start': time(11, 0), 'end': time(11, 50), 'subject': 'Strength of Materials', 'semester': 3},
        {'period': 4, 'start': time(12, 0), 'end': time(12, 50), 'subject': 'Material Science', 'semester': 3},
    ],

    'Thursday': [
        {'period': 1, 'start': time(9, 0), 'end': time(9, 50), 'subject': 'Library', 'semester': 3},
        {'period': 2, 'start': time(10, 0), 'end': time(10, 50), 'subject': 'Thermodynamics', 'semester': 3},
        {'period': 3, 'start': time(11, 0), 'end': time(11, 50), 'subject': 'Metrology and Measurements', 'semester': 3},
        {'period': 4, 'start': time(12, 0), 'end': time(12, 50), 'subject': 'CAD / CAM', 'semester': 3},
    ],

    'Friday': [
        {'period': 1, 'start': time(9, 0), 'end': time(9, 50), 'subject': 'Manufacturing Processes', 'semester': 3},
        {'period': 2, 'start': time(10, 0), 'end': time(10, 50), 'subject': 'Fluid Mechanics', 'semester': 3},
        {'period': 3, 'start': time(11, 0), 'end': time(11, 50), 'subject': 'Library', 'semester': 3},
        {'period': 4, 'start': time(12, 0), 'end': time(12, 50), 'subject': 'Computer-Aided Engineering', 'semester': 3},
    ],

    'Saturday': [
        {'period': 1, 'start': time(9, 0), 'end': time(9, 50), 'subject': 'Project Work', 'semester': 3},
        {'period': 2, 'start': time(10, 0), 'end': time(10, 50), 'subject': 'Seminar', 'semester': 3},
    ],

    'Sunday': []
},
'Civil Engineering': {
    'Monday': [
        {'period': 1, 'start': time(9, 0), 'end': time(9, 50), 'subject': 'Engineering Mathematics – III', 'semester': 3},
        {'period': 2, 'start': time(10, 0), 'end': time(10, 50), 'subject': 'Strength of Materials', 'semester': 3},
        {'period': 3, 'start': time(11, 0), 'end': time(11, 50), 'subject': 'Surveying – I', 'semester': 3},
        {'period': 4, 'start': time(12, 0), 'end': time(12, 50), 'subject': 'Engineering Geology', 'semester': 3},
        {'period': 5, 'start': time(14, 0), 'end': time(14, 50), 'subject': 'Fluid Mechanics', 'semester': 3},
        {'period': 6, 'start': time(15, 0), 'end': time(15, 50), 'subject': 'Programming for Engineers', 'semester': 3},
        {'period': 7, 'start': time(16, 0), 'end': time(16, 50), 'subject': 'Construction Materials', 'semester': 3},
    ],

    'Tuesday': [
        {'period': 1, 'start': time(9, 0), 'end': time(9, 50), 'subject': 'Strength of Materials', 'semester': 3},
        {'period': 2, 'start': time(10, 0), 'end': time(10, 50), 'subject': 'Fluid Mechanics', 'semester': 3},
        {'period': 3, 'start': time(11, 0), 'end': time(11, 50), 'subject': 'Surveying – I', 'semester': 3},
        {'period': 4, 'start': time(12, 0), 'end': time(12, 50), 'subject': 'Building Construction', 'semester': 3},
        {'period': 5, 'start': time(14, 0), 'end': time(14, 50), 'subject': 'Programming for Engineers', 'semester': 3},
    ],

    'Wednesday': [
        {'period': 1, 'start': time(9, 0), 'end': time(9, 50), 'subject': 'Aptitude', 'semester': 3},
        {'period': 2, 'start': time(10, 0), 'end': time(10, 50), 'subject': 'Engineering Drawing', 'semester': 3},
        {'period': 3, 'start': time(11, 0), 'end': time(11, 50), 'subject': 'Strength of Materials', 'semester': 3},
        {'period': 4, 'start': time(12, 0), 'end': time(12, 50), 'subject': 'Construction Materials', 'semester': 3},
    ],

    'Thursday': [
        {'period': 1, 'start': time(9, 0), 'end': time(9, 50), 'subject': 'Library', 'semester': 3},
        {'period': 2, 'start': time(10, 0), 'end': time(10, 50), 'subject': 'Engineering Geology', 'semester': 3},
        {'period': 3, 'start': time(11, 0), 'end': time(11, 50), 'subject': 'Surveying Instruments', 'semester': 3},
        {'period': 4, 'start': time(12, 0), 'end': time(12, 50), 'subject': 'CAD for Civil Engineering', 'semester': 3},
    ],

    'Friday': [
        {'period': 1, 'start': time(9, 0), 'end': time(9, 50), 'subject': 'Building Construction', 'semester': 3},
        {'period': 2, 'start': time(10, 0), 'end': time(10, 50), 'subject': 'Fluid Mechanics', 'semester': 3},
        {'period': 3, 'start': time(11, 0), 'end': time(11, 50), 'subject': 'Library', 'semester': 3},
        {'period': 4, 'start': time(12, 0), 'end': time(12, 50), 'subject': 'Environmental Engineering – I', 'semester': 3},
    ],

    'Saturday': [
        {'period': 1, 'start': time(9, 0), 'end': time(9, 50), 'subject': 'Project Work', 'semester': 3},
        {'period': 2, 'start': time(10, 0), 'end': time(10, 50), 'subject': 'Seminar', 'semester': 3},
    ],

    'Sunday': []
},
'Electronics Engineering': {
    'Monday': [
        {'period': 1, 'start': time(9, 0), 'end': time(9, 50), 'subject': 'Engineering Mathematics – III', 'semester': 3},
        {'period': 2, 'start': time(10, 0), 'end': time(10, 50), 'subject': 'Electronic Devices & Circuits', 'semester': 3},
        {'period': 3, 'start': time(11, 0), 'end': time(11, 50), 'subject': 'Signals & Systems', 'semester': 3},
        {'period': 4, 'start': time(12, 0), 'end': time(12, 50), 'subject': 'Network Analysis', 'semester': 3},
        {'period': 5, 'start': time(13, 0), 'end': time(13, 50), 'subject': 'Digital Electronics', 'semester': 3},
        {'period': 6, 'start': time(15, 30), 'end': time(15, 50), 'subject': 'Programming for python', 'semester': 3},
        {'period': 7, 'start': time(16, 0), 'end': time(16, 50), 'subject': 'Programming for Engineers', 'semester': 3},
    ],

    'Tuesday': [
        {'period': 1, 'start': time(9, 0), 'end': time(9, 50), 'subject': 'Electronic Devices & Circuits', 'semester': 3},
        {'period': 2, 'start': time(10, 0), 'end': time(10, 50), 'subject': 'Digital Electronics', 'semester': 3},
        {'period': 3, 'start': time(11, 0), 'end': time(11, 50), 'subject': 'Signals & Systems', 'semester': 3},
        {'period': 4, 'start': time(12, 0), 'end': time(12, 50), 'subject': 'Linear Integrated Circuits', 'semester': 3},
        {'period': 5, 'start': time(13, 0), 'end': time(13, 50), 'subject': 'Programming for python', 'semester': 3},
        {'period': 6, 'start': time(14, 0), 'end': time(14, 50), 'subject': 'Programming for Engineers', 'semester': 3},
    ],

    'Wednesday': [
        {'period': 1, 'start': time(9, 0), 'end': time(9, 50), 'subject': 'Aptitude', 'semester': 3},
        {'period': 2, 'start': time(10, 0), 'end': time(10, 50), 'subject': 'Network Analysis', 'semester': 3},
        {'period': 3, 'start': time(11, 0), 'end': time(11, 50), 'subject': 'Analog Circuits', 'semester': 3},
        {'period': 4, 'start': time(12, 0), 'end': time(12, 50), 'subject': 'Digital Electronic', 'semester': 3},
        {'period': 5, 'start': time(13, 0), 'end': time(13, 50), 'subject': 'Digital Communications', 'semester': 3},
    ],
    

    'Thursday': [
        {'period': 1, 'start': time(9, 0), 'end': time(9, 50), 'subject': 'Library', 'semester': 3},
        {'period': 2, 'start': time(10, 0), 'end': time(10, 50), 'subject': 'Signals & Systems', 'semester': 3},
        {'period': 3, 'start': time(11, 0), 'end': time(11, 50), 'subject': 'Electronic Measurements & Instrumentation', 'semester': 3},
        {'period': 4, 'start': time(12, 0), 'end': time(12, 50), 'subject': 'PCB Design', 'semester': 3},
    ],

    'Friday': [
        {'period': 1, 'start': time(9, 0), 'end': time(9, 50), 'subject': 'Linear Integrated Circuits', 'semester': 3},
        {'period': 2, 'start': time(10, 0), 'end': time(10, 50), 'subject': 'Network Analysis', 'semester': 3},
        {'period': 3, 'start': time(11, 0), 'end': time(11, 50), 'subject': 'Library', 'semester': 3},
        {'period': 4, 'start': time(12, 0), 'end': time(12, 50), 'subject': 'Digital System Design', 'semester': 3},
    ],

    'Saturday': [
        {'period': 1, 'start': time(9, 0), 'end': time(9, 50), 'subject': 'Project Work', 'semester': 3},
        {'period': 2, 'start': time(10, 0), 'end': time(10, 50), 'subject': 'Seminar', 'semester': 3},
    ],

    'Sunday': []
}


}

def get_all_students_by_department(department):
    """Get all students from a specific department"""
    try:
        if not os.path.exists(STUDENTS_CSV):
            return []
        
        df = pd.read_csv(STUDENTS_CSV)
        students = df[df['department'] == department]
        return students.to_dict('records')
    except Exception as e:
        print(f"❌ Error loading students: {e}")
        return []


def check_attendance_marked(student_id, subject, period, date_str):
    """Check if student has already marked attendance"""
    try:
        if not os.path.exists(ATTENDANCE_CSV):
            return False
        
        df = pd.read_csv(ATTENDANCE_CSV)
        
        # Check if attendance exists
        marked = df[
            (df['student_id'] == student_id) & 
            (df['subject'] == subject) & 
            (df['period'] == str(period)) & 
            (df['date'] == date_str)
        ]
        
        return not marked.empty
        
    except Exception as e:
        print(f"❌ Error checking attendance: {e}")
        return False


def mark_student_absent(student_id, subject, period, department, semester):
    """Mark a student as absent in CSV"""
    try:
        now = datetime.now()
        date_str = now.strftime('%Y-%m-%d')
        time_str = now.strftime('%H:%M:%S')
        
        # Check if already marked
        if check_attendance_marked(student_id, subject, period, date_str):
            return False
        
        # Append to attendance CSV
        with open(ATTENDANCE_CSV, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                student_id,
                date_str,
                time_str,
                'absent',  # Status
                subject,
                str(period),
                department,
                str(semester),
                now.strftime('%Y-%m-%d %H:%M:%S')  # marked_at
            ])
        
        print(f"✅ Marked absent: {student_id} - {subject} Period {period}")
        return True
        
    except Exception as e:
        print(f"❌ Error marking absent: {e}")
        return False


def send_absent_notification(student_id, student_name, parent_email, subject, period, date_str):
    """Send email notification to parent about absent student"""
    
    if not parent_email or '@' not in parent_email:
        print(f"⚠️ Invalid parent email for {student_id}")
        return False
    
    email_subject = f"🚨 Absence Alert - {student_name} - {date_str}"
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; background: #f4f4f4; padding: 20px; }}
            .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .header {{ background: linear-gradient(135deg, #ef4444, #dc2626); color: white; padding: 30px; border-radius: 10px; text-align: center; }}
            .header h1 {{ margin: 0; font-size: 28px; }}
            .content {{ padding: 30px 0; }}
            .alert-box {{ background: #fef2f2; border-left: 4px solid #ef4444; padding: 20px; margin: 20px 0; border-radius: 5px; }}
            .info-row {{ display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #f3f4f6; }}
            .info-label {{ font-weight: bold; color: #6b7280; }}
            .info-value {{ color: #111827; }}
            .footer {{ text-align: center; color: #6b7280; font-size: 14px; margin-top: 30px; padding-top: 20px; border-top: 1px solid #e5e7eb; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚨 Absence Alert</h1>
            </div>
            
            <div class="content">
                <h2>Dear Parent/Guardian,</h2>
                
                <div class="alert-box">
                    <strong>⚠️ Your ward was marked ABSENT for not marking attendance within the allowed time window.</strong>
                </div>
                
                <h3>Absence Details:</h3>
                
                <div class="info-row">
                    <span class="info-label">Student Name:</span>
                    <span class="info-value">{student_name}</span>
                </div>
                
                <div class="info-row">
                    <span class="info-label">Student ID:</span>
                    <span class="info-value">{student_id}</span>
                </div>
                
                <div class="info-row">
                    <span class="info-label">Date:</span>
                    <span class="info-value">{date_str}</span>
                </div>
                
                <div class="info-row">
                    <span class="info-label">Subject:</span>
                    <span class="info-value">{subject}</span>
                </div>
                
                <div class="info-row">
                    <span class="info-label">Period:</span>
                    <span class="info-value">{period}</span>
                </div>
                
                <div class="info-row">
                    <span class="info-label">Time:</span>
                    <span class="info-value">{datetime.now().strftime('%I:%M %p')}</span>
                </div>
                
                <h3>What This Means:</h3>
                <ul>
                    <li>Student did not mark attendance within 5 minutes of class start</li>
                    <li>Attendance has been automatically marked as ABSENT</li>
                    <li>This will affect the student's overall attendance percentage</li>
                </ul>
                
                <h3>Action Required:</h3>
                <p>Please contact your ward to understand the reason for absence. If this is an error, please contact the institution immediately.</p>
                
                <div class="alert-box" style="background: #fef3c7; border-left: 4px solid #f59e0b;">
                    <strong>📊 Attendance Reminder:</strong> Maintaining 75% attendance is mandatory for appearing in examinations.
                </div>
            </div>
            
            <div class="footer">
                <p>This is an automated notification from Smart Attendance System</p>
                <p>Please do not reply to this email</p>
                <p>&copy; 2025 Smart Attendance System</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    body = f"""
    Dear Parent/Guardian,
    
    ABSENCE ALERT
    
    Your ward was marked ABSENT for not marking attendance within the allowed time window.
    
    Student Name: {student_name}
    Student ID: {student_id}
    Date: {date_str}
    Subject: {subject}
    Period: {period}
    Time: {datetime.now().strftime('%I:%M %p')}
    
    What This Means:
    - Student did not mark attendance within 5 minutes of class start
    - Attendance has been automatically marked as ABSENT
    - This will affect the student's overall attendance percentage
    
    Action Required:
    Please contact your ward to understand the reason for absence. If this is an error, please contact the institution immediately.
    
    Attendance Reminder: Maintaining 75% attendance is mandatory for appearing in examinations.
    
    This is an automated notification from Smart Attendance System.
    
    Best regards,
    Smart Attendance System
    """
    
    try:
        result = send_email(parent_email, email_subject, body, html)
        if result:
            print(f"✅ Email sent to parent: {parent_email}")
        else:
            print(f"❌ Failed to send email to: {parent_email}")
        return result
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        return False


def check_and_mark_absent_students():
    """
    Main function that checks if any class period has passed the 5-minute window
    and marks absent students who haven't marked attendance
    """
    try:
        now = datetime.now()
        current_time = now.time()
        current_day = now.strftime('%A')
        current_date = now.strftime('%Y-%m-%d')
        
        print(f"\n{'='*80}")
        print(f"🔍 AUTOMATIC ATTENDANCE CHECK - {now.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*80}")
        
        # Check each department
        for department, schedule in CLASS_SCHEDULE.items():
            if current_day not in schedule:
                continue
            
            day_schedule = schedule[current_day]
            
            # Check each period
            for period_info in day_schedule:
                period_start = period_info['start']
                period_num = period_info['period']
                subject = period_info['subject']
                semester = period_info['semester']
                
                # Calculate the 5-minute window end time
                start_datetime = datetime.combine(date.today(), period_start)
                window_end_datetime = start_datetime + timedelta(minutes=ATTENDANCE_WINDOW_MINUTES)
                window_end_time = window_end_datetime.time()
                
                # Check if we are exactly past the 5-minute window (within 1 minute tolerance)
                # This ensures we only process each period once
                tolerance_start = window_end_datetime
                tolerance_end = window_end_datetime + timedelta(minutes=1)
                
                if tolerance_start.time() <= current_time < tolerance_end.time():
                    print(f"\n⏰ Processing: {department} - {subject} Period {period_num}")
                    print(f"   Class started: {period_start.strftime('%I:%M %p')}")
                    print(f"   Window closed: {window_end_time.strftime('%I:%M %p')}")
                    
                    # Get all students in this department
                    students = get_all_students_by_department(department)
                    
                    absent_count = 0
                    email_sent_count = 0
                    
                    # Check each student
                    for student in students:
                        student_id = student['user_id']
                        student_name = student.get('name', 'Unknown')
                        parent_email = student.get('parent_email', '')
                        
                        # Check if attendance is marked
                        if not check_attendance_marked(student_id, subject, period_num, current_date):
                            # Mark as absent
                            if mark_student_absent(student_id, subject, period_num, department, semester):
                                absent_count += 1
                                print(f"   ❌ {student_id} ({student_name}) - ABSENT")
                                
                                # Send email to parent
                                if parent_email:
                                    if send_absent_notification(
                                        student_id, 
                                        student_name, 
                                        parent_email, 
                                        subject, 
                                        period_num, 
                                        current_date
                                    ):
                                        email_sent_count += 1
                    
                    if absent_count > 0:
                        print(f"\n   📊 Summary:")
                        print(f"      Total Absent: {absent_count}")
                        print(f"      Emails Sent: {email_sent_count}")
                    else:
                        print(f"   ✅ All students marked attendance")
        
        print(f"{'='*80}\n")
        
    except Exception as e:
        print(f"❌ Error in automatic attendance check: {e}")
        import traceback
        traceback.print_exc()


# ==================== SCHEDULER INITIALIZATION ====================
scheduler = None

def start_attendance_scheduler(app):
    """Start the background scheduler with Flask app context"""
    global scheduler
    
    if scheduler is not None:
        print("⚠️ Scheduler already running")
        return
    
    scheduler = BackgroundScheduler()
    
    # Wrap the check function with app context
    def check_with_context():
        with app.app_context():
            check_and_mark_absent_students()
    
    # Run every 1 minute
    scheduler.add_job(
        check_with_context,
        'interval',
        seconds=CHECK_INTERVAL_SECONDS,
        id='auto_attendance_check',
        replace_existing=True
    )
    
    scheduler.start()
    
    print("\n" + "="*80)
    print("✅ AUTOMATIC ATTENDANCE SCHEDULER STARTED")
    print("="*80)
    print(f"⏰ Check Interval: Every {CHECK_INTERVAL_SECONDS} seconds")
    print(f"⏱️  Attendance Window: {ATTENDANCE_WINDOW_MINUTES} minutes after class start")
    print(f"📧 Parent Email: Enabled")
    print("="*80 + "\n")


def stop_attendance_scheduler():
    """Stop the background scheduler"""
    global scheduler
    
    if scheduler is not None:
        scheduler.shutdown()
        scheduler = None
        print("🛑 Attendance scheduler stopped")