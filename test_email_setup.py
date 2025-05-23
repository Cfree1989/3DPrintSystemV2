#!/usr/bin/env python3
"""
Test script to verify email configuration is working properly.
Run this after setting up your .env file.
"""

from app import create_app
from app.services.email_service import get_email_status, send_email

def test_email_config():
    app = create_app()
    with app.app_context():
        print("🔧 Testing Email Configuration...")
        print("-" * 50)
        
        # Check configuration status
        status = get_email_status()
        
        if status['configured']:
            print("✅ Email is properly configured!")
            print(f"📧 Server: {status['server']}")
            print(f"📤 Sender: {status['sender']}")
            
            # Optionally test sending an email to yourself
            test_email = input("\n📬 Enter your email to send a test message (or press Enter to skip): ").strip()
            
            if test_email:
                print(f"\n📮 Sending test email to {test_email}...")
                
                success = send_email(
                    to=test_email,
                    subject="3D Print System - Email Test",
                    html_content="""
                    <h2>🎉 Email Configuration Test</h2>
                    <p>Congratulations! Your 3D Print System email configuration is working correctly.</p>
                    <p>You should now receive email notifications for:</p>
                    <ul>
                        <li>Job approvals (requiring student confirmation)</li>
                        <li>Job rejections (with reasons)</li>
                        <li>Job completions (ready for pickup)</li>
                    </ul>
                    <p>This test was sent from your 3D Print System.</p>
                    """
                )
                
                if success:
                    print("✅ Test email sent successfully!")
                    print("📧 Check your inbox to confirm delivery.")
                else:
                    print("❌ Test email failed to send.")
                    print("🔍 Check your email credentials and try again.")
            else:
                print("⏭️  Skipping test email send.")
                
        else:
            print("❌ Email not configured properly")
            print(f"ℹ️  {status['message']}")
            print("\n🔧 To fix this:")
            print("1. Create a .env file in your project root")
            print("2. Add your email settings (see instructions)")
            print("3. Restart your Flask app")
            print("4. Run this test again")

if __name__ == "__main__":
    test_email_config() 