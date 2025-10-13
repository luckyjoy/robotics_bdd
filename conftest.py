# conftest.py
import sys
import os
import pytest
#from pytest_html import extras

# -------------------------
# Ensure project root is in sys.path
# -------------------------
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from simulation.robot_sim import RobotSim

# -------------------------
# Pytest Fixtures
# -------------------------
@pytest.fixture
def sim():
    """Fixture to create a RobotSim instance."""
    robot = RobotSim()
    # Boundaries ((min_x, min_y, min_z), (max_x, max_y, max_z))
    robot.boundary = ((0, 0, 0), (5, 5, 5))
    robot.object_position = (0, 0, 0)
    robot.arm_position = (0, 0, 0)
    robot.obstacles = []
    return robot

# -------------------------
# Register Custom Markers
# -------------------------
'''
def pytest_configure(config):
    markers = [
        "navigation: Tests related to robot navigation",
        "pick_and_place: Tests for pick and place sequences",
        "safety: Safety-related tests",
        "walking: Walking-related tests",
        "sensors: Sensor-related tests",
        "security: Security and Access Control tests",
    ]
    
    for mark in markers:
        config.addinivalue_line("markers", mark)


# -------------------------
# Pytest HTML Report Hooks
# -------------------------
# -------------------------
# Pytest HTML Report Title
# -------------------------
def pytest_html_report_title(report):
    report.title = "Robot Simulation BDD Test Report"
    
def pytest_html_results_table_header(cells):
    """Add Suite and Author columns to HTML report header."""
    cells.insert(pytest_html.extras.html('<th>Suite</th>'))
   # cells.insert(pytest_html.extras.html('<th>Author</th>'))

def pytest_html_results_table_row(report, cells):
    """Populate Suite and Author columns for each test row."""
    suite_markers = ["navigation", "pick_and_place", "safety", "walking", "sensors"]
    suite = "General"
    for m in suite_markers:
        if m in getattr(report, "keywords", {}):
            suite = m
            break

    # Insert HTML-rendered cells
    cells.insert(pytest_html.extras.html(f"<td>{suite}</td>"))
    #cells.insert(1, pytest_html.extras.html(f"<td>{suite}</td>"))
    #cells.insert(2, pytest_html.extras.html("<td>Bang Thien Nguyen</td>"))

def pytest_html_results_summary(prefix, summary, postfix):
    prefix.extend([extras.html("<p>Author: Bang Thien Nguyen</p>")])

def pytest_html_results_table_header(cells):
    """Add Suite and Author columns to HTML report header."""
    #cells.insert("Suite")
    cells.insert(1, "Suite")
    # cells.insert(2, "Author")

def pytest_html_results_table_row(report, cells):
    """Populate Suite and Author columns for each test row."""
    # Suite: take first matching marker
    suite_markers = ["navigation", "pick_and_place", "safety", "walking", "sensors"]
    suite = "General"
    for m in suite_markers:
        if m in getattr(report, "keywords", {}):
            suite = m
            break
    #cells.insert(suite)
    cells.insert(1, suite)
    #cells.insert(2, "Bang Thien Nguyen")

def pytest_html_results_summary(prefix, summary, postfix):
    prefix.extend([f"Author: Bang Thien Nguyen"])
'''

# -------------------------
# Optional metadata
# -------------------------
def pytest_metadata(metadata):
    metadata['Author'] = "Bang Thien Nguyen"
    metadata['Project'] = "Robot Simulation BDD"
