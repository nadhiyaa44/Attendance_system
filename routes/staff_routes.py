from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from utils.database import (
    get_od_requests, approve_od_request, reject_od_request,
    get_attendance, get_user_by_id, STUDENTS_CSV, ATTENDANCE_CSV, OD_REQUESTS_CSV
)
from datetime import datetime, date, timedelta
import pandas as pd
import os

bp = Blueprint('staff', __name__, url_prefix='/staff')

def staff_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'staff':
            flash('Access denied!', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def enrich_od_requests(od_requests):
    """Enrich OD requests with student information"""
    enriched = []
    
    try:
        # Load students data
        if not os.path.exists(STUDENTS_CSV):
            return od_requests
        
        students_df = pd.read_csv(STUDENTS_CSV)
        
        for od in od_requests:
            # Get student info
            student_id = od.get('student_id', '')
            student_info = students_df[students_df['user_id'] == student_id]
            
            if not student_info.empty:
                student = student_info.iloc[0]
                od['student_name'] = student.get('name', 'Unknown')
                od['class'] = student.get('class', 'N/A')
                od['department'] = student.get('department', 'N/A')
            else:
                od['student_name'] = 'Unknown Student'
                od['class'] = 'N/A'
                od['department'] = 'N/A'
            
            enriched.append(od)
        
        return enriched
        
    except Exception as e:
        print(f"❌ Error enriching OD requests: {e}")
        import traceback
        traceback.print_exc()
        return od_requests


def enrich_attendance_records(attendance_records):
    """Enrich attendance records with student names"""
    enriched = []
    
    try:
        # Load students data
        if not os.path.exists(STUDENTS_CSV):
            return attendance_records
        
        students_df = pd.read_csv(STUDENTS_CSV)
        
        for record in attendance_records:
            # Get student info
            student_id = record.get('student_id', '')
            student_info = students_df[students_df['user_id'] == student_id]
            
            if not student_info.empty:
                student = student_info.iloc[0]
                record['student_name'] = student.get('name', 'Unknown')
                record['class'] = student.get('class', record.get('class', 'N/A'))
            else:
                record['student_name'] = 'Unknown Student'
                record['class'] = record.get('class', 'N/A')
            
            # Format marked_by
            if not record.get('marked_by'):
                record['marked_by'] = 'System'
            
            enriched.append(record)
        
        return enriched
        
    except Exception as e:
        print(f"❌ Error enriching attendance: {e}")
        import traceback
        traceback.print_exc()
        return attendance_records


@bp.route('/dashboard')
@staff_required
def dashboard():
    """Staff Dashboard with all required data - FIXED VERSION"""
    try:
        # Get session data
        name = session.get('name', 'Staff')
        user_id = session.get('user_id', '')
        department = session.get('department', 'General')
        
        print(f"\n{'='*60}")
        print(f"📊 STAFF DASHBOARD LOADING")
        print(f"{'='*60}")
        print(f"Name: {name}")
        print(f"User ID: {user_id}")
        print(f"Department: {department}")
        
        # Current date
        current_date = datetime.now().strftime('%A, %B %d, %Y')
        
        # Get all students count
        total_students = 0
        if os.path.exists(STUDENTS_CSV):
            df = pd.read_csv(STUDENTS_CSV)
            # Filter by department if not admin
            if department and department != 'General' and department != 'Administration':
                df = df[df['department'] == department]
            total_students = len(df)
            print(f"👥 Total students: {total_students}")
        
        # Get today's attendance
        today_attendance = 0
        if os.path.exists(ATTENDANCE_CSV):
            try:
                att_df = pd.read_csv(ATTENDANCE_CSV)
                att_df = att_df.fillna('')
                today = datetime.now().strftime('%Y-%m-%d')
                
                # Get today's records
                today_att = att_df[att_df['date'] == today]
                
                # Filter by department if needed
                if department and department != 'General' and department != 'Administration':
                    today_att = today_att[today_att['department'] == department]
                
                if len(today_att) > 0:
                    # Count unique students who attended
                    unique_students = today_att['student_id'].nunique()
                    
                    # Count present students (including OD)
                    present = len(today_att[(today_att['status'] == 'present') | (today_att['status'] == 'od')])
                    
                    # Calculate percentage based on unique students
                    if unique_students > 0:
                        today_attendance = round((present / unique_students) * 100)
                    
                    print(f"📊 Today's attendance: {present}/{unique_students} = {today_attendance}%")
            except Exception as e:
                print(f"❌ Error calculating today's attendance: {e}")
                import traceback
                traceback.print_exc()
        
        # Get pending OD requests
        pending_ods = 0
        pending_od_list = []
        try:
            all_ods = get_od_requests(status='pending')
            # Enrich with student info
            all_ods = enrich_od_requests(all_ods)
            
            # Filter by department if needed
            if department and department != 'General' and department != 'Administration':
                all_ods = [od for od in all_ods if od.get('department') == department]
            
            pending_od_list = all_ods[:5]  # Top 5
            pending_ods = len(all_ods)
            print(f"📋 Pending ODs: {pending_ods}")
        except Exception as e:
            print(f"❌ Error loading ODs: {e}")
        
        # Classes today (placeholder)
        classes_today = 6
        
        print(f"✅ Dashboard data prepared successfully")
        print(f"{'='*60}\n")
        
        # Create session dict for template
        session_data = {
            'user_id': user_id,
            'name': name,
            'department': department,
            'role': session.get('role', 'staff')
        }
        
        return render_template('staff/dashboard.html',
                             name=name,
                             current_date=current_date,
                             total_students=total_students,
                             today_attendance=today_attendance,
                             pending_ods=pending_ods,
                             classes_today=classes_today,
                             pending_od_list=pending_od_list,
                             session=session_data)
    
    except Exception as e:
        print(f"❌ ERROR IN STAFF DASHBOARD: {e}")
        import traceback
        traceback.print_exc()
        flash('Error loading dashboard. Please try again.', 'error')
        return redirect(url_for('auth.login'))


@bp.route('/view-attendance')
@staff_required
def view_attendance():
    """View attendance with filters"""
    try:
        # Get filter parameters
        selected_class = request.args.get('class', '')
        selected_date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
        selected_period = request.args.get('period', '')
        department = session.get('department', 'General')
        
        # Get attendance data
        attendance = []
        attendance_summary = {
            'total': 0,
            'present': 0,
            'absent': 0,
            'percentage': 0
        }
        
        if os.path.exists(ATTENDANCE_CSV):
            try:
                df = pd.read_csv(ATTENDANCE_CSV)
                df = df.fillna('')
                
                # Apply filters
                if selected_date:
                    df = df[df['date'] == selected_date]
                
                if selected_class:
                    df = df[df['class'] == selected_class]
                
                if selected_period:
                    df = df[df['period'] == selected_period]
                
                # Filter by department
                if department and department != 'General' and department != 'Administration':
                    df = df[df['department'] == department]
                
                if len(df) > 0:
                    # Calculate summary
                    total = len(df)
                    present = len(df[(df['status'] == 'present') | (df['status'] == 'od')])
                    absent = len(df[df['status'] == 'absent'])
                    percentage = round((present / total) * 100, 2) if total > 0 else 0
                    
                    attendance_summary = {
                        'total': total,
                        'present': present,
                        'absent': absent,
                        'percentage': percentage
                    }
                    
                    # Convert to records
                    attendance = df.to_dict('records')
                    
                    # Enrich with student names
                    attendance = enrich_attendance_records(attendance)
                
            except Exception as e:
                print(f"❌ Error loading attendance: {e}")
                import traceback
                traceback.print_exc()
        
        # Get defaulters
        defaulters = []
        try:
            if os.path.exists(ATTENDANCE_CSV) and os.path.exists(STUDENTS_CSV):
                att_df = pd.read_csv(ATTENDANCE_CSV)
                att_df = att_df.fillna('')
                students_df = pd.read_csv(STUDENTS_CSV)
                
                # Filter by department
                if department and department != 'General' and department != 'Administration':
                    students_df = students_df[students_df['department'] == department]
                
                for _, student in students_df.iterrows():
                    student_id = student['user_id']
                    student_att = att_df[att_df['student_id'] == student_id]
                    
                    if len(student_att) > 0:
                        total = len(student_att)
                        present = len(student_att[(student_att['status'] == 'present') | (student_att['status'] == 'od')])
                        absent = len(student_att[student_att['status'] == 'absent'])
                        percentage = round((present / total) * 100, 2)
                        
                        if percentage < 75:
                            defaulters.append({
                                'student_id': student_id,
                                'name': student.get('name', 'Unknown'),
                                'class': student.get('class', 'N/A'),
                                'total': total,
                                'present': present,
                                'absent': absent,
                                'percentage': percentage
                            })
                
        except Exception as e:
            print(f"❌ Error loading defaulters: {e}")
        
        return render_template('staff/view_attendance.html',
                             attendance=attendance,
                             attendance_summary=attendance_summary,
                             defaulters=defaulters,
                             selected_date=selected_date)
    
    except Exception as e:
        print(f"❌ Error in view_attendance: {e}")
        import traceback
        traceback.print_exc()
        flash('Error loading attendance data', 'error')
        return redirect(url_for('staff.dashboard'))


@bp.route('/od-approval')
@staff_required
def od_approval():
    """OD Approval Page"""
    try:
        department = session.get('department', 'General')
        current_date = datetime.now().strftime('%A, %B %d, %Y')
        
        # Get pending requests
        pending_requests = get_od_requests(status='pending')
        pending_requests = enrich_od_requests(pending_requests)
        
        # Filter by department
        if department and department != 'General' and department != 'Administration':
            pending_requests = [od for od in pending_requests if od.get('department') == department]
        
        # Get history (approved/rejected today)
        history = []
        try:
            all_requests = get_od_requests()
            all_requests = enrich_od_requests(all_requests)
            
            # Filter by department
            if department and department != 'General' and department != 'Administration':
                all_requests = [od for od in all_requests if od.get('department') == department]
            
            # Get today's processed requests
            today = datetime.now().strftime('%Y-%m-%d')
            history = [
                od for od in all_requests 
                if od.get('status') in ['approved', 'rejected'] 
                and od.get('approved_at', '').startswith(today)
            ]
            
        except Exception as e:
            print(f"❌ Error loading history: {e}")
        
        return render_template('staff/od_approval.html',
                             pending_requests=pending_requests,
                             history=history,
                             current_date=current_date)
    
    except Exception as e:
        print(f"❌ Error in od_approval: {e}")
        import traceback
        traceback.print_exc()
        flash('Error loading OD approvals', 'error')
        return redirect(url_for('staff.dashboard'))


@bp.route('/od-approve/<request_id>', methods=['POST'])
@staff_required
def od_approve(request_id):
    """Approve OD request"""
    try:
        staff_id = session.get('user_id')
        staff_name = session.get('name', 'Staff')
        
        success = approve_od_request(request_id, staff_id, staff_name)
        
        if success:
            return jsonify({'success': True, 'message': 'OD approved successfully'})
        else:
            return jsonify({'success': False, 'message': 'Failed to approve OD'}), 400
    
    except Exception as e:
        print(f"❌ Error approving OD: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500


@bp.route('/od-reject/<request_id>', methods=['POST'])
@staff_required
def od_reject(request_id):
    """Reject OD request"""
    try:
        staff_id = session.get('user_id')
        staff_name = session.get('name', 'Staff')
        
        # Get remarks from request
        data = request.get_json()
        remarks = data.get('remarks', 'No reason provided')
        
        success = reject_od_request(request_id, staff_id, staff_name, remarks)
        
        if success:
            return jsonify({'success': True, 'message': 'OD rejected successfully'})
        else:
            return jsonify({'success': False, 'message': 'Failed to reject OD'}), 400
    
    except Exception as e:
        print(f"❌ Error rejecting OD: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500


@bp.route('/reports')
@staff_required
def reports():
    """Reports and Analytics"""
    try:
        department = session.get('department', 'General')
        current_date = datetime.now().strftime('%A, %B %d, %Y')
        
        # Get report parameters
        report_type = request.args.get('type', 'attendance')
        start_date = request.args.get('start_date', '')
        end_date = request.args.get('end_date', '')
        selected_class = request.args.get('class', '')
        
        # Calculate statistics
        stats = {
            'total_students': 0,
            'avg_attendance': 0,
            'total_attendance_records': 0,
            'pending_ods': 0,
            'approved_ods': 0,
            'rejected_ods': 0
        }
        
        # Get students count
        if os.path.exists(STUDENTS_CSV):
            df = pd.read_csv(STUDENTS_CSV)
            if department and department != 'General' and department != 'Administration':
                df = df[df['department'] == department]
            stats['total_students'] = len(df)
        
        # Get attendance stats
        if os.path.exists(ATTENDANCE_CSV):
            try:
                df = pd.read_csv(ATTENDANCE_CSV)
                df = df.fillna('')
                
                if department and department != 'General' and department != 'Administration':
                    df = df[df['department'] == department]
                
                stats['total_attendance_records'] = len(df)
                
                if len(df) > 0:
                    present = len(df[(df['status'] == 'present') | (df['status'] == 'od')])
                    stats['avg_attendance'] = round((present / len(df)) * 100, 2)
                
            except Exception as e:
                print(f"❌ Error calculating stats: {e}")
        
        # Get OD stats
        try:
            all_ods = get_od_requests()
            if department and department != 'General' and department != 'Administration':
                # Filter by department (would need to enrich first)
                all_ods = enrich_od_requests(all_ods)
                all_ods = [od for od in all_ods if od.get('department') == department]
            
            stats['pending_ods'] = len([od for od in all_ods if od.get('status') == 'pending'])
            stats['approved_ods'] = len([od for od in all_ods if od.get('status') == 'approved'])
            stats['rejected_ods'] = len([od for od in all_ods if od.get('status') == 'rejected'])
            
        except Exception as e:
            print(f"❌ Error loading OD stats: {e}")
        
        # Generate report data based on type
        report_data = None
        
        if report_type and start_date and end_date:
            # TODO: Generate specific reports based on type
            pass
        
        return render_template('staff/reports.html',
                             stats=stats,
                             current_date=current_date,
                             report_type=report_type,
                             start_date=start_date,
                             end_date=end_date,
                             report_data=report_data)
    
    except Exception as e:
        print(f"❌ Error in reports: {e}")
        import traceback
        traceback.print_exc()
        flash('Error loading reports', 'error')
        return redirect(url_for('staff.dashboard'))


@bp.route('/student-attendance/<student_id>')
@staff_required
def student_attendance(student_id):
    """View individual student attendance"""
    try:
        # Get student info
        student = get_user_by_id(student_id, 'student')
        
        if not student:
            flash('Student not found', 'error')
            return redirect(url_for('staff.od_approval'))
        
        # Get student's attendance records
        attendance_records = []
        attendance_summary = {
            'total': 0,
            'present': 0,
            'absent': 0,
            'od': 0,
            'percentage': 0
        }
        
        if os.path.exists(ATTENDANCE_CSV):
            try:
                df = pd.read_csv(ATTENDANCE_CSV)
                df = df.fillna('')
                
                # Filter by student ID
                student_att = df[df['student_id'] == student_id]
                
                if len(student_att) > 0:
                    total = len(student_att)
                    present = len(student_att[student_att['status'] == 'present'])
                    absent = len(student_att[student_att['status'] == 'absent'])
                    od = len(student_att[student_att['status'] == 'od'])
                    
                    # OD counts as present
                    total_present = present + od
                    percentage = round((total_present / total) * 100, 2) if total > 0 else 0
                    
                    attendance_summary = {
                        'total': total,
                        'present': present,
                        'absent': absent,
                        'od': od,
                        'percentage': percentage
                    }
                    
                    # Sort by date descending
                    student_att = student_att.sort_values('date', ascending=False)
                    attendance_records = student_att.to_dict('records')
                
            except Exception as e:
                print(f"❌ Error loading attendance: {e}")
                import traceback
                traceback.print_exc()
        
        # Get subject-wise attendance
        subject_wise = []
        if len(attendance_records) > 0:
            try:
                df = pd.DataFrame(attendance_records)
                
                for subject in df['subject'].unique():
                    if not subject:
                        continue
                    
                    subject_att = df[df['subject'] == subject]
                    total = len(subject_att)
                    present = len(subject_att[(subject_att['status'] == 'present') | (subject_att['status'] == 'od')])
                    absent = len(subject_att[subject_att['status'] == 'absent'])
                    percentage = round((present / total) * 100, 2) if total > 0 else 0
                    
                    subject_wise.append({
                        'subject': subject,
                        'total': total,
                        'present': present,
                        'absent': absent,
                        'percentage': percentage
                    })
                
                # Sort by percentage
                subject_wise = sorted(subject_wise, key=lambda x: x['percentage'], reverse=True)
                
            except Exception as e:
                print(f"❌ Error calculating subject-wise: {e}")
        
        return render_template('staff/student_attendance.html',
                             student=student,
                             attendance_summary=attendance_summary,
                             attendance_records=attendance_records,
                             subject_wise=subject_wise)
    
    except Exception as e:
        print(f"❌ Error in student_attendance: {e}")
        import traceback
        traceback.print_exc()
        flash('Error loading student attendance', 'error')
        return redirect(url_for('staff.od_approval'))