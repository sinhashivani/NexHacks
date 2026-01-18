#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify Vercel deployment readiness.
Run this before deploying to catch any import or configuration issues.
"""

import sys
from pathlib import Path

def test_imports():
    """Test that all imports work correctly"""
    print("Testing imports...")
    
    try:
        # Test main imports
        from api.index import app
        print("  [OK] api.index imports successfully")
        
        # Test that app is FastAPI instance
        from fastapi import FastAPI
        assert isinstance(app, FastAPI), "app should be FastAPI instance"
        print("  [OK] app is FastAPI instance")
        
        # Test that routes are registered
        routes = [route.path for route in app.routes]
        assert "/" in routes, "Root route should exist"
        assert "/markets/trending" in routes, "Trending route should exist"
        assert "/similar" in routes, "Similar route should exist"
        print(f"  [OK] Found {len(routes)} routes registered")
        
        return True
        
    except Exception as e:
        print(f"  [FAIL] Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_dependencies():
    """Test that all required dependencies can be imported"""
    print("\nTesting dependencies...")
    
    dependencies = [
        ("fastapi", "FastAPI"),
        ("fastapi.middleware.cors", "CORSMiddleware"),
        ("starlette.middleware.base", "BaseHTTPMiddleware"),
        ("supabase", None),  # Just check it exists
        ("httpx", None),
        ("google.generativeai", None),
    ]
    
    all_ok = True
    for module, attr in dependencies:
        try:
            mod = __import__(module, fromlist=[attr] if attr else [])
            if attr:
                assert hasattr(mod, attr), f"{module} should have {attr}"
            print(f"  [OK] {module}")
        except ImportError as e:
            print(f"  [FAIL] {module}: {e}")
            all_ok = False
    
    return all_ok

def test_configuration():
    """Test configuration files exist"""
    print("\nTesting configuration files...")
    
    files = [
        "api/index.py",
        "api/main.py",
        "api/requirements.txt",
        "vercel.json",
        "pyproject.toml",
    ]
    
    all_ok = True
    for file_path in files:
        path = Path(file_path)
        if path.exists():
            print(f"  [OK] {file_path}")
        else:
            print(f"  [FAIL] {file_path} - MISSING!")
            all_ok = False
    
    return all_ok

def main():
    print("=" * 60)
    print("Vercel Deployment Readiness Test")
    print("=" * 60)
    
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("Dependencies", test_dependencies()))
    results.append(("Configuration", test_configuration()))
    
    print("\n" + "=" * 60)
    print("Test Results:")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{name}: {status}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    if all_passed:
        print("SUCCESS: All tests passed! Ready for Vercel deployment!")
        return 0
    else:
        print("WARNING: Some tests failed. Fix issues before deploying.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
