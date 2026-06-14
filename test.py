"""
CSV Permission and Write Test Script
Run this to diagnose attendance storage issues
"""

import os
import csv
from datetime import datetime
import pandas as pd

def check_csv_permissions():
    """Check if CSV files are accessible"""
    
    csv_files = [
        'data/attendance.csv',
        'data/students.csv',
        'data/staff.csv',
        'data/od_requests.csv'
    ]
    
    print("\n" + "="*70)
    print("CSV FILE PERMISSION CHECK")
    print("="*70 + "\n")
    
    for filepath in csv_files:
        print(f"Checking: {filepath}")
        
        if os.path.exists(filepath):
            print(f"  ✅ File exists")
            
            # Check read permission
            if os.access(filepath, os.R_OK):
                print(f"  ✅ Readable")
            else:
                print(f"  ❌ NOT readable")
            
            # Check write permission
            if os.access(filepath, os.W_OK):
                print(f"  ✅ Writable")
            else:
                print(f"  ❌ NOT writable - FIX THIS!")
            
            # Check file size
            size = os.path.getsize(filepath)
            print(f"  📊 Size: {size} bytes")
            
            # Try to read
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    headers = next(reader)
                    print(f"  📋 Headers ({len(headers)}): {', '.join(headers[:5])}...")
                    
                    # Count rows
                    rows = list(reader)
                    print(f"  📊 Data rows: {len(rows)}")
                    
                    if len(rows) > 0:
                        print(f"  📋 Sample row: {rows[0][:3]}...")
                    
            except Exception as e:
                print(f"  ❌ Read error: {e}")
        else:
            print(f"  ❌ File does NOT exist - CREATE IT!")
        
        print()


def test_write_attendance():
    """Test writing to attendance CSV"""
    
    ATTENDANCE_CSV = 'data/attendance.csv'
    
    print("\n" + "="*70)
    print("TESTING ATTENDANCE CSV WRITE")
    print("="*70 + "\n")
    
    # Create data directory
    os.makedirs('data', exist_ok=True)
    print("✅ Data directory ensured")
    
    # Create CSV if doesn't exist
    if not os.path.exists(ATTENDANCE_CSV):
        with open(ATTENDANCE_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['student_id', 'date', 'time', 'status', 'subject', 
                           'period', 'department', 'semester', 'class', 'marked_by', 'marked_at'])
        print(f"✅ Created {ATTENDANCE_CSV}")
    
    # Test write
    test_record = [
        'TEST001',
        datetime.now().strftime('%Y-%m-%d'),
        datetime.now().strftime('%H:%M:%S'),
        'present',
        'Test Subject',
        '1',
        'Computer Science',
        '3',
        'CS-A',
        'Test Script',
        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ]
    
    print(f"\n📝 Writing test record: {test_record[:4]}...")
    
    try:
        with open(ATTENDANCE_CSV, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(test_record)
        
        print("✅ Write successful")
        
        # Verify
        with open(ATTENDANCE_CSV, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            print(f"✅ CSV now has {len(lines)} lines (including header)")
            print(f"📋 Last line: {lines[-1].strip()[:50]}...")
        
        # Verify with pandas
        df = pd.read_csv(ATTENDANCE_CSV)
        last_row = df.iloc[-1]
        
        if last_row['student_id'] == 'TEST001':
            print(f"✅ PANDAS VERIFICATION: Record found")
            print(f"   Student: {last_row['student_id']}")
            print(f"   Subject: {last_row['subject']}")
            print(f"   Status: {last_row['status']}")
        else:
            print(f"❌ PANDAS VERIFICATION FAILED")
        
        print("\n" + "="*70)
        print("✅ TEST PASSED: CSV writing works correctly!")
        print("="*70 + "\n")
        
        return True
        
    except PermissionError as e:
        print(f"\n❌ PERMISSION ERROR!")
        print(f"   {e}")
        print(f"   Solution: Close Excel or any app that has attendance.csv open")
        print("\n" + "="*70 + "\n")
        return False
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        print("\n" + "="*70 + "\n")
        return False


def check_student_data():
    """Check if students exist in CSV"""
    
    STUDENTS_CSV = 'data/students.csv'
    
    print("\n" + "="*70)
    print("CHECKING STUDENT DATA")
    print("="*70 + "\n")
    
    if not os.path.exists(STUDENTS_CSV):
        print(f"❌ Students CSV not found: {STUDENTS_CSV}")
        print(f"   Run: python clean_init.py")
        return False
    
    try:
        df = pd.read_csv(STUDENTS_CSV)
        print(f"📊 Total students: {len(df)}")
        
        if len(df) > 0:
            print(f"\n📋 Columns: {list(df.columns)}")
            print(f"\n📋 First student:")
            first = df.iloc[0]
            print(f"   ID: {first.get('user_id', 'N/A')}")
            print(f"   Name: {first.get('name', 'N/A')}")
            print(f"   Email: {first.get('email', 'N/A')}")
            print(f"   Department: {first.get('department', 'N/A')}")
            
            # Check if parent_email column exists
            if 'parent_email' in df.columns:
                print(f"   ✅ parent_email column exists")
            else:
                print(f"   ❌ parent_email column MISSING - ADD IT!")
        else:
            print(f"⚠️ No students in database")
            print(f"   Register students at: /face-registration/register")
        
        print("\n" + "="*70 + "\n")
        return True
        
    except Exception as e:
        print(f"❌ Error reading students: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all diagnostic tests"""
    
    print("\n" + "="*70)
    print("SMART ATTENDANCE SYSTEM - DIAGNOSTIC TOOL")
    print("="*70)
    
    print("\n[1/3] Checking CSV file permissions...")
    check_csv_permissions()
    
    print("\n[2/3] Testing attendance CSV write...")
    write_ok = test_write_attendance()
    
    print("\n[3/3] Checking student data...")
    student_ok = check_student_data()
    
    # Summary
    print("\n" + "="*70)
    print("DIAGNOSTIC SUMMARY")
    print("="*70)
    
    if write_ok and student_ok:
        print("✅ ALL TESTS PASSED")
        print("\nYour system should be working correctly.")
        print("If attendance still not showing:")
        print("  1. Check console output when marking attendance")
        print("  2. Verify student_id matches between files")
        print("  3. Clear browser cache and reload dashboard")
    else:
        print("❌ SOME TESTS FAILED")
        print("\nPlease fix the issues shown above, then:")
        print("  1. Close any apps that have CSV files open")
        print("  2. Run: python clean_init.py")
        print("  3. Re-run this test: python test_system.py")
    
    print("="*70 + "\n")


if __name__ == "__main__":
    main()