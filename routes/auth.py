# routes/auth.py - Complete Fixed Version
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
import hashlib
import pandas as pd
import os
from datetime import datetime

bp = Blueprint('auth', __name__, url_prefix='/auth')

STUDENTS_CSV = 'data/students.csv'
STAFF_CSV = 'data/staff.csv'

def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_user(user_id, password, role):
    """Verify user credentials"""
    try:
        print(f"\n🔍 Verifying user: {user_id} as {role}")
        
        if role == 'student':
            file_path = STUDENTS_CSV
            id_column = 'user_id'
        elif role in ['staff', 'admin']:
            file_path = STAFF_CSV
            id_column = 'user_id'
        else:
            print(f"❌ Invalid role: {role}")
            return None
        
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            return None
        
        # Read CSV
        df = pd.read_csv(file_path)
        print(f"📋 Total records in {file_path}: {len(df)}")
        print(f"📋 Columns: {df.columns.tolist()}")
        
        # Find user by user_id
        user = df[df[id_column].astype(str) == str(user_id)]
        
        if user.empty:
            print(f"❌ User {user_id} not found in {file_path}")
            return None
        
        user_data = user.iloc[0]
        print(f"✅ Found user: {user_data['name']}")
        
        # Get stored password
        stored_password = str(user_data['password'])
        
        # Hash the input password
        hashed_password = hash_password(password)
        
        print(f"🔐 Stored password: {stored_password[:20]}...")
        print(f"🔐 Input password hash: {hashed_password[:20]}...")
        
        # Check password
        if stored_password == hashed_password:
            print("✅ Password matched!")
            
            # Convert to dict
            user_dict = user_data.to_dict()
            
            # For admin role, check designation
            if role == 'admin':
                designation = str(user_dict.get('designation', '')).lower()
                if 'admin' not in designation:
                    print("❌ User is not an administrator")
                    return None
            
            return user_dict
        else:
            print("❌ Password did not match")
            return None
        
    except Exception as e:
        print(f"❌ Error verifying user: {e}")
        import traceback
        traceback.print_exc()
        return None


