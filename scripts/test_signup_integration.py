import requests
import json
import time
from typing import Dict, Any

class SignupTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def test_signup(self, user_data: Dict[str, str]) -> Dict[str, Any]:
        """Test user signup"""
        try:
            response = self.session.post(
                f"{self.base_url}/signup",
                data=user_data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=10
            )
            
            return {
                'status_code': response.status_code,
                'response': response.json() if response.headers.get('content-type') == 'application/json' else response.text,
                'success': response.status_code == 200
            }
        except requests.exceptions.RequestException as e:
            return {
                'status_code': 0,
                'response': f"Connection error: {str(e)}",
                'success': False
            }
    
    def test_signin(self, email: str, password: str) -> Dict[str, Any]:
        """Test user signin"""
        try:
            response = self.session.post(
                f"{self.base_url}/signin",
                data={'email': email, 'password': password},
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=10
            )
            
            return {
                'status_code': response.status_code,
                'response': response.json() if response.headers.get('content-type') == 'application/json' else response.text,
                'success': response.status_code == 200
            }
        except requests.exceptions.RequestException as e:
            return {
                'status_code': 0,
                'response': f"Connection error: {str(e)}",
                'success': False
            }
    
    def run_comprehensive_tests(self):
        """Run comprehensive signup and signin tests"""
        print("🧪 FarmConnect Signup Integration Tests")
        print("=" * 50)
        
        # Test 1: Valid signup
        print("\n📝 Test 1: Valid Signup")
        valid_user = {
            'fullName': 'Test Farmer',
            'email': f'test.farmer.{int(time.time())}@example.com',
            'password': 'securepassword123',
            'confirmPassword': 'securepassword123',
            'farmingExperience': 'beginner',
            'farmType': 'crop',
            'location': 'Test Valley, CA'
        }
        
        result = self.test_signup(valid_user)
        if result['success'] and result['response'].get('success'):
            print("✅ Valid signup successful")
            print(f"   User ID: {result['response']['user']['id']}")
            print(f"   Email: {result['response']['user']['email']}")
            
            # Test signin with new user
            print("\n🔐 Test 1b: Signin with new user")
            signin_result = self.test_signin(valid_user['email'], valid_user['password'])
            if signin_result['success'] and signin_result['response'].get('success'):
                print("✅ Signin successful")
                print(f"   Welcome: {signin_result['response']['user']['full_name']}")
            else:
                print(f"❌ Signin failed: {signin_result['response']}")
        else:
            print(f"❌ Valid signup failed: {result['response']}")
        
        # Test 2: Duplicate email
        print("\n📝 Test 2: Duplicate Email")
        duplicate_result = self.test_signup(valid_user)
        if not duplicate_result['success'] or not duplicate_result['response'].get('success'):
            print("✅ Duplicate email correctly rejected")
            print(f"   Message: {duplicate_result['response'].get('message', 'Unknown error')}")
        else:
            print("❌ Duplicate email was incorrectly accepted")
        
        # Test 3: Invalid email format
        print("\n📝 Test 3: Invalid Email Format")
        invalid_email_user = valid_user.copy()
        invalid_email_user['email'] = 'invalid-email-format'
        
        result = self.test_signup(invalid_email_user)
        if not result['success'] or not result['response'].get('success'):
            print("✅ Invalid email format correctly rejected")
            print(f"   Message: {result['response'].get('message', 'Unknown error')}")
        else:
            print("❌ Invalid email format was incorrectly accepted")
        
        # Test 4: Password mismatch
        print("\n📝 Test 4: Password Mismatch")
        mismatch_user = valid_user.copy()
        mismatch_user['email'] = f'mismatch.{int(time.time())}@example.com'
        mismatch_user['confirmPassword'] = 'differentpassword'
        
        result = self.test_signup(mismatch_user)
        if not result['success'] or not result['response'].get('success'):
            print("✅ Password mismatch correctly rejected")
            print(f"   Message: {result['response'].get('message', 'Unknown error')}")
        else:
            print("❌ Password mismatch was incorrectly accepted")
        
        # Test 5: Missing required fields
        print("\n📝 Test 5: Missing Required Fields")
        incomplete_user = {
            'fullName': 'Incomplete User',
            'email': f'incomplete.{int(time.time())}@example.com',
            'password': 'password123'
            # Missing confirmPassword, farmingExperience, farmType, location
        }
        
        result = self.test_signup(incomplete_user)
        if not result['success'] or not result['response'].get('success'):
            print("✅ Missing fields correctly rejected")
            print(f"   Message: {result['response'].get('message', 'Unknown error')}")
        else:
            print("❌ Missing fields were incorrectly accepted")
        
        # Test 6: Short password
        print("\n📝 Test 6: Short Password")
        short_password_user = valid_user.copy()
        short_password_user['email'] = f'short.{int(time.time())}@example.com'
        short_password_user['password'] = '123'
        short_password_user['confirmPassword'] = '123'
        
        result = self.test_signup(short_password_user)
        if not result['success'] or not result['response'].get('success'):
            print("✅ Short password correctly rejected")
            print(f"   Message: {result['response'].get('message', 'Unknown error')}")
        else:
            print("❌ Short password was incorrectly accepted")
        
        # Test 7: Invalid farming experience
        print("\n📝 Test 7: Invalid Farming Experience")
        invalid_exp_user = valid_user.copy()
        invalid_exp_user['email'] = f'invalid.exp.{int(time.time())}@example.com'
        invalid_exp_user['farmingExperience'] = 'invalid_experience'
        
        result = self.test_signup(invalid_exp_user)
        if not result['success'] or not result['response'].get('success'):
            print("✅ Invalid farming experience correctly rejected")
            print(f"   Message: {result['response'].get('message', 'Unknown error')}")
        else:
            print("❌ Invalid farming experience was incorrectly accepted")
        
        print("\n" + "=" * 50)
        print("🎯 Integration tests completed!")
        print("💡 Make sure your Python server is running on localhost:8000")

if __name__ == "__main__":
    tester = SignupTester()
    tester.run_comprehensive_tests()
