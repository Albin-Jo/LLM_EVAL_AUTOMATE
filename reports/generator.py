import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

import matplotlib.pyplot as plt
import numpy as np

from config.settings import REPORT_DIR, REPORT_TITLE


class ReportGenerator:
    """Generate detailed test reports in various formats."""

    def __init__(self, results: Dict[str, Any]):
        """Initialize with test results data."""
        self.results = results
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    def save_json(self, filename: Optional[str] = None) -> str:
        """Save results as a JSON file."""
        if filename is None:
            filename = f"test_report_{self.timestamp}.json"

        filepath = REPORT_DIR / filename
        with open(filepath, "w") as f:
            json.dump(self.results, f, indent=2)

        return str(filepath)

    def save_html(self, filename: Optional[str] = None) -> str:
        """Generate and save an HTML report."""
        if filename is None:
            filename = f"test_report_{self.timestamp}.html"

        filepath = REPORT_DIR / filename

        # Create HTML content
        html_content = self._generate_html_report()

        with open(filepath, "w") as f:
            f.write(html_content)

        return str(filepath)

    def save_charts(self, directory: Optional[str] = None) -> Dict[str, str]:
        """Generate and save chart images for the report."""
        if directory is None:
            directory = f"charts_{self.timestamp}"

        chart_dir = REPORT_DIR / directory
        chart_dir.mkdir(exist_ok=True)

        chart_paths = {}

        # Generate summary pie chart
        summary_path = self._generate_summary_pie_chart(chart_dir)
        if summary_path:
            chart_paths["summary"] = summary_path

        # Generate module comparison chart
        module_path = self._generate_module_comparison_chart(chart_dir)
        if module_path:
            chart_paths["module_comparison"] = module_path

        # Generate duration comparison chart
        duration_path = self._generate_duration_chart(chart_dir)
        if duration_path:
            chart_paths["duration"] = duration_path

        return chart_paths

    def _generate_summary_pie_chart(self, chart_dir: Path) -> Optional[str]:
        """Generate a pie chart of overall test results."""
        try:
            passed = self.results.get("passed", 0)
            failed = self.results.get("failed", 0)
            skipped = self.results.get("skipped", 0)

            if passed == 0 and failed == 0 and skipped == 0:
                return None

            # Create pie chart
            labels = []
            sizes = []
            colors = []

            if passed > 0:
                labels.append(f"Passed ({passed})")
                sizes.append(passed)
                colors.append("#4CAF50")  # Green

            if failed > 0:
                labels.append(f"Failed ({failed})")
                sizes.append(failed)
                colors.append("#F44336")  # Red

            if skipped > 0:
                labels.append(f"Skipped ({skipped})")
                sizes.append(skipped)
                colors.append("#FFC107")  # Amber

            plt.figure(figsize=(8, 6))
            plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
            plt.axis('equal')
            plt.title("Test Results Summary")

            # Save chart
            filepath = chart_dir / "summary_pie.png"
            plt.savefig(filepath)
            plt.close()

            return str(filepath)
        except Exception as e:
            print(f"Error generating summary pie chart: {e}")
            return None

    def _generate_module_comparison_chart(self, chart_dir: Path) -> Optional[str]:
        """Generate a chart comparing results across modules."""
        try:
            modules = self.results.get("modules", {})
            if not modules:
                return None

            module_names = []
            passed_counts = []
            failed_counts = []
            skipped_counts = []

            for name, stats in modules.items():
                module_names.append(name)
                passed_counts.append(stats.get("passed", 0))
                failed_counts.append(stats.get("failed", 0))
                skipped_counts.append(stats.get("skipped", 0))

            if not module_names:
                return None

            # Create bar chart
            x = np.arange(len(module_names))
            width = 0.25

            fig, ax = plt.figure(figsize=(10, 6)), plt.subplot()

            ax.bar(x - width, passed_counts, width, label='Passed', color='#4CAF50')
            ax.bar(x, failed_counts, width, label='Failed', color='#F44336')
            ax.bar(x + width, skipped_counts, width, label='Skipped', color='#FFC107')

            ax.set_ylabel('Number of tests')
            ax.set_title('Test Results by Module')
            ax.set_xticks(x)
            ax.set_xticklabels(module_names, rotation=45, ha='right')
            ax.legend()

            plt.tight_layout()

            # Save chart
            filepath = chart_dir / "module_comparison.png"
            plt.savefig(filepath)
            plt.close()

            return str(filepath)
        except Exception as e:
            print(f"Error generating module comparison chart: {e}")
            return None

    def _generate_duration_chart(self, chart_dir: Path) -> Optional[str]:
        """Generate a chart showing test durations."""
        try:
            test_durations = self.results.get("test_durations", {})
            if not test_durations:
                return None

            # Sort by duration
            sorted_durations = sorted(test_durations.items(), key=lambda x: x[1], reverse=True)

            # Limit to top 10 for readability
            test_names = [item[0] for item in sorted_durations[:10]]
            durations = [item[1] for item in sorted_durations[:10]]

            # Create horizontal bar chart
            plt.figure(figsize=(10, 6))
            plt.barh(test_names, durations, color='#2196F3')
            plt.xlabel('Duration (seconds)')
            plt.title('Top 10 Test Durations')
            plt.grid(axis='x', linestyle='--', alpha=0.7)
            plt.tight_layout()

            # Save chart
            filepath = chart_dir / "test_durations.png"
            plt.savefig(filepath)
            plt.close()

            return str(filepath)
        except Exception as e:
            print(f"Error generating duration chart: {e}")
            return None

    def _generate_html_report(self) -> str:
        """Generate an HTML report from the test results."""
        # Generate charts
        chart_paths = self.save_charts()

        # Basic information
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        total = self.results.get("total", 0)
        passed = self.results.get("passed", 0)
        failed = self.results.get("failed", 0)
        skipped = self.results.get("skipped", 0)
        duration = self.results.get("duration", 0)

        # Calculate pass rate
        pass_rate = (passed / total * 100) if total > 0 else 0

        # Start HTML
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{REPORT_TITLE}</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                h1, h2, h3 {{
                    color: #2c3e50;
                }}
                .summary {{
                    display: flex;
                    justify-content: space-between;
                    flex-wrap: wrap;
                    margin-bottom: 20px;
                }}
                .summary-item {{
                    flex: 1;
                    min-width: 200px;
                    padding: 15px;
                    margin: 10px;
                    border-radius: 5px;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                }}
                .passed {{
                    background-color: #e8f5e9;
                    border-left: 5px solid #4CAF50;
                }}
                .failed {{
                    background-color: #ffebee;
                    border-left: 5px solid #F44336;
                }}
                .skipped {{
                    background-color: #fff8e1;
                    border-left: 5px solid #FFC107;
                }}
                .total {{
                    background-color: #e3f2fd;
                    border-left: 5px solid #2196F3;
                }}
                .duration {{
                    background-color: #f3e5f5;
                    border-left: 5px solid #9C27B0;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-bottom: 20px;
                }}
                th, td {{
                    padding: 12px 15px;
                    text-align: left;
                    border-bottom: 1px solid #ddd;
                }}
                th {{
                    background-color: #f5f5f5;
                }}
                tr:hover {{
                    background-color: #f9f9f9;
                }}
                .error {{
                    background-color: #ffebee;
                }}
                .charts {{
                    display: flex;
                    flex-wrap: wrap;
                    justify-content: space-around;
                    margin: 20px 0;
                }}
                .chart {{
                    max-width: 100%;
                    height: auto;
                    margin: 10px;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                }}
                .expand-btn {{
                    background: none;
                    border: none;
                    color: #2196F3;
                    cursor: pointer;
                    font-size: 14px;
                }}
                .traceback {{
                    display: none;
                    background-color: #f5f5f5;
                    padding: 10px;
                    border-radius: 4px;
                    white-space: pre-wrap;
                    font-family: monospace;
                    margin-top: 10px;
                }}
            </style>
        </head>
        <body>
            <h1>{REPORT_TITLE}</h1>
            <p>Generated on: {timestamp}</p>

            <div class="summary">
                <div class="summary-item total">
                    <h3>Total Tests</h3>
                    <p>{total}</p>
                </div>
                <div class="summary-item passed">
                    <h3>Passed</h3>
                    <p>{passed} ({pass_rate:.1f}%)</p>
                </div>
                <div class="summary-item failed">
                    <h3>Failed</h3>
                    <p>{failed}</p>
                </div>
                <div class="summary-item skipped">
                    <h3>Skipped</h3>
                    <p>{skipped}</p>
                </div>
                <div class="summary-item duration">
                    <h3>Duration</h3>
                    <p>{duration:.2f} seconds</p>
                </div>
            </div>
        """

        # Add charts if available
        if chart_paths:
            html += '<div class="charts">'
            for chart_type, path in chart_paths.items():
                img_path = os.path.relpath(path, REPORT_DIR)
                html += f'<img src="{img_path}" alt="{chart_type} chart" class="chart">'
            html += '</div>'

        # Add module results table
        modules = self.results.get("modules", {})
        if modules:
            html += """
            <h2>Results by Module</h2>
            <table>
                <tr>
                    <th>Module</th>
                    <th>Total</th>
                    <th>Passed</th>
                    <th>Failed</th>
                    <th>Skipped</th>
                    <th>Pass Rate</th>
                </tr>
            """

            for name, stats in modules.items():
                module_total = stats.get("total", 0)
                module_passed = stats.get("passed", 0)
                module_failed = stats.get("failed", 0)
                module_skipped = stats.get("skipped", 0)
                module_pass_rate = (module_passed / module_total * 100) if module_total > 0 else 0

                html += f"""
                <tr>
                    <td>{name}</td>
                    <td>{module_total}</td>
                    <td>{module_passed}</td>
                    <td>{module_failed}</td>
                    <td>{module_skipped}</td>
                    <td>{module_pass_rate:.1f}%</td>
                </tr>
                """

            html += "</table>"

        # Add failures table
        failures = self.results.get("failures", [])
        if failures:
            html += """
            <h2>Failed Tests</h2>
            <table>
                <tr>
                    <th>Test</th>
                    <th>Module</th>
                    <th>Error Message</th>
                    <th>Details</th>
                </tr>
            """

            for i, failure in enumerate(failures):
                test_name = failure.get("name", "Unknown")
                module_name = failure.get("module", "Unknown")
                error_message = failure.get("message", "No error message")
                traceback = failure.get("traceback", "No traceback available")

                html += f"""
                <tr class="error">
                    <td>{test_name}</td>
                    <td>{module_name}</td>
                    <td>{error_message}</td>
                    <td>
                        <button class="expand-btn" onclick="toggleTraceback({i})">Show/Hide Details</button>
                        <div id="traceback-{i}" class="traceback">{traceback}</div>
                    </td>
                </tr>
                """

            html += "</table>"

        # Add JavaScript for expandable sections
        html += """
        <script>
            function toggleTraceback(id) {
                const element = document.getElementById('traceback-' + id);
                if (element.style.display === 'block') {
                    element.style.display = 'none';
                } else {
                    element.style.display = 'block';
                }
            }
        </script>
        """

        # Close HTML
        html += """
        </body>
        </html>
        """

        return html