def add_student(student_data):
    """Add new student to CSV"""
    try:
        os.makedirs('data', exist_ok=True)
        
        # Check if file exists
        if os.path.exists(STUDENTS_CSV):
            df = pd.read_csv(STUDENTS_CSV)
            
            # Check if user_id already exists
            if student_data['user_id'] in df['user_id'].values:
                return False, "User ID already exists"
            
            # Check if email already exists
            if student_data['email'] in df['email'].values:
                return False, "Email already registered"
        else:
            # Create new DataFrame with all required columns
            df = pd.DataFrame(columns=[
                'user_id', 'name', 'email', 'parent_email', 'password',
                'phone', 'class', 'roll_no', 'department', 'semester',
                'face_registered', 'created_at'
            ])
        
        # Add default values
        student_data['face_registered'] = False
        student_data['created_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Create new student DataFrame
        new_student = pd.DataFrame([student_data])
        
        # Append to existing DataFrame
        df = pd.concat([df, new_student], ignore_index=True)
        
        # Save to CSV
        df.to_csv(STUDENTS_CSV, index=False)
        
        return True, "Student registered successfully"
        
    except Exception as e:
        print(f"❌ Error adding student: {e}")
        import traceback
        traceback.print_exc()
        return False, str(e)


def get_user_by_email(email, role):
    """Get user by email"""
    try:
        file_path = STUDENTS_CSV if role == 'student' else STAFF_CSV
        
        if not os.path.exists(file_path):
            return None
        
        df = pd.read_csv(file_path)
        user = df[df['email'].astype(str).str.lower() == email.lower()]
        
        if user.empty:
            return None
        
        return user.iloc[0].to_dict()
        
    except Exception as e:
        print(f"Error getting user by email: {e}")
        return None


def update_password(email, new_password, role):
    """Update user password"""
    try:
        file_path = STUDENTS_CSV if role == 'student' else STAFF_CSV
        
        if not os.path.exists(file_path):
            return False
        
        df = pd.read_csv(file_path)
        
        # Find user
        mask = df['email'].astype(str).str.lower() == email.lower()
        
        if not mask.any():
            return False
        
        # Hash new password
        hashed_password = hash_password(new_password)
        
        # Update password
        df.loc[mask, 'password'] = hashed_password
        
        # Save
        df.to_csv(file_path, index=False)
        
        return True
        
    except Exception as e:
        print(f"Error updating password: {e}")
        return False


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form.get('user_id', '').strip()
        password = request.form.get('password', '').strip()
        role = request.form.get('role', '').strip()
        
        print(f"\n{'='*60}")
        print(f"🔐 LOGIN ATTEMPT")
        print(f"{'='*60}")
        print(f"User ID: {user_id}")
        print(f"Role: {role}")
        print(f"{'='*60}\n")
        
        if not user_id or not password or not role:
            flash('Please fill all fields!', 'error')
            return render_template('login.html')
        
        # Verify user
        user = verify_user(user_id, password, role)
        
        if user:
            print(f"\n✅ LOGIN SUCCESSFUL for {user_id}\n")
            
            session['user_id'] = user_id
            session['role'] = role
            session['name'] = user['name']
            session['email'] = user.get('email', '')
            
            flash(f'Welcome {user["name"]}!', 'success')
            
            # Redirect based on role
            if role == 'student':
                return redirect(url_for('student.dashboard'))
            elif role == 'staff':
                return redirect(url_for('staff.dashboard'))
            elif role == 'admin':
                return redirect(url_for('admin.dashboard'))
        else:
            print(f"\n❌ LOGIN FAILED for {user_id}\n")
            flash('Invalid credentials! Please check your User ID and Password.', 'error')
            
    return render_template('login.html')


@bp.route('/student-register', methods=['GET', 'POST'])
def student_register():
    """Student Registration"""
    if request.method == 'POST':
        try:
            # Get form data
            user_id = request.form.get('user_id', '').strip()
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip().lower()
            parent_email = request.form.get('parent_email', '').strip().lower()
            phone = request.form.get('phone', '').strip()
            department = request.form.get('department', '').strip()
            semester = request.form.get('semester', '').strip()
            class_name = request.form.get('class', '').strip()
            roll_no = request.form.get('roll_no', '').strip()
            password = request.form.get('password', '').strip()
            confirm_password = request.form.get('confirm_password', '').strip()
            
            # Validation
            if not all([user_id, name, email, parent_email, department, password, confirm_password]):
                flash('Please fill all required fields!', 'error')
                return render_template('student_register.html')
            
            if password != confirm_password:
                flash('Passwords do not match!', 'error')
                return render_template('student_register.html')
            
            if len(password) < 6:
                flash('Password must be at least 6 characters long!', 'error')
                return render_template('student_register.html')
            
            # Hash password
            hashed_password = hash_password(password)
            
            # Create student data
            student_data = {
                'user_id': user_id,
                'name': name,
                'email': email,
                'parent_email': parent_email,
                'password': hashed_password,
                'phone': phone,
                'class': class_name,
                'roll_no': roll_no,
                'department': department,
                'semester': semester
            }
            
            # Add student
            success, message = add_student(student_data)
            
            if success:
                print(f"✅ New student registered: {user_id}")
                
                # Try to send emails
                try:
                    from utils.email_service import send_registration_email, send_parent_notification
                    send_registration_email(email, name, user_id, password)
                    send_parent_notification(parent_email, name, user_id)
                except Exception as e:
                    print(f"⚠️ Email sending failed: {e}")
                
                flash('Registration successful! Please login.', 'success')
                return redirect(url_for('auth.login'))
            else:
                flash(f'Registration failed: {message}', 'error')
                return render_template('student_register.html')
            
        except Exception as e:
            print(f"❌ Registration error: {e}")
            import traceback
            traceback.print_exc()
            flash('Registration failed! Please try again.', 'error')
            return render_template('student_register.html')
    
    return render_template('student_register.html')


@bp.route('/staff-register', methods=['GET', 'POST'])
def staff_register():
    """Staff Registration"""
    if request.method == 'POST':
        try:
            user_id = request.form.get('user_id', '').strip()
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip()
            phone = request.form.get('phone', '').strip()
            department = request.form.get('department', '').strip()
            designation = request.form.get('designation', '').strip()
            password = request.form.get('password', '').strip()
            confirm_password = request.form.get('confirm_password', '').strip()
            
            if not all([user_id, name, email, phone, department, designation, password, confirm_password]):
                flash('Please fill all fields!', 'error')
                return render_template('staff_register.html')
            
            if password != confirm_password:
                flash('Passwords do not match!', 'error')
                return render_template('staff_register.html')
            
            if len(password) < 6:
                flash('Password must be at least 6 characters long!', 'error')
                return render_template('staff_register.html')
            
            # Check if exists
            if os.path.exists(STAFF_CSV):
                df = pd.read_csv(STAFF_CSV)
                if user_id in df['user_id'].values:
                    flash('User ID already exists!', 'error')
                    return render_template('staff_register.html')
                if email in df['email'].values:
                    flash('Email already registered!', 'error')
                    return render_template('staff_register.html')
            else:
                df = pd.DataFrame(columns=['user_id', 'name', 'email', 'phone', 'department', 'designation', 'password'])
            
            # Hash password
            hashed_password = hash_password(password)
            
            # Create new staff
            new_staff = pd.DataFrame([{
                'user_id': user_id,
                'name': name,
                'email': email,
                'phone': phone,
                'department': department,
                'designation': designation,
                'password': hashed_password
            }])
            
            df = pd.concat([df, new_staff], ignore_index=True)
            df.to_csv(STAFF_CSV, index=False)
            
            print(f"✅ New staff registered: {user_id}")
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            print(f"❌ Registration error: {e}")
            flash('Registration failed!', 'error')
    
    return render_template('staff_register.html')


@bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Forgot Password"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        role = request.form.get('role', 'student').strip()
        
        if not email:
            flash('Please enter your email!', 'error')
            return render_template('reset_password.html')
        
        user = get_user_by_email(email, role)
        
        if user:
            try:
                from utils.email_service import send_password_reset_email, generate_reset_token
                token = generate_reset_token(email)
                reset_url = url_for('auth.reset_password', token=token, _external=True)
                send_password_reset_email(email, reset_url, user['name'])
                flash('Password reset link sent to your email!', 'success')
            except Exception as e:
                print(f"❌ Failed to send email: {e}")
                flash('Failed to send email. Please try again.', 'error')
        else:
            flash('If email exists, reset link has been sent!', 'info')
        
        return redirect(url_for('auth.login'))
    
    return render_template('reset_password.html')


@bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Reset Password"""
    try:
        from utils.email_service import verify_reset_token, send_password_changed_notification
        
        email = verify_reset_token(token)
        
        if not email:
            flash('Invalid or expired reset link!', 'error')
            return redirect(url_for('auth.forgot_password'))
        
        if request.method == 'POST':
            new_password = request.form.get('password', '').strip()
            confirm_password = request.form.get('confirm_password', '').strip()
            
            if not new_password or not confirm_password:
                flash('Please fill all fields!', 'error')
                return render_template('reset_password.html', token=token)
            
            if new_password != confirm_password:
                flash('Passwords do not match!', 'error')
                return render_template('reset_password.html', token=token)
            
            if len(new_password) < 6:
                flash('Password must be at least 6 characters!', 'error')
                return render_template('reset_password.html', token=token)
            
            user = get_user_by_email(email, 'student') or get_user_by_email(email, 'staff')
            
            if not user:
                flash('User not found!', 'error')
                return redirect(url_for('auth.login'))
            
            role = 'staff' if 'designation' in user else 'student'
            
            if update_password(email, new_password, role):
                try:
                    send_password_changed_notification(email, user['name'])
                except:
                    pass
                
                flash('Password changed successfully! Please login.', 'success')
                return redirect(url_for('auth.login'))
            else:
                flash('Failed to update password!', 'error')
        
        return render_template('reset_password.html', token=token, email=email)
        
    except Exception as e:
        print(f"Error in reset password: {e}")
        flash('An error occurred!', 'error')
        return redirect(url_for('auth.login'))


@bp.route('/logout')
def logout():
    """Logout"""
    user_name = session.get('name', 'User')
    session.clear()
    flash(f'Goodbye {user_name}! Logged out successfully.', 'success')
    return redirect(url_for('index'))


# Initialize CSV files
def init_csv_files():
    """Initialize CSV files"""
    os.makedirs('data', exist_ok=True)
    
    if not os.path.exists(STAFF_CSV):
        df = pd.DataFrame(columns=['user_id', 'name', 'email', 'phone', 'department', 'designation', 'password'])
        df.to_csv(STAFF_CSV, index=False)
        print(f"✅ Created {STAFF_CSV}")
    
    if not os.path.exists(STUDENTS_CSV):
        df = pd.DataFrame(columns=['user_id', 'name', 'email', 'parent_email', 'password', 'phone', 'class', 'roll_no', 'department', 'semester', 'face_registered', 'created_at'])
        df.to_csv(STUDENTS_CSV, index=False)
        print(f"✅ Created {STUDENTS_CSV}")

# Initialize files when module is imported
init_csv_files()