#!/usr/bin/env python3
"""Development and testing script for SDKWA WhatsApp Chatbot."""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def run_command(command, cwd=None):
    """Run a shell command and return the result."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr


def format_code():
    """Format code with Black and isort."""
    print("Formatting code with Black...")
    success, output = run_command("black sdkwa_whatsapp_chatbot/ examples/ --line-length 88")
    if not success:
        print(f"Black failed: {output}")
        return False
    
    print("Sorting imports with isort...")
    success, output = run_command("isort sdkwa_whatsapp_chatbot/ examples/ --profile black")
    if not success:
        print(f"isort failed: {output}")
        return False
    
    print("Code formatting complete!")
    return True


def lint_code():
    """Lint code with flake8."""
    print("Linting code with flake8...")
    success, output = run_command("flake8 sdkwa_whatsapp_chatbot/ --max-line-length=88 --extend-ignore=E203,W503")
    if not success:
        print(f"Flake8 found issues:\n{output}")
        return False
    
    print("Linting passed!")
    return True


def type_check():
    """Type check with mypy."""
    print("Type checking with mypy...")
    success, output = run_command("mypy sdkwa_whatsapp_chatbot/ --ignore-missing-imports")
    if not success:
        print(f"MyPy found issues:\n{output}")
        return False
    
    print("Type checking passed!")
    return True


def run_tests():
    """Run tests with pytest."""
    print("Running tests with pytest...")
    success, output = run_command("pytest tests/ -v")
    if not success:
        print(f"Tests failed:\n{output}")
        return False
    
    print("All tests passed!")
    return True


def build_package():
    """Build the package."""
    print("Building package...")
    
    # Clean previous builds
    run_command("rm -rf build/ dist/ *.egg-info/")
    
    # Build package
    success, output = run_command("python setup.py sdist bdist_wheel")
    if not success:
        print(f"Build failed: {output}")
        return False
    
    print("Package built successfully!")
    return True


def install_package():
    """Install package in development mode."""
    print("Installing package in development mode...")
    success, output = run_command("pip install -e .")
    if not success:
        print(f"Installation failed: {output}")
        return False
    
    print("Package installed successfully!")
    return True


def clean():
    """Clean build artifacts."""
    print("Cleaning build artifacts...")
    
    artifacts = [
        "build/",
        "dist/",
        "*.egg-info/",
        "__pycache__/",
        "*.pyc",
        "*.pyo",
        ".pytest_cache/",
        ".mypy_cache/",
        ".coverage"
    ]
    
    for artifact in artifacts:
        run_command(f"find . -name '{artifact}' -exec rm -rf {{}} +")
    
    print("Clean complete!")


def check_env():
    """Check if environment variables are set."""
    required_vars = ['ID_INSTANCE', 'API_TOKEN_INSTANCE']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("⚠️  Missing environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nSet these variables to run the examples:")
        print("export ID_INSTANCE='your-instance-id'")
        print("export API_TOKEN_INSTANCE='your-api-token'")
        return False
    
    print("✅ Environment variables are set!")
    return True


def run_example(example_name):
    """Run a specific example."""
    example_path = Path("examples") / f"{example_name}.py"
    
    if not example_path.exists():
        print(f"Example {example_name} not found!")
        available_examples = [f.stem for f in Path("examples").glob("*.py")]
        print(f"Available examples: {', '.join(available_examples)}")
        return False
    
    if not check_env():
        return False
    
    print(f"Running example: {example_name}")
    success, output = run_command(f"python {example_path}")
    if not success:
        print(f"Example failed: {output}")
        return False
    
    return True


def list_examples():
    """List available examples."""
    examples_dir = Path("examples")
    if not examples_dir.exists():
        print("No examples directory found!")
        return
    
    examples = [f.stem for f in examples_dir.glob("*.py")]
    if not examples:
        print("No examples found!")
        return
    
    print("Available examples:")
    for example in sorted(examples):
        print(f"  - {example}")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Development script for SDKWA WhatsApp Chatbot")
    parser.add_argument("command", choices=[
        "format", "lint", "typecheck", "test", "build", "install", "clean",
        "check-env", "run-example", "list-examples", "all"
    ], help="Command to run")
    parser.add_argument("--example", help="Example name to run (for run-example command)")
    
    args = parser.parse_args()
    
    if args.command == "format":
        format_code()
    elif args.command == "lint":
        lint_code()
    elif args.command == "typecheck":
        type_check()
    elif args.command == "test":
        run_tests()
    elif args.command == "build":
        build_package()
    elif args.command == "install":
        install_package()
    elif args.command == "clean":
        clean()
    elif args.command == "check-env":
        check_env()
    elif args.command == "run-example":
        if not args.example:
            print("Please specify an example name with --example")
            list_examples()
            sys.exit(1)
        run_example(args.example)
    elif args.command == "list-examples":
        list_examples()
    elif args.command == "all":
        print("Running all checks...")
        success = (
            format_code() and
            lint_code() and
            type_check() and
            run_tests() and
            build_package()
        )
        if success:
            print("✅ All checks passed!")
        else:
            print("❌ Some checks failed!")
            sys.exit(1)


if __name__ == "__main__":
    main()
