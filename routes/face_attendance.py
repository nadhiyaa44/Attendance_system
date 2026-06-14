# routes/face_attendance.py - FIXED VERSION
from flask import Blueprint, request, jsonify, Response
from datetime import datetime, time, timedelta
import os
import base64
import cv2
import numpy as np
from io import BytesIO
from PIL import Image
import traceback

bp = Blueprint('face_attendance', __name__, url_prefix='/face-attendance')

# ==================== CONFIGURATION ====================
SIMILARITY_THRESHOLD = 0.4
MAX_IMAGE_SIZE = 10 * 1024 * 1024
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png'}
FACE_SIZE = (200, 200)
ATTENDANCE_WINDOW_MINUTES = 5  # 5 minutes from class start to mark attendance

# ==================== CLASS SCHEDULE ====================
CLASS_SCHEDULE = {
    'Computer Science': {
        'Monday': [
            {'period': 1, 'start': time(9, 2), 'end': time(10, 00), 'subject': 'Data Structures', 'semester': 3},
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
        {'period': 6, 'start': time(15, 0), 'end': time(15, 50), 'subject': 'Programming for python', 'semester': 3},
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

# ==================== HELPER FUNCTIONS ====================

def safe_jsonify(data, status=200):
    """Safely return JSON response"""
    response = jsonify(data)
    response.status_code = status
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    return response


def validate_image(image_data):
    """Validate image data"""
    if not image_data:
        return False, "No image data"
    if len(image_data) > MAX_IMAGE_SIZE:
        return False, "Image too large"
    return True, None


def match_face(captured_image, student_id):
    """Match captured face with registered faces using face detection"""
    try:
        student_dir = os.path.join('static', 'uploads', 'student_faces', student_id)
        if not os.path.exists(student_dir):
            return 0.0

        registered_images = [f for f in os.listdir(student_dir) 
                           if os.path.splitext(f)[1].lower() in ALLOWED_EXTENSIONS]
        
        if not registered_images:
            return 0.0

        # Load Haar cascade for face detection
        face_cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        face_cascade = cv2.CascadeClassifier(face_cascade_path)

        captured_gray = cv2.cvtColor(captured_image, cv2.COLOR_BGR2GRAY)
        
        # Detect and crop face from captured image
        faces = face_cascade.detectMultiScale(captured_gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60))
        if len(faces) > 0:
            x, y, w, h = faces[0]
            captured_face = captured_gray[y:y+h, x:x+w]
        else:
            # No face detected — use full image but log it
            print(f"  ⚠️ No face detected in captured image for {student_id}, using full frame")
            captured_face = captured_gray

        captured_resized = cv2.resize(captured_face, FACE_SIZE)

        similarities = []
        for img_file in registered_images[:5]:  # Check up to 5 registered images
            registered_path = os.path.join(student_dir, img_file)
            registered = cv2.imread(registered_path, cv2.IMREAD_GRAYSCALE)
            
            if registered is None:
                continue
            
            # Detect and crop face from registered image too
            reg_faces = face_cascade.detectMultiScale(registered, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
            if len(reg_faces) > 0:
                rx, ry, rw, rh = reg_faces[0]
                registered_face = registered[ry:ry+rh, rx:rx+rw]
            else:
                registered_face = registered
                
            registered_resized = cv2.resize(registered_face, FACE_SIZE)
            result = cv2.matchTemplate(captured_resized, registered_resized, cv2.TM_CCOEFF_NORMED)
            similarities.append(float(result[0][0]))
        
        return max(similarities) if similarities else 0.0
        
    except Exception as e:
        print(f"Error matching face: {e}")
        return 0.0


def can_mark_attendance(department=None):
    """
    Check if attendance can be marked - FIXED VERSION
    """
    try:
        now = datetime.now()
        current_time = now.time()
        day = now.strftime('%A')

        print(f"\n{'='*60}")
        print(f"CHECKING ATTENDANCE WINDOW")
        print(f"{'='*60}")
        print(f"Current Time: {now.strftime('%I:%M:%S %p')}")
        print(f"Current Day: {day}")
        print(f"Department Filter: {department or 'All'}")

        departments_to_check = [department] if department else CLASS_SCHEDULE.keys()
        all_periods = []
        
        for dept in departments_to_check:
            if dept not in CLASS_SCHEDULE:
                print(f"⚠️ Department '{dept}' not in schedule")
                continue
                
            schedule = CLASS_SCHEDULE.get(dept, {})
            if day not in schedule:
                print(f"⚠️ No schedule for {day} in {dept}")
                continue

            print(f"\n🔍 Checking {dept} schedule for {day}:")
            
            for period in schedule[day]:
                period_start = period['start']
                period_end = period['end']
                
                # Convert times to datetime for comparison
                start_dt = datetime.combine(now.date(), period_start)
                end_dt = datetime.combine(now.date(), period_end)
                window_end = start_dt + timedelta(minutes=ATTENDANCE_WINDOW_MINUTES)
                
                print(f"\n  Period {period['period']}: {period['subject']}")
                print(f"    Start: {period_start.strftime('%I:%M %p')}")
                print(f"    End: {period_end.strftime('%I:%M %p')}")
                print(f"    Attendance Window: {period_start.strftime('%I:%M %p')} - {window_end.strftime('%I:%M %p')}")
                print(f"    Current: {now.strftime('%I:%M:%S %p')}")
                
                # Check if we're within the attendance window
                # Must be: start_time <= now <= start_time + window_minutes
                if start_dt <= now <= window_end:
                    minutes_remaining = int((window_end - now).total_seconds() / 60)
                    seconds_remaining = int((window_end - now).total_seconds() % 60)
                    
                    print(f"    ✅ ACTIVE - {minutes_remaining}m {seconds_remaining}s remaining")
                    print(f"    Start DT: {start_dt}")
                    print(f"    Current DT: {now}")
                    print(f"    Window End DT: {window_end}")
                    print(f"    Comparison: {start_dt} <= {now} <= {window_end} = TRUE")
                    
                    all_periods.append({
                        'can_mark': True,
                        'department': dept,
                        'period': period['period'],
                        'subject': period['subject'],
                        'semester': period['semester'],
                        'start_time': period['start'].strftime('%H:%M'),
                        'end_time': period['end'].strftime('%H:%M'),
                        'time_remaining': minutes_remaining,
                        'message': f'✅ {period["subject"]} - Period {period["period"]} ({minutes_remaining}m {seconds_remaining}s left)'
                    })
                else:
                    print(f"    ❌ Outside window")
        
        print(f"\n{'='*60}")
        
        print(f"\n{'='*60}")
        
        if all_periods:
            all_periods.sort(key=lambda x: x['time_remaining'], reverse=True)
            print(f"✅ Found {len(all_periods)} active period(s)")
            print(f"First active period: {all_periods[0]['subject']} - Period {all_periods[0]['period']}")
            print(f"{'='*60}\n")
            return all_periods
        
        print(f"❌ No active attendance windows")
        print(f"{'='*60}\n")
        
        return [{
            'can_mark': False, 
            'message': f'No classes now or attendance window closed ({ATTENDANCE_WINDOW_MINUTES} min limit)'
        }]
        
    except Exception as e:
        print(f"\n{'='*60}")
        print(f"❌ ERROR in can_mark_attendance")
        print(f"{'='*60}")
        print(f"Error: {e}")
        traceback.print_exc()
        print(f"{'='*60}\n")
        return [{
            'can_mark': False, 
            'message': 'Error checking schedule'
        }]


# ==================== ROUTES ====================

@bp.route('/mark')
def mark_attendance_page():
    """Main attendance page with camera interface"""
    html = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Face Attendance System</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 900px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        
        h1 { 
            color: #667eea; 
            text-align: center; 
            margin-bottom: 30px;
            font-size: 2em;
        }
        
        .status-card {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 25px;
            border-radius: 15px;
            margin-bottom: 25px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
        }
        
        .status-card h2 { font-size: 1.8em; margin-bottom: 10px; }
        .status-card p { font-size: 1.1em; margin: 5px 0; }
        
        .camera-section {
            background: #000;
            padding: 20px;
            border-radius: 15px;
            margin: 20px 0;
        }
        
        video {
            width: 100%;
            max-width: 640px;
            display: block;
            margin: 0 auto;
            border-radius: 10px;
        }
        
        .controls { text-align: center; margin-top: 20px; }
        
        .btn {
            padding: 15px 35px;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            margin: 5px;
            color: white;
            transition: all 0.3s ease;
        }
        
        .btn-success { background: linear-gradient(135deg, #10b981, #059669); }
        .btn-danger { background: linear-gradient(135deg, #ef4444, #dc2626); }
        .btn-primary { background: linear-gradient(135deg, #667eea, #764ba2); }
        
        .btn:hover { 
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.2);
        }
        
        .btn:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }
        
        .alert {
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            text-align: center;
            font-weight: 600;
            animation: slideIn 0.3s ease;
        }
        
        @keyframes slideIn {
            from { opacity: 0; transform: translateY(-10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .alert-success { background: #d1fae5; color: #065f46; border-left: 5px solid #10b981; }
        .alert-error { background: #fee2e2; color: #991b1b; border-left: 5px solid #ef4444; }
        .alert-info { background: #dbeafe; color: #1e40af; border-left: 5px solid #3b82f6; }
        
        .result-success {
            background: linear-gradient(135deg, #d1fae5, #a7f3d0);
            padding: 30px;
            border-radius: 15px;
            text-align: center;
        }
        
        .result-success h2 { color: #065f46; font-size: 2em; margin-bottom: 15px; }
        .result-success p { color: #047857; font-size: 1.2em; margin: 10px 0; }
        
        .debug-info {
            background: #f3f4f6;
            padding: 15px;
            border-radius: 10px;
            margin: 20px 0;
            font-family: monospace;
            font-size: 0.9em;
            text-align: left;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📸 Face Attendance System</h1>
        
        <div class="status-card" id="statusCard">
            <h2>⏰ Loading...</h2>
            <p>Please wait...</p>
        </div>
        
        <div id="alertContainer"></div>
        
        <div class="camera-section" id="cameraSection" style="display:none;">
            <video id="video" autoplay playsinline></video>
            <canvas id="canvas" style="display:none;"></canvas>
            <div class="controls">
                <button class="btn btn-success" id="captureBtn" onclick="captureAttendance()">
                    📸 Mark Attendance
                </button>
                <button class="btn btn-danger" onclick="stopCamera()">⏹️ Stop Camera</button>
            </div>
        </div>
        
        <div style="text-align:center; margin:20px;">
            <button class="btn btn-primary" id="startBtn" onclick="startCamera()">
                🎥 Start Camera
            </button>
        </div>
        
        <div id="resultContainer"></div>
        
        <!-- Debug Info -->
        <div class="debug-info" id="debugInfo">
            <strong>Debug Info:</strong><br>
            <span id="debugText">Checking status...</span>
        </div>
    </div>
    
    <script>
        let video, canvas, stream;
        
        window.addEventListener('load', () => {
            video = document.getElementById('video');
            canvas = document.getElementById('canvas');
            checkStatus();
            setInterval(checkStatus, 10000); // Check every 10 seconds
        });
        
        async function checkStatus() {
            try {
                const res = await fetch('/face-attendance/get-current-status');
                const data = await res.json();
                
                // Update debug info
                const debugText = document.getElementById('debugText');
                debugText.innerHTML = `
                    Time: ${data.current_time}<br>
                    Day: ${data.current_day}<br>
                    Periods Found: ${data.periods ? data.periods.length : 0}<br>
                    Can Mark: ${data.periods && data.periods[0] ? data.periods[0].can_mark : 'false'}
                `;
                
                if (data.success && data.periods && data.periods.length > 0) {
                    const p = data.periods[0];
                    
                    if (p.can_mark) {
                        document.getElementById('statusCard').innerHTML = 
                            `<h2>✅ ${p.subject}</h2>
                             <p>Period ${p.period} - ${p.department}</p>
                             <p>${p.message}</p>
                             <p style="font-size: 0.9em; margin-top: 10px;">⏱️ Window closes in ${p.time_remaining} minutes</p>`;
                    } else {
                        document.getElementById('statusCard').innerHTML = 
                            `<h2>⏰ ${data.current_day}</h2>
                             <p>${p.message}</p>
                             <p style="font-size: 0.9em; margin-top: 10px;">Current Time: ${data.current_time}</p>`;
                    }
                }
            } catch (e) {
                console.error('Status check error:', e);
                document.getElementById('statusCard').innerHTML = 
                    `<h2>❌ Error</h2><p>Failed to load status</p>`;
                document.getElementById('debugText').innerHTML = `Error: ${e.message}`;
            }
        }
        
        async function startCamera() {
            try {
                stream = await navigator.mediaDevices.getUserMedia({
                    video: { width: 1280, height: 720, facingMode: 'user' }
                });
                video.srcObject = stream;
                document.getElementById('cameraSection').style.display = 'block';
                document.getElementById('startBtn').style.display = 'none';
                showAlert('✅ Camera started successfully!', 'info');
            } catch (e) {
                showAlert('❌ Camera error: ' + e.message, 'error');
            }
        }
        
        function stopCamera() {
            if (stream) {
                stream.getTracks().forEach(t => t.stop());
                video.srcObject = null;
                stream = null;
            }
            document.getElementById('cameraSection').style.display = 'none';
            document.getElementById('startBtn').style.display = 'inline-block';
            showAlert('Camera stopped', 'info');
        }
        
        async function captureAttendance() {
            const btn = document.getElementById('captureBtn');
            btn.disabled = true;
            btn.textContent = '⏳ Processing...';
            
            try {
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
                canvas.getContext('2d').drawImage(video, 0, 0);
                const imageData = canvas.toDataURL('image/jpeg', 0.9);
                
                const res = await fetch('/face-attendance/recognize-and-mark', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({image: imageData})
                });
                
                const result = await res.json();
                
                if (result.success) {
                    document.getElementById('resultContainer').innerHTML = `
                        <div class="result-success">
                            <h2>✅ Attendance Marked Successfully!</h2>
                            <p><strong>👤 ${result.student_name}</strong></p>
                            <p>🆔 Student ID: ${result.student_id}</p>
                            <p>📚 ${result.subject} - Period ${result.period}</p>
                            <p>🎯 Confidence: ${result.confidence}%</p>
                            <p>🏢 Department: ${result.department}</p>
                            <p>🕐 Time: ${result.time_marked}</p>
                        </div>`;
                    stopCamera();
                    setTimeout(checkStatus, 1000);
                } else {
                    showAlert('❌ ' + result.message, 'error');
                }
            } catch (e) {
                showAlert('❌ Error: ' + e.message, 'error');
            } finally {
                btn.disabled = false;
                btn.textContent = '📸 Mark Attendance';
            }
        }
        
        function showAlert(msg, type) {
            document.getElementById('alertContainer').innerHTML = 
                `<div class="alert alert-${type}">${msg}</div>`;
            setTimeout(() => {
                document.getElementById('alertContainer').innerHTML = '';
            }, 5000);
        }
    </script>
</body>
</html>'''
    return Response(html, mimetype='text/html')


@bp.route('/check-time-window', methods=['GET'])
def check_time_window():
    """Check if attendance window is open (used by face_attendance.html)"""
    try:
        all_periods = can_mark_attendance()
        if all_periods and all_periods[0].get('can_mark'):
            p = all_periods[0]
            return safe_jsonify({
                'can_mark': True,
                'period': p['period'],
                'subject': p['subject'],
                'start_time': p['start_time'],
                'end_time': p['end_time'],
                'time_remaining': p['time_remaining'],
                'message': p['message']
            })
        else:
            msg = all_periods[0].get('message', 'No active class') if all_periods else 'No active class'
            return safe_jsonify({
                'can_mark': False,
                'message': msg
            })
    except Exception as e:
        return safe_jsonify({'can_mark': False, 'message': str(e)})


@bp.route('/get-current-status', methods=['GET'])
def get_current_status():
    """Get current attendance status"""
    try:
        now = datetime.now()
        day = now.strftime('%A')
        current_time = now.strftime('%I:%M:%S %p')
        
        all_periods = can_mark_attendance()
        
        return safe_jsonify({
            'success': True,
            'current_time': current_time,
            'current_day': day,
            'periods': all_periods
        })
        
    except Exception as e:
        print(f"ERROR in get_current_status: {e}")
        traceback.print_exc()
        return safe_jsonify({
            'success': False,
            'message': str(e),
            'periods': [{'can_mark': False, 'message': 'Error checking status'}]
        })


@bp.route('/recognize-and-mark', methods=['POST'])
def recognize_and_mark():
    """Recognize face and mark attendance"""
    try:
        from utils.database import mark_attendance, get_user_by_id, check_duplicate_attendance
        
        data = request.get_json()
        if not data:
            return safe_jsonify({'success': False, 'message': 'No data received'})
        
        image_data = data.get('image')
        valid, error = validate_image(image_data)
        if not valid:
            return safe_jsonify({'success': False, 'message': error})

        # Decode image
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        image_bytes = base64.b64decode(image_data)
        image = Image.open(BytesIO(image_bytes))
        image_np = np.array(image)
        
        if len(image_np.shape) == 3:
            image_np = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)

        # Find registered students
        students_dir = os.path.join('static', 'uploads', 'student_faces')
        if not os.path.exists(students_dir):
            return safe_jsonify({
                'success': False, 
                'message': 'No students registered. Please register first.'
            })

        # Match face
        best_match = None
        best_score = 0.0
        
        print("\n=== Face Matching Started ===")
        for student_id in os.listdir(students_dir):
            student_path = os.path.join(students_dir, student_id)
            if os.path.isdir(student_path):
                score = match_face(image_np, student_id)
                print(f"Student {student_id}: {score:.3f}")
                
                if score > best_score:
                    best_score = score
                    best_match = student_id

        if best_score < SIMILARITY_THRESHOLD:
            return safe_jsonify({
                'success': False,
                'message': f'Face not recognized. Confidence too low: {best_score:.2%}'
            })

        print(f"\n✅ Best Match: {best_match} (Score: {best_score:.3f})")

        # Get student details
        student = get_user_by_id(best_match, 'student')
        if not student:
            return safe_jsonify({
                'success': False, 
                'message': 'Student record not found in database'
            })

        dept = student.get('department', 'Computer Science')
        
        # Check attendance window
        periods = can_mark_attendance(dept)
        
        print(f"\n{'='*60}")
        print(f"ATTENDANCE WINDOW CHECK FOR MARKING")
        print(f"{'='*60}")
        print(f"Student: {best_match}")
        print(f"Department: {dept}")
        print(f"Periods returned: {len(periods)}")
        
        if periods:
            for i, period in enumerate(periods):
                print(f"\nPeriod {i+1}:")
                print(f"  Can Mark: {period.get('can_mark', False)}")
                print(f"  Subject: {period.get('subject', 'N/A')}")
                print(f"  Message: {period.get('message', 'N/A')}")
        
        if not periods or not periods[0].get('can_mark', False):
            error_msg = periods[0].get('message', 'Unknown error') if periods else 'No periods found'
            print(f"\n❌ Cannot mark attendance: {error_msg}")
            print(f"{'='*60}\n")
            return safe_jsonify({
                'success': False, 
                'message': error_msg
            })
        
        p = periods[0]
        print(f"\n✅ Valid period found: {p['subject']} - Period {p['period']}")
        print(f"{'='*60}\n")

        # Check duplicate
        if check_duplicate_attendance(best_match, p['subject'], str(p['period']), datetime.now().date()):
            return safe_jsonify({
                'success': False, 
                'message': f'Attendance already marked for {p["subject"]} Period {p["period"]}'
            })

        # Mark attendance
        if not mark_attendance(
            student_id=best_match,
            status='present',
            subject=p['subject'],
            period=str(p['period']),
            department=dept,
            semester=p['semester']
        ):
            return safe_jsonify({
                'success': False, 
                'message': 'Failed to save attendance to database'
            })

        print(f"\n✅ Attendance Marked: {best_match} - {p['subject']} Period {p['period']}")

        return safe_jsonify({
            'success': True,
            'message': 'Attendance marked successfully!',
            'student_id': best_match,
            'student_name': student.get('name'),
            'department': dept,
            'confidence': round(best_score * 100, 2),
            'period': p['period'],
            'subject': p['subject'],
            'semester': p['semester'],
            'time_marked': datetime.now().strftime('%I:%M %p')
        })

    except Exception as e:
        print(f"\n❌ ERROR in recognize_and_mark: {e}")
        traceback.print_exc()
        return safe_jsonify({
            'success': False, 
            'message': f'Server error: {str(e)}'
        })