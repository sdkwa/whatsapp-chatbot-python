#!/usr/bin/env python3
"""Development script for formatting and linting code."""

import subprocess
import sys
from pathlib import Path


def run_command(command: list[str], description: str) -> bool:
    """Run a command and return True if successful."""
    print(f"Running: {description}")
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False


def main():
    """Main function to run formatting and linting."""
    if len(sys.argv) > 1:
        command = sys.argv[1]
    else:
        command = "format"

    # Change to project root
    project_root = Path(__file__).parent.parent
    
    if command == "format":
        print("🎨 Formatting code...")
        success = True
        success &= run_command([sys.executable, "-m", "black", "."], "Black formatting")
        success &= run_command([sys.executable, "-m", "isort", "."], "Import sorting")
        
        if success:
            print("✨ All formatting completed successfully!")
        else:
            print("💥 Some formatting failed!")
            sys.exit(1)
    
    elif command == "check":
        print("🔍 Checking code quality...")
        success = True
        success &= run_command([sys.executable, "-m", "black", "--check", "."], "Black check")
        success &= run_command([sys.executable, "-m", "isort", "--check-only", "."], "Import sort check")
        success &= run_command([sys.executable, "-m", "flake8", "sdkwa_whatsapp_chatbot", "tests", "examples"], "Flake8 linting")
        
        if success:
            print("✅ All checks passed!")
        else:
            print("❌ Some checks failed!")
            sys.exit(1)
    
    elif command == "lint":
        print("🔧 Running linting...")
        success = True
        success &= run_command([sys.executable, "-m", "flake8", "sdkwa_whatsapp_chatbot"], "Flake8 linting")
        
        try:
            success &= run_command([sys.executable, "-m", "mypy", "sdkwa_whatsapp_chatbot"], "MyPy type checking")
        except Exception:
            print("⚠️ MyPy not available, skipping type checking")
        
        if success:
            print("✅ All linting passed!")
        else:
            print("❌ Some linting failed!")
            sys.exit(1)
    
    elif command == "test":
        print("🧪 Running tests...")
        try:
            success = run_command([sys.executable, "-m", "pytest"], "Running tests")
            if success:
                print("✅ All tests passed!")
            else:
                print("❌ Some tests failed!")
                sys.exit(1)
        except Exception:
            print("⚠️ Pytest not available, skipping tests")
    
    else:
        print("Usage: python scripts/dev.py [format|check|lint|test]")
        print("  format: Format code with black and isort")
        print("  check:  Check formatting and linting")
        print("  lint:   Run linting only")
        print("  test:   Run tests")
        sys.exit(1)


if __name__ == "__main__":
    main()
