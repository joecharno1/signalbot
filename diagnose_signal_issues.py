#!/usr/bin/env python3
"""
Signal Registration Diagnostic Tool

This script diagnoses why captcha registration isn't working and suggests solutions.
"""

import subprocess
import requests
import json
import time
import re

class SignalDiagnostic:
    """Diagnose Signal registration issues"""
    
    def __init__(self):
        self.api_base = "http://localhost:8080/v1"
        self.phone_number = "+13045641145"
        self.issues_found = []
        self.solutions = []
    
    def run_command(self, cmd):
        """Run a command and return output"""
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result.stdout, result.stderr, result.returncode
        except Exception as e:
            return None, str(e), 1
    
    def check_docker_status(self):
        """Check Docker container status"""
        print("🔍 Checking Docker Status...")
        print("-" * 40)
        
        # Check if Docker is running
        stdout, stderr, code = self.run_command("docker --version")
        if code != 0:
            self.issues_found.append("Docker not installed or not running")
            self.solutions.append("Install Docker Desktop and ensure it's running")
            return False
        
        print(f"✅ Docker version: {(stdout or '').strip()}")
        
        # Check signal-api container
        stdout, stderr, code = self.run_command("docker ps --filter name=signal-api")
        if "signal-api" not in (stdout or ""):
            self.issues_found.append("signal-api container not running")
            self.solutions.append("Run: docker-compose up -d")
            return False
        
        print("✅ signal-api container is running")
        
        # Check container logs for errors
        stdout, stderr, code = self.run_command("docker logs signal-api --tail 20")
        if "ERROR" in (stdout or "") or "FATAL" in (stdout or ""):
            print("⚠️  Found errors in container logs:")
            print(stdout)
            self.issues_found.append("Errors in signal-api container logs")
        
        return True
    
    def check_api_connectivity(self):
        """Check API connectivity and status"""
        print("\n🔍 Checking API Connectivity...")
        print("-" * 40)
        
        try:
            # Test basic connectivity
            response = requests.get(f"{self.api_base}/about", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ API is responding")
                print(f"   Version: {data.get('version', 'Unknown')}")
                print(f"   Mode: {data.get('mode', 'Unknown')}")
                
                # Check accounts
                accounts_response = requests.get(f"{self.api_base}/accounts", timeout=5)
                if accounts_response.status_code == 200:
                    accounts = accounts_response.json()
                    print(f"   Registered accounts: {len(accounts)} ({accounts})")
                    
                    if self.phone_number in accounts:
                        print(f"✅ {self.phone_number} is already registered!")
                        return "already_registered"
                
                return True
            else:
                self.issues_found.append(f"API returned status {response.status_code}")
                return False
                
        except requests.exceptions.ConnectionError:
            self.issues_found.append("Cannot connect to Signal API")
            self.solutions.append("Check if signal-api container is running on port 8080")
            return False
        except Exception as e:
            self.issues_found.append(f"API error: {e}")
            return False
    
    def test_captcha_process(self):
        """Test the captcha process step by step"""
        print("\n🔍 Testing Captcha Process...")
        print("-" * 40)
        
        # Step 1: Try direct registration to see exact error
        print("📝 Testing direct registration...")
        stdout, stderr, code = self.run_command(
            f"docker exec signal-api signal-cli -a {self.phone_number} register"
        )
        
        print(f"Exit code: {code}")
        print(f"Stdout: {stdout}")
        print(f"Stderr: {stderr}")
        
        combined_output = (stdout or "") + (stderr or "")
        
        if "Captcha required" in combined_output:
            print("✅ Registration correctly requires captcha")
            
            # Analyze what type of captcha is needed
            if "hcaptcha" in combined_output.lower():
                print("   Type: hCaptcha")
            elif "recaptcha" in combined_output.lower():
                print("   Type: reCaptcha")
            else:
                print("   Type: Unknown captcha system")
            
            return "captcha_required"
            
        elif "already registered" in combined_output.lower():
            print("✅ Number is already registered!")
            return "already_registered"
            
        elif "rate limit" in combined_output.lower() or "too many" in combined_output.lower():
            print("⚠️  Rate limited")
            self.issues_found.append("Rate limited")
            self.solutions.append("Wait 15+ minutes or use different number")
            return "rate_limited"
            
        else:
            print("❓ Unexpected response - no captcha required?")
            # Try to proceed with SMS
            if "SMS" in combined_output or "voice" in combined_output:
                print("✅ Registration may have worked without captcha!")
                return "no_captcha_needed"
            else:
                self.issues_found.append(f"Unexpected registration response: {combined_output}")
                return "unexpected"
    
    def test_captcha_url_access(self):
        """Test if we can access the captcha URL"""
        print("\n🔍 Testing Captcha URL Access...")
        print("-" * 40)
        
        captcha_url = "https://signalcaptchas.org/challenge/generate.html"
        
        try:
            response = requests.get(captcha_url, timeout=10)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ Captcha URL is accessible")
                
                # Check if it contains expected content
                if "captcha" in response.text.lower():
                    print("✅ Page contains captcha content")
                else:
                    print("⚠️  Page doesn't seem to contain captcha")
                    self.issues_found.append("Captcha page doesn't contain expected content")
                
                # Check for JavaScript requirements
                if "javascript" in response.text.lower():
                    print("⚠️  Page requires JavaScript - may not work in some browsers")
                
            else:
                print(f"❌ Captcha URL returned {response.status_code}")
                self.issues_found.append(f"Captcha URL inaccessible: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Cannot access captcha URL: {e}")
            self.issues_found.append(f"Cannot access captcha URL: {e}")
            self.solutions.append("Check internet connection and firewall settings")
    
    def test_alternative_registration_methods(self):
        """Test alternative registration methods"""
        print("\n🔍 Testing Alternative Methods...")
        print("-" * 40)
        
        methods_to_test = [
            ("Voice Registration", f"docker exec signal-api signal-cli -a {self.phone_number} register --voice"),
            ("REST API Registration", None),  # Will test separately
        ]
        
        for method_name, command in methods_to_test:
            print(f"\n📝 Testing: {method_name}")
            
            if command:
                stdout, stderr, code = self.run_command(command)
                combined = (stdout or "") + (stderr or "")
                
                if "SMS" in combined or "voice" in combined:
                    print(f"✅ {method_name} may work!")
                    self.solutions.append(f"Try {method_name.lower()}")
                elif "Captcha" in combined:
                    print(f"⚠️  {method_name} also requires captcha")
                else:
                    print(f"❓ {method_name} gave unexpected response: {combined}")
        
        # Test REST API
        print(f"\n📝 Testing: REST API Registration")
        try:
            response = requests.post(
                f"{self.api_base}/register/{self.phone_number}",
                json={},
                timeout=10
            )
            
            print(f"REST API Status: {response.status_code}")
            print(f"REST API Response: {response.text}")
            
            if response.status_code in [200, 201]:
                print("✅ REST API registration may work!")
                self.solutions.append("Try REST API registration method")
            
        except Exception as e:
            print(f"❌ REST API test failed: {e}")
    
    def check_network_issues(self):
        """Check for network connectivity issues"""
        print("\n🔍 Checking Network Connectivity...")
        print("-" * 40)
        
        # Test DNS resolution
        try:
            import socket
            socket.gethostbyname("signalcaptchas.org")
            print("✅ DNS resolution working")
        except Exception as e:
            print(f"❌ DNS resolution failed: {e}")
            self.issues_found.append("DNS resolution problems")
            self.solutions.append("Check DNS settings or try different DNS (8.8.8.8)")
        
        # Test HTTPS connectivity
        try:
            response = requests.get("https://httpbin.org/status/200", timeout=5)
            if response.status_code == 200:
                print("✅ HTTPS connectivity working")
            else:
                print("⚠️  HTTPS connectivity issues")
        except Exception as e:
            print(f"❌ HTTPS test failed: {e}")
            self.issues_found.append("HTTPS connectivity problems")
            self.solutions.append("Check firewall and proxy settings")
    
    def generate_report(self):
        """Generate diagnostic report"""
        print("\n" + "="*60)
        print("📋 DIAGNOSTIC REPORT")
        print("="*60)
        
        if not self.issues_found:
            print("✅ No issues detected!")
            print("\n💡 Captcha may be working - try again with fresh token")
        else:
            print(f"❌ Found {len(self.issues_found)} issue(s):")
            for i, issue in enumerate(self.issues_found, 1):
                print(f"   {i}. {issue}")
        
        if self.solutions:
            print(f"\n🔧 Suggested Solutions:")
            for i, solution in enumerate(self.solutions, 1):
                print(f"   {i}. {solution}")
        
        print(f"\n📱 Alternative Registration Methods:")
        print("   1. python register_without_captcha.py")
        print("   2. python register_via_linking.py")
        print("   3. Use a different phone number")
        print("   4. Try registration from different network")


def main():
    """Main diagnostic process"""
    print("🔧 Signal Registration Diagnostic Tool")
    print("="*60)
    print("This tool will diagnose why captcha registration isn't working.\n")
    
    diagnostic = SignalDiagnostic()
    
    # Run all diagnostic tests
    tests = [
        ("Docker Status", diagnostic.check_docker_status),
        ("API Connectivity", diagnostic.check_api_connectivity),
        ("Captcha Process", diagnostic.test_captcha_process),
        ("Captcha URL Access", diagnostic.test_captcha_url_access),
        ("Alternative Methods", diagnostic.test_alternative_registration_methods),
        ("Network Issues", diagnostic.check_network_issues),
    ]
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            if result == "already_registered":
                print("\n🎉 GOOD NEWS! Your number is already registered!")
                print("🚀 You can skip registration and run: python src/idle_bot.py")
                return
        except Exception as e:
            print(f"❌ Test failed: {e}")
            diagnostic.issues_found.append(f"{test_name} test failed: {e}")
    
    # Generate final report
    diagnostic.generate_report()


if __name__ == "__main__":
    main()
