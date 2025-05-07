import streamlit as st
import subprocess
import time
import json
import os
import threading
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

# Set page config
st.set_page_config(
    page_title="LLM API Test Automation Console",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# State variables
if "test_running" not in st.session_state:
    st.session_state.test_running = False
if "progress" not in st.session_state:
    st.session_state.progress = 0
if "current_test" not in st.session_state:
    st.session_state.current_test = ""
if "test_results" not in st.session_state:
    st.session_state.test_results = None
if "log_output" not in st.session_state:
    st.session_state.log_output = []
if "test_process" not in st.session_state:
    st.session_state.test_process = None

# Title
st.title("LLM API Test Automation Console")

# Sidebar for configuration
st.sidebar.header("Configuration")

# Authentication token
token = st.sidebar.text_input("Authentication Token (JWT)", type="password")

# Test module selection
st.sidebar.subheader("Test Modules")
auth_tests = st.sidebar.checkbox("Authentication APIs", value=True)
agent_tests = st.sidebar.checkbox("Agents APIs", value=True)
dataset_tests = st.sidebar.checkbox("Datasets APIs", value=True)
evaluation_tests = st.sidebar.checkbox("Evaluations APIs", value=True)
prompt_tests = st.sidebar.checkbox("Prompts APIs", value=True)
report_tests = st.sidebar.checkbox("Reports APIs", value=True)

# Options
st.sidebar.subheader("Options")
generate_data = st.sidebar.checkbox("Generate test data", value=True)
detailed_logging = st.sidebar.checkbox("Detailed logging", value=True)
parallel_execution = st.sidebar.checkbox("Parallel execution", value=False)


# Helper functions
def parse_pytest_output(line: str) -> Optional[Dict[str, Any]]:
    """Parse pytest output line."""
    if line.startswith("test_"):
        parts = line.strip().split()
        if len(parts) >= 2:
            test_name = parts[0]
            result = parts[1]
            return {"test": test_name, "result": result}
    return None


def update_progress():
    """Update progress based on log output."""
    total_tests = 0
    completed_tests = 0

    # Count total tests
    for module in ["auth", "agents", "datasets", "evaluations", "prompts", "reports"]:
        if getattr(st.session_state, f"{module}_tests", False):
            # This is an estimate - could be refined with actual test counts
            total_tests += 5

    if total_tests == 0:
        return

    # Count completed tests
    for line in st.session_state.log_output:
        if "PASSED" in line or "FAILED" in line or "SKIPPED" in line:
            completed_tests += 1

    # Update progress
    progress = min(completed_tests / total_tests, 1.0)
    st.session_state.progress = progress


def run_tests():
    """Run the pytest tests based on configuration."""
    if not st.session_state.test_running:
        return

    # Build command
    cmd = ["pytest", "-v"]

    # Add selected test modules
    test_modules = []
    if auth_tests:
        test_modules.append("tests/test_auth.py")
    if agent_tests:
        test_modules.append("tests/test_agents.py")
    if dataset_tests:
        test_modules.append("tests/test_datasets.py")
    if evaluation_tests:
        test_modules.append("tests/test_evaluations.py")
    if prompt_tests:
        test_modules.append("tests/test_prompts.py")
    if report_tests:
        test_modules.append("tests/test_reports.py")

    cmd.extend(test_modules)

    # Add options
    if detailed_logging:
        cmd.append("-v")
    if not generate_data:
        cmd.append("--no-generate-data")
    if parallel_execution:
        cmd.append("-n=auto")

    # Add JWT token as environment variable
    env = os.environ.copy()
    env["LLM_API_TOKEN"] = token

    # Run tests in a subprocess
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        env=env
    )

    st.session_state.test_process = process

    # Process output
    while st.session_state.test_running:
        output = process.stdout.readline()
        if output:
            st.session_state.log_output.append(output.strip())
            result = parse_pytest_output(output)
            if result:
                st.session_state.current_test = result["test"]
            update_progress()
        elif process.poll() is not None:
            break
        time.sleep(0.1)

    # Ensure process is terminated if stopped manually
    if process.poll() is None:
        process.terminate()

    # Parse and process final results
    try:
        results_file = "reports/latest_results.json"
        if os.path.exists(results_file):
            with open(results_file, "r") as f:
                st.session_state.test_results = json.load(f)
    except Exception as e:
        st.error(f"Error loading test results: {str(e)}")

    st.session_state.test_running = False
    st.session_state.progress = 1.0


def start_tests():
    """Start the test execution in a separate thread."""
    if st.session_state.test_running:
        return

    st.session_state.test_running = True
    st.session_state.progress = 0
    st.session_state.current_test = ""
    st.session_state.log_output = []
    st.session_state.test_results = None

    thread = threading.Thread(target=run_tests)
    thread.daemon = True
    thread.start()


