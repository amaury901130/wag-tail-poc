#!/usr/bin/env python
"""
Demo script showing how to use the OTP authentication system.
This demonstrates the complete flow from sending OTP to user authentication.

Usage: python demo_otp.py
"""

import requests
import json
import time


class OTPAuthDemo:
    """Demo class for OTP authentication flow"""
    
    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.access_token = None
    
    def send_otp(self, phone_number):
        """Send OTP to phone number"""
        url = f"{self.base_url}/api/auth/send-otp/"
        data = {"phone_number": phone_number}
        
        print(f"📱 Sending OTP to {phone_number}...")
        response = self.session.post(url, json=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ OTP sent successfully!")
            print(f"📞 Phone: {result['phone_number']}")
            print(f"⏰ Expires in: {result['expires_in_minutes']} minutes")
            return True
        else:
            print(f"❌ Failed to send OTP: {response.text}")
            return False
    
    def verify_otp(self, phone_number, otp_code):
        """Verify OTP and get authentication tokens"""
        url = f"{self.base_url}/api/auth/verify-otp/"
        data = {
            "phone_number": phone_number,
            "otp_code": otp_code
        }
        
        print(f"🔑 Verifying OTP {otp_code} for {phone_number}...")
        response = self.session.post(url, json=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Authentication successful!")
            
            # Store tokens
            self.access_token = result['tokens']['access']
            
            # Print user info
            user = result['user']
            print(f"👤 User: {user['phone_number']} (ID: {user['id']})")
            print(f"📅 Joined: {user['date_joined']}")
            print(f"✔️ Phone verified: {user['is_phone_verified']}")
            print(f"🆕 New user: {result['is_new_user']}")
            
            return True
        else:
            print(f"❌ Failed to verify OTP: {response.text}")
            return False
    
    def get_profile(self):
        """Get user profile using authentication token"""
        if not self.access_token:
            print("❌ No access token available. Please authenticate first.")
            return False
        
        url = f"{self.base_url}/api/auth/profile/"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        print("👤 Getting user profile...")
        response = self.session.get(url, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            user = result['user']
            print(f"✅ Profile retrieved successfully!")
            print(f"📱 Phone: {user['phone_number']}")
            print(f"👤 Username: {user['username']}")
            print(f"🆔 ID: {user['id']}")
            return True
        else:
            print(f"❌ Failed to get profile: {response.text}")
            return False
    
    def demo_flow(self, phone_number, otp_code):
        """Demonstrate the complete OTP flow"""
        print("🚀 Starting OTP Authentication Demo")
        print("=" * 50)
        
        # Step 1: Send OTP
        if not self.send_otp(phone_number):
            return
        
        print("\n" + "=" * 50)
        print("⏸️  In a real app, the user would receive the OTP via SMS")
        print(f"⏸️  For this demo, we'll use the code: {otp_code}")
        print("=" * 50 + "\n")
        
        # Wait a moment to simulate user receiving SMS
        time.sleep(1)
        
        # Step 2: Verify OTP
        if not self.verify_otp(phone_number, otp_code):
            return
        
        print("\n" + "=" * 50)
        
        # Step 3: Use authenticated endpoint
        if not self.get_profile():
            return
        
        print("\n" + "=" * 50)
        print("✅ Demo completed successfully!")
        print("🎉 User is now authenticated and can access protected endpoints")


def main():
    """Main demo function"""
    print("📋 OTP Authentication System Demo")
    print("🔧 Make sure the Django server is running on http://127.0.0.1:8000")
    print()
    
    # Demo phone number
    phone_number = "+1555000123"  # Different phone for demo
    
    # Create demo instance
    demo = OTPAuthDemo()
    
    # Send OTP first
    print("🚀 Starting OTP Authentication Demo")
    print("=" * 50)
    
    if not demo.send_otp(phone_number):
        return
    
    print("\n" + "=" * 50)
    print("⏸️  In a real app, the user would receive the OTP via SMS")
    print("⏸️  Check the Django server console output to see the OTP code")
    print("⏸️  For this demo, please enter the OTP code from the server logs:")
    
    # Get OTP from user input
    otp_code = input("🔑 Enter the OTP code: ").strip()
    
    if len(otp_code) != 6 or not otp_code.isdigit():
        print("❌ Invalid OTP format. Should be 6 digits.")
        return
    
    print("=" * 50 + "\n")
    
    # Verify OTP
    if not demo.verify_otp(phone_number, otp_code):
        return
    
    print("\n" + "=" * 50)
    
    # Use authenticated endpoint
    if not demo.get_profile():
        return
    
    print("\n" + "=" * 50)
    print("✅ Demo completed successfully!")
    print("🎉 User is now authenticated and can access protected endpoints")


if __name__ == "__main__":
    main()
