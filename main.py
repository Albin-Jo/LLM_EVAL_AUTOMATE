#!/usr/bin/env python3
import argparse
import os
import sys
import subprocess


def run_ui():
    """Run the Streamlit UI."""
    try:
        import streamlit
        subprocess.check_call(["streamlit", "run", "ui/app.py"])
    except ImportError:
        print("Error: Streamlit is not installed. Please install it with:")
        print("pip install streamlit")
        sys.exit(1)
    except subprocess.CalledProcessError:
        print("Error: Failed to start the Streamlit UI.")
        sys.exit(1)


def run_tests(modules=None, token=None, generate_data=True, parallel=False, verbose=False):
    """Run the test suite."""
    cmd = ["pytest"]

    if verbose:
        cmd.append("-v")

    if not generate_data:
        os.environ["NO_GENERATE_DATA"] = "1"

    if parallel:
        cmd.append("-n=auto")

    if token:
        os.environ["LLM_API_TOKEN"] = token

    if modules:
        for module in modules:
            cmd.append(f"tests/test_{module}.py")

    subprocess.check_call(cmd)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="LLM API Test Automation Framework")

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # UI command
    ui_parser = subparsers.add_parser("ui", help="Run the UI interface")

    # Test command
    test_parser = subparsers.add_parser("test", help="Run the test suite")
    test_parser.add_argument(
        "--modules",
        nargs="+",
        choices=["auth", "agents", "datasets", "evaluations", "prompts", "reports", "all"],
        help="Test modules to run"
    )
    test_parser.add_argument("--token", help="API authentication token")
    test_parser.add_argument("--no-generate-data", action="store_true", help="Disable test data generation")
    test_parser.add_argument("--parallel", action="store_true", help="Run tests in parallel")
    test_parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    if args.command == "ui":
        run_ui()
    elif args.command == "test":
        modules = args.modules
        if modules and "all" in modules:
            modules = None
        run_tests(
            modules=modules,
            token=args.token,
            generate_data=not args.no_generate_data,
            parallel=args.parallel,
            verbose=args.verbose
        )
    else:
        parser.print_help()


if __name__ == "__main__":
    main()