def stop_tests():
    """Stop the running tests."""
    if not st.session_state.test_running:
        return

    st.session_state.test_running = False

    if st.session_state.test_process and st.session_state.test_process.poll() is None:
        st.session_state.test_process.terminate()


# Action buttons
col1, col2 = st.sidebar.columns(2)
with col1:
    start_button = st.button("Run Tests", key="run_tests", disabled=st.session_state.test_running)
with col2:
    stop_button = st.button("Stop", key="stop_tests", disabled=not st.session_state.test_running)

if start_button:
    start_tests()
if stop_button:
    stop_tests()

# Main panel - Test execution progress
st.header("Test Execution Progress")

# Progress bar
progress_bar = st.progress(st.session_state.progress)

# Status information
col1, col2 = st.columns(2)
with col1:
    st.subheader("Current Status")
    if st.session_state.test_running:
        st.info("Tests are running...")
    elif st.session_state.progress == 1.0:
        st.success("Tests completed!")
    else:
        st.warning("Tests not started")

    st.markdown(f"**Current Test:** {st.session_state.current_test}")

    # Calculate test statistics if results are available
    if st.session_state.test_results:
        results = st.session_state.test_results
        total = results.get("total", 0)
        passed = results.get("passed", 0)
        failed = results.get("failed", 0)
        skipped = results.get("skipped", 0)

        st.metric("Tests Completed", f"{total}")

        if passed > 0:
            st.metric("Passing", f"{passed}", delta=f"{passed / total * 100:.1f}%" if total > 0 else None,
                      delta_color="normal")

        if failed > 0:
            st.metric("Failing", f"{failed}", delta=f"{failed / total * 100:.1f}%" if total > 0 else None,
                      delta_color="inverse")

        if skipped > 0:
            st.metric("Skipped", f"{skipped}")

with col2:
    st.subheader("Test Log")
    log_container = st.container()
    with log_container:
        for log in st.session_state.log_output[-10:]:  # Show last 10 log entries
            if "PASSED" in log:
                st.success(log)
            elif "FAILED" in log:
                st.error(log)
            elif "SKIPPED" in log:
                st.warning(log)
            else:
                st.text(log)

# Detailed results section
st.header("Test Results")

# Tabs for different views
tab1, tab2, tab3 = st.tabs(["Summary", "Failures", "Logs"])

with tab1:
    if st.session_state.test_results:
        results = st.session_state.test_results

        # Summary by module
        st.subheader("Results by Module")
        module_data = []
        for module, stats in results.get("modules", {}).items():
            module_data.append({
                "Module": module,
                "Total": stats.get("total", 0),
                "Passed": stats.get("passed", 0),
                "Failed": stats.get("failed", 0),
                "Skipped": stats.get("skipped", 0),
                "Pass Rate": f"{stats.get('passed', 0) / stats.get('total', 1) * 100:.1f}%"
            })

        if module_data:
            df = pd.DataFrame(module_data)
            st.dataframe(df, use_container_width=True)

        # Overall summary
        st.subheader("Overall Summary")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Duration", f"{results.get('duration', 0):.2f}s")
        with col2:
            st.metric("Total Tests", results.get("total", 0))
        with col3:
            pass_rate = results.get("passed", 0) / results.get("total", 1) * 100
            st.metric("Pass Rate", f"{pass_rate:.1f}%")
        with col4:
            st.metric("Started At", results.get("started_at", "N/A"))
    else:
        st.info("No test results available yet. Run the tests to see results here.")

with tab2:
    if st.session_state.test_results and st.session_state.test_results.get("failures"):
        failures = st.session_state.test_results.get("failures", [])
        st.subheader(f"Failed Tests ({len(failures)})")

        for i, failure in enumerate(failures):
            with st.expander(f"{failure.get('name', 'Unknown test')}"):
                st.markdown(f"**Module:** {failure.get('module', 'Unknown')}")
                st.markdown(f"**Error Message:**")
                st.code(failure.get("message", "No error message available"))

                if "traceback" in failure:
                    st.markdown("**Traceback:**")
                    st.code(failure.get("traceback", ""))
    else:
        st.success("No test failures found!")

with tab3:
    st.subheader("Complete Test Log")

    # Create a text area with all log output
    log_text = "\n".join(st.session_state.log_output)
    st.text_area("Log Output", log_text, height=400)

    # Download button for logs
    if st.session_state.log_output:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = f"test_log_{timestamp}.txt"

        st.download_button(
            label="Download Logs",
            data=log_text,
            file_name=log_filename,
            mime="text/plain"
        )

# Download report button
if st.session_state.test_results:
    st.download_button(
        label="Download Full Report",
        data=json.dumps(st.session_state.test_results, indent=2),
        file_name=f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json"
    )