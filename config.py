# config.py - Configuration file for Smart Attendance System

class Config:
    """Flask configuration"""
    
    # Secret key for session management
    SECRET_KEY = 'your-secret-key-here-change-this-to-random-string'
    
    # ==================== EMAIL CONFIGURATION ====================
    # Gmail SMTP Settings (Recommended)
    # You need to create an App Password if using Gmail
    # Steps:
    # 1. Go to Google Account Settings
    # 2. Enable 2-Factor Authentication
    # 3. Go to Security > App Passwords
    # 4. Generate new app password for "Mail"
    # 5. Use that password below (16-character password without spaces)
    
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    
    # IMPORTANT: Replace these with your actual email credentials
    MAIL_USERNAME = 'bloghosting34@gmail.com'  # Your Gmail address
    MAIL_PASSWORD = 'fcmipzqwssucvdtv'  # 16-character App Password from Google
    MAIL_DEFAULT_SENDER = 'bloghosting34@gmail.com'  # Same as MAIL_USERNAME
    
    # ==================== ALTERNATIVE EMAIL PROVIDERS ====================
    
    # Option 1: Outlook/Hotmail
    # MAIL_SERVER = 'smtp-mail.outlook.com'
    # MAIL_PORT = 587
    # MAIL_USE_TLS = True
    # MAIL_USERNAME = 'your-email@outlook.com'
    # MAIL_PASSWORD = 'your-password'
    # MAIL_DEFAULT_SENDER = 'your-email@outlook.com'
    
    # Option 2: Yahoo Mail
    # MAIL_SERVER = 'smtp.mail.yahoo.com'
    # MAIL_PORT = 587
    # MAIL_USE_TLS = True
    # MAIL_USERNAME = 'your-email@yahoo.com'
    # MAIL_PASSWORD = 'your-app-password'  # Generate from Yahoo Account Security
    # MAIL_DEFAULT_SENDER = 'your-email@yahoo.com'
    
    # Option 3: Custom SMTP Server
    # MAIL_SERVER = 'smtp.yourdomain.com'
    # MAIL_PORT = 587
    # MAIL_USE_TLS = True
    # MAIL_USERNAME = 'your-email@yourdomain.com'
    # MAIL_PASSWORD = 'your-password'
    # MAIL_DEFAULT_SENDER = 'your-email@yourdomain.com'
    
    # ==================== ATTENDANCE SETTINGS ====================
    ATTENDANCE_WINDOW_MINUTES = 5  # Students must mark within 5 minutes
    
    # ==================== UPLOAD SETTINGS ====================
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = 'static/uploads'


# ==================== TESTING CONFIGURATION ====================
# For testing without actual email sending, you can use these settings:

class TestConfig(Config):
    """Test configuration without real email sending"""
    MAIL_SUPPRESS_SEND = True  # Prevents actual email sending
    TESTING = True