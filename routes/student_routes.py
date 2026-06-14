from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from utils.database import (
    get_attendance, submit_od_request, generate_bus_pass, get_hostel_pass,
    get_user_by_id, ATTENDANCE_CSV, OD_REQUESTS_CSV, submit_hostel_pass
)
from datetime import datetime, time
import os
import pandas as pd

bp = Blueprint('student', __name__, url_prefix='/student')

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'student':
            flash('Please login first!', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


@bp.route('/dashboard')
@login_required
def dashboard():
    """Student Dashboard with proper data - FIXED VERSION"""
    try:
        user_id = session.get('user_id')
        name = session.get('name', 'Student')
        
        # Get student details
        student = get_user_by_id(user_id, 'student')
        if not student:
            flash('Student data not found', 'error')
            return redirect(url_for('auth.login'))
        
        department = student.get('department', 'Computer Science')
        
        # Get attendance summary - FIXED LOGIC
        attendance_data = {
            'total': 0,
            'present': 0,
            'absent': 0,
            'percentage': 0
        }
        
        if os.path.exists(ATTENDANCE_CSV):
            try:
                df = pd.read_csv(ATTENDANCE_CSV)
                df = df.fillna('')
                
                # Filter by student ID
                student_att = df[df['student_id'] == user_id]
                
                if len(student_att) > 0:
                    total = len(student_att)
                    # Count present and OD as present
                    present = len(student_att[(student_att['status'] == 'present') | (student_att['status'] == 'od')])
                    absent = len(student_att[student_att['status'] == 'absent'])
                    percentage = round((present / total) * 100) if total > 0 else 0
                    
                    attendance_data = {
                        'total': total,
                        'present': present,
                        'absent': absent,
                        'percentage': percentage
                    }
                    
                    print(f"📊 Student {user_id} attendance: {present}/{total} = {percentage}%")
                
            except Exception as e:
                print(f"❌ Error calculating attendance: {e}")
                import traceback
                traceback.print_exc()
        
        # Get current date
        current_date = datetime.now().strftime('%A, %B %d, %Y')
        
        # Get today's schedule
        schedule = []
        try:
            # Import CLASS_SCHEDULE from auto_attendance_scheduler
            try:
                from auto_attendance_scheduler import CLASS_SCHEDULE
            except:
                CLASS_SCHEDULE = {}
            
            # Get today's day name
            current_day = datetime.now().strftime('%A')
            
            # Get schedule for today
            if department in CLASS_SCHEDULE and current_day in CLASS_SCHEDULE[department]:
                today_classes = CLASS_SCHEDULE[department][current_day]
                
                # Get today's attendance records
                if os.path.exists(ATTENDANCE_CSV):
                    df = pd.read_csv(ATTENDANCE_CSV)
                    df = df.fillna('')
                    today = datetime.now().strftime('%Y-%m-%d')
                    student_today = df[(df['student_id'] == user_id) & (df['date'] == today)]
                else:
                    student_today = pd.DataFrame()
                
                # Build schedule with attendance status
                current_time = datetime.now().time()
                
                for class_info in today_classes:
                    # Check if attended
                    attended = False
                    if not student_today.empty:
                        class_attended = student_today[
                            (student_today['subject'] == class_info['subject']) & 
                            (student_today['period'] == str(class_info['period']))
                        ]
                        attended = not class_attended.empty
                    
                    # Check if current
                    is_current = class_info['start'] <= current_time <= class_info['end']
                    
                    schedule.append({
                        'period': class_info['period'],
                        'start': class_info['start'].strftime('%I:%M %p'),
                        'end': class_info['end'].strftime('%I:%M %p'),
                        'subject': class_info['subject'],
                        'attended': attended,
                        'is_current': is_current
                    })
        except Exception as e:
            print(f"❌ Error loading schedule: {e}")
            import traceback
            traceback.print_exc()
        
        # Get recent OD requests
        recent_ods = []
        try:
            if os.path.exists(OD_REQUESTS_CSV):
                df = pd.read_csv(OD_REQUESTS_CSV)
                df = df.fillna('')
                
                # Filter by student ID
                student_ods = df[df['student_id'] == user_id]
                
                # Sort by submitted_at descending
                student_ods = student_ods.sort_values('submitted_at', ascending=False)
                
                # Get top 5
                recent_ods = student_ods.head(5).to_dict('records')
        except Exception as e:
            print(f"❌ Error loading OD requests: {e}")
            import traceback
            traceback.print_exc()
        
        return render_template('student/dashboard.html', 
                             name=name,
                             current_date=current_date,
                             attendance=attendance_data,
                             schedule=schedule,
                             recent_ods=recent_ods,
                             session=session)
    
    except Exception as e:
        print(f"❌ Error in student dashboard: {e}")
        import traceback
        traceback.print_exc()
        flash('Error loading dashboard', 'error')
        return redirect(url_for('auth.login'))


@bp.route('/attendance')
@login_required
def attendance():
    """Student attendance page with detailed records - FIXED VERSION"""
    try:
        user_id = session.get('user_id')
        
        # Get attendance summary - FIXED LOGIC
        attendance_summary = {
            'total': 0,
            'present': 0,
            'absent': 0,
            'percentage': 0
        }
        
        # Get detailed attendance records
        attendance_records = []
        subjects = []
        
        if os.path.exists(ATTENDANCE_CSV):
            try:
                df = pd.read_csv(ATTENDANCE_CSV)
                df = df.fillna('')
                
                # Filter by student ID
                student_df = df[df['student_id'] == user_id]
                
                print(f"📊 Found {len(student_df)} attendance records for student {user_id}")
                
                if len(student_df) > 0:
                    # Calculate summary
                    total = len(student_df)
                    present = len(student_df[(student_df['status'] == 'present') | (student_df['status'] == 'od')])
                    absent = len(student_df[student_df['status'] == 'absent'])
                    percentage = round((present / total) * 100) if total > 0 else 0
                    
                    attendance_summary = {
                        'total': total,
                        'present': present,
                        'absent': absent,
                        'percentage': percentage
                    }
                    
                    print(f"✅ Summary: {present}/{total} = {percentage}%")
                
                # Sort by date descending
                student_df = student_df.sort_values('date', ascending=False)
                
                # Convert to records
                attendance_records = student_df.to_dict('records')
                
                # Add day name to each record
                for record in attendance_records:
                    try:
                        date_obj = datetime.strptime(record.get('date', ''), '%Y-%m-%d')
                        record['day'] = date_obj.strftime('%A')
                    except:
                        record['day'] = 'N/A'
                    
                    # Ensure marked_at exists
                    if not record.get('marked_at'):
                        record['marked_at'] = record.get('time', 'N/A')
                
                # Extract unique subjects
                subjects = list(set([r.get('subject', '') for r in attendance_records if r.get('subject')]))
                subjects.sort()
                
                print(f"📚 Subjects: {subjects}")
                
            except Exception as e:
                print(f"❌ Error loading attendance records: {e}")
                import traceback
                traceback.print_exc()
        
        # Calculate subject-wise attendance - FIXED LOGIC
        subject_wise = []
        
        if attendance_records:
            try:
                for subject in subjects:
                    subject_records = [r for r in attendance_records if r.get('subject') == subject]
                    
                    if subject_records:
                        total = len(subject_records)
                        present = len([r for r in subject_records if r.get('status') in ['present', 'od']])
                        absent = len([r for r in subject_records if r.get('status') == 'absent'])
                        percentage = round((present / total) * 100) if total > 0 else 0
                        
                        subject_wise.append({
                            'subject': subject,
                            'total': total,
                            'present': present,
                            'absent': absent,
                            'percentage': percentage
                        })
                
                print(f"📊 Subject-wise breakdown calculated for {len(subject_wise)} subjects")
                
            except Exception as e:
                print(f"❌ Error calculating subject-wise: {e}")
                import traceback
                traceback.print_exc()
        
        return render_template('student/attendance.html',
                             attendance_summary=attendance_summary,
                             attendance_records=attendance_records,
                             subjects=subjects,
                             subject_wise=subject_wise)
    
    except Exception as e:
        print(f"❌ Error in attendance: {e}")
        import traceback
        traceback.print_exc()
        flash('Error loading page', 'error')
        return redirect(url_for('student.dashboard'))


@bp.route('/apply-od', methods=['GET', 'POST'])
@login_required
def apply_od():
    """Apply for On-Duty"""
    try:
        user_id = session.get('user_id')
        
        if request.method == 'POST':
            # Validate required fields
            required_fields = ['od_type', 'date', 'start_time', 'end_time', 'reason']
            
            for field in required_fields:
                if not request.form.get(field):
                    flash(f'Please fill in {field.replace("_", " ")}', 'error')
                    return redirect(url_for('student.apply_od'))
            
            # Validate date is not in past
            od_date = datetime.strptime(request.form.get('date'), '%Y-%m-%d').date()
            if od_date < datetime.now().date():
                flash('OD date cannot be in the past', 'error')
                return redirect(url_for('student.apply_od'))
            
            # Validate time
            start_time = request.form.get('start_time')
            end_time = request.form.get('end_time')
            
            if start_time >= end_time:
                flash('End time must be after start time', 'error')
                return redirect(url_for('student.apply_od'))
            
            # Handle file upload
            supporting_doc = None
            if 'supporting_doc' in request.files:
                file = request.files['supporting_doc']
                if file.filename:
                    # Save file
                    from werkzeug.utils import secure_filename
                    import uuid
                    
                    filename = secure_filename(file.filename)
                    unique_filename = f"{uuid.uuid4()}_{filename}"
                    
                    upload_folder = os.path.join('static', 'uploads', 'od_documents')
                    os.makedirs(upload_folder, exist_ok=True)
                    
                    file_path = os.path.join(upload_folder, unique_filename)
                    file.save(file_path)
                    
                    supporting_doc = unique_filename
            
            # Get student info
            student = get_user_by_id(user_id, 'student')
            
            # Create OD request
            od_data = {
                'student_id': user_id,
                'od_type': request.form.get('od_type'),
                'date': request.form.get('date'),
                'start_time': start_time,
                'end_time': end_time,
                'reason': request.form.get('reason'),
                'supporting_doc': supporting_doc,
                'class': student.get('class', 'N/A'),
                'department': student.get('department', 'N/A')
            }
            
            # Submit OD request
            if submit_od_request(od_data):
                flash('OD request submitted successfully!', 'success')
            else:
                flash('Failed to submit OD request', 'error')
            
            return redirect(url_for('student.apply_od'))
        
        # GET request - show form and history
        pending_requests = []
        
        try:
            if os.path.exists(OD_REQUESTS_CSV):
                df = pd.read_csv(OD_REQUESTS_CSV)
                df = df.fillna('')
                
                # Filter by student ID
                student_ods = df[df['student_id'] == user_id]
                
                # Sort by submitted_at descending
                student_ods = student_ods.sort_values('submitted_at', ascending=False)
                
                # Convert to list of dicts
                pending_requests = student_ods.to_dict('records')
        except Exception as e:
            print(f"❌ Error loading OD requests: {e}")
            import traceback
            traceback.print_exc()
        
        return render_template('student/apply_od.html',
                             pending_requests=pending_requests)
    
    except Exception as e:
        print(f"❌ Error in apply_od: {e}")
        import traceback
        traceback.print_exc()
        flash('Error loading page', 'error')
        return redirect(url_for('student.dashboard'))


@bp.route('/cancel-od/<request_id>', methods=['POST'])
@login_required
def cancel_od(request_id):
    """Cancel pending OD request"""
    try:
        user_id = session.get('user_id')
        
        if not os.path.exists(OD_REQUESTS_CSV):
            return jsonify({'success': False, 'message': 'OD file not found'}), 404
        
        # Load OD requests
        df = pd.read_csv(OD_REQUESTS_CSV)
        
        # Find the request
        mask = (df['request_id'].astype(str) == str(request_id)) & (df['student_id'] == user_id)
        
        if not mask.any():
            return jsonify({'success': False, 'message': 'OD request not found'}), 404
        
        # Check if already processed
        status = df.loc[mask, 'status'].iloc[0]
        if status != 'pending':
            return jsonify({'success': False, 'message': 'Cannot cancel processed request'}), 400
        
        # Update status to cancelled
        df.loc[mask, 'status'] = 'cancelled'
        df.loc[mask, 'remarks'] = 'Cancelled by student'
        
        # Save
        df.to_csv(OD_REQUESTS_CSV, index=False)
        
        return jsonify({'success': True, 'message': 'OD request cancelled'})
    
    except Exception as e:
        print(f"❌ Error cancelling OD: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500


@bp.route('/hostel-pass', methods=['GET', 'POST'])
@login_required
def hostel_pass():
    """Hostel pass management"""
    try:
        user_id = session.get('user_id')
        
        if request.method == 'POST':
            # Validate form data
            required_fields = ['out_date', 'out_time', 'in_date', 'in_time', 'destination', 'reason', 'emergency_contact']
            
            for field in required_fields:
                if not request.form.get(field):
                    flash(f'Please fill in {field.replace("_", " ")}', 'error')
                    return redirect(url_for('student.hostel_pass'))
            
            # Validate dates
            try:
                out_datetime = datetime.strptime(
                    f"{request.form.get('out_date')} {request.form.get('out_time')}",
                    '%Y-%m-%d %H:%M'
                )
                in_datetime = datetime.strptime(
                    f"{request.form.get('in_date')} {request.form.get('in_time')}",
                    '%Y-%m-%d %H:%M'
                )
                
                if in_datetime <= out_datetime:
                    flash('Return time must be after exit time', 'error')
                    return redirect(url_for('student.hostel_pass'))
            except ValueError:
                flash('Invalid date or time format', 'error')
                return redirect(url_for('student.hostel_pass'))
            
            # Create pass data
            pass_data = {
                'student_id': user_id,
                'out_date': request.form.get('out_date'),
                'out_time': request.form.get('out_time'),
                'in_date': request.form.get('in_date'),
                'in_time': request.form.get('in_time'),
                'destination': request.form.get('destination'),
                'reason': request.form.get('reason'),
                'emergency_contact': request.form.get('emergency_contact'),
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'status': 'pending'
            }
            
            # Submit hostel pass request
            if submit_hostel_pass(pass_data):
                flash('Hostel pass request submitted!', 'success')
            else:
                flash('Failed to submit hostel pass!', 'error')
            
            return redirect(url_for('student.hostel_pass'))
        
        # Get existing passes
        passes = get_hostel_pass(user_id)
        
        # Get active pass (most recent approved pass)
        active_pass = None
        if passes:
            # Filter approved passes
            approved_passes = [p for p in passes if p.get('status') == 'approved']
            if approved_passes:
                # Sort by created_at descending
                approved_passes.sort(key=lambda x: x.get('created_at', ''), reverse=True)
                
                # Check if still valid
                latest = approved_passes[0]
                try:
                    in_datetime = datetime.strptime(
                        f"{latest.get('in_date')} {latest.get('in_time')}",
                        '%Y-%m-%d %H:%M'
                    )
                    
                    if in_datetime > datetime.now():
                        # Generate QR code
                        try:
                            import qrcode
                            from io import BytesIO
                            import base64
                            
                            qr_data = f"HOSTEL_PASS:{latest.get('pass_id')}:{user_id}:{latest.get('out_date')}"
                            
                            qr = qrcode.QRCode(version=1, box_size=10, border=5)
                            qr.add_data(qr_data)
                            qr.make(fit=True)
                            
                            img = qr.make_image(fill_color="black", back_color="white")
                            
                            buffer = BytesIO()
                            img.save(buffer, format='PNG')
                            buffer.seek(0)
                            
                            img_str = base64.b64encode(buffer.getvalue()).decode()
                            
                            latest['qr_code'] = f"data:image/png;base64,{img_str}"
                            active_pass = latest
                        except Exception as e:
                            print(f"❌ Error generating QR code: {e}")
                except:
                    pass
        
        return render_template('student/hostel_pass.html',
                             passes=passes,
                             active_pass=active_pass)
    
    except Exception as e:
        print(f"❌ Error in hostel_pass: {e}")
        import traceback
        traceback.print_exc()
        flash('Error loading page', 'error')
        return redirect(url_for('student.dashboard'))


@bp.route('/bus-pass')
@login_required
def bus_pass():
    """Bus pass QR code generation"""
    try:
        user_id = session.get('user_id')
        
        # Generate QR code for bus pass
        qr_code = generate_bus_pass(user_id)
        
        if not qr_code:
            flash('Error generating bus pass', 'error')
            return redirect(url_for('student.dashboard'))
        
        return render_template('student/bus_pass.html', qr_code=qr_code)
    
    except Exception as e:
        print(f"❌ Error in bus_pass: {e}")
        import traceback
        traceback.print_exc()
        flash('Error loading page', 'error')
        return redirect(url_for('student.dashboard'))
    

