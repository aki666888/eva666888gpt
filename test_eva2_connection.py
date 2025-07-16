#!/usr/bin/env python3
"""
Test Eva2 connection and environment setup
"""
import os
import subprocess
import sys

def test_ufo2_setup():
    print("=== Eva2 Connection Test ===\n")
    
    # Check Eva2 path
    ufo_path = "D:/UFO"
    print(f"1. Checking Eva2 path: {ufo_path}")
    if os.path.exists(ufo_path):
        print("   ✓ Eva2 directory exists")
    else:
        print("   ✗ Eva2 directory NOT found")
        return False
    
    # Check for UFO module
    ufo_module = os.path.join(ufo_path, "ufo", "__init__.py")
    print(f"\n2. Checking Eva2 module: {ufo_module}")
    if os.path.exists(ufo_module):
        print("   ✓ Eva2 module found")
    else:
        print("   ✗ Eva2 module NOT found")
        return False
    
    # Check API keys
    print("\n3. Checking API keys:")
    gemini_key = os.environ.get('GEMINI_API_KEY') or 'AIzaSyBC4m0pBy8t6D1Q0OAdzPGJ0m8ZAdXr7o0'
    if gemini_key:
        print(f"   ✓ Gemini API key found: {gemini_key[:10]}...")
    else:
        print("   ✗ Gemini API key NOT found")
    
    # Test Eva2 help command
    print("\n4. Testing Eva2 help command:")
    try:
        # Set up environment
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        env['GEMINI_API_KEY'] = gemini_key
        env['GOOGLE_API_KEY'] = gemini_key
        
        cmd = f'cd /d "{ufo_path}" && python -m ufo --help'
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=ufo_path,
            env=env
        )
        
        if result.returncode == 0:
            print("   ✓ Eva2 help command successful")
            print("\n   Output preview:")
            print("   " + "\n   ".join(result.stdout.split('\n')[:5]))
        else:
            print("   ✗ Eva2 help command failed")
            print(f"   Error: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        print("   ✗ Eva2 command timed out")
    except Exception as e:
        print(f"   ✗ Error testing Eva2: {str(e)}")
    
    # Test simple Eva2 task
    print("\n5. Testing simple Eva2 task:")
    try:
        cmd = f'cd /d "{ufo_path}" && python -m ufo --task "What is on my screen?" --non_visual'
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60,
            cwd=ufo_path,
            env=env
        )
        
        if result.returncode == 0:
            print("   ✓ Eva2 task command successful")
        else:
            print("   ✗ Eva2 task command failed")
            print(f"   Error: {result.stderr[:200]}")
            
    except subprocess.TimeoutExpired:
        print("   ✗ Eva2 task timed out (60s)")
    except Exception as e:
        print(f"   ✗ Error running Eva2 task: {str(e)}")
    
    print("\n=== Test Complete ===")
    return True

if __name__ == "__main__":
    test_ufo2_setup()