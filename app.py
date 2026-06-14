from flask import Flask, render_template, redirect, session, url_for
from routes import auth, student_routes, staff_routes, admin_routes
from routes import face_attendance, face_registration, bus_pass
from utils.email_service import init_mail
from config import Config
from auto_attendance_scheduler import start_attendance_scheduler, stop_attendance_scheduler
import atexit

app = Flask(__name__)
app.config.from_object(Config)

# Initialize Flask-Mail
mail = init_mail(app)

# Register blueprints
app.register_blueprint(auth.bp)
app.register_blueprint(student_routes.bp)
app.register_blueprint(staff_routes.bp)
app.register_blueprint(admin_routes.bp)
app.register_blueprint(face_attendance.bp)
app.register_blueprint(face_registration.bp)
app.register_blueprint(bus_pass.bp)

@app.route('/')
def index():
    if 'user_id' in session:
        role = session.get('role')
        if role == 'student':
            return redirect(url_for('student.dashboard'))
        elif role == 'staff':
            return redirect(url_for('staff.dashboard'))
        elif role == 'admin':
            return redirect(url_for('admin.dashboard'))
    return render_template('index.html')

if __name__ == '__main__':
    # Create required directories
    import os
    os.makedirs('static/uploads/student_faces', exist_ok=True)
    os.makedirs('static/uploads/od_proofs', exist_ok=True)
    os.makedirs('models/saved_models', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    
    print("\n" + "="*60)
    print("🚀 SMART ATTENDANCE SYSTEM WITH AUTO-ABSENT")
    print("="*60)
    print("\n📧 Email Configuration:")
    print(f"   Server: {app.config['MAIL_SERVER']}")
    print(f"   Port: {app.config['MAIL_PORT']}")
    print(f"   Username: {app.config['MAIL_USERNAME']}")
    print(f"   Sender: {app.config['MAIL_DEFAULT_SENDER']}")
    print("\n⚠️  IMPORTANT: Configure MAIL_USERNAME and MAIL_PASSWORD in config.py")
    print("="*60 + "\n")
    
    # Start automatic attendance scheduler
    start_attendance_scheduler(app)
    
    # Register cleanup function to stop scheduler on exit
    atexit.register(stop_attendance_scheduler)
    
    app.run(debug=True, port=5000)