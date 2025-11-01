#security_steps.py

import pytest
import allure
from pytest_bdd import scenarios, given, when, then, parsers

# Link all navigation scenarios
scenarios('../features/security.feature')

# --- MOCK ROBOT AND SECURITY CLASSES ---

class MockRobotState:
    """A simple class to mock the robot's internal state and logging."""
    def __init__(self):
        self.state = "Operational"
        self.last_command = ""
        self.security_log = []

class MockSecuritySystem:
    """Mocks the security system, handling role-based access control (RBAC)."""
    
    # Define which commands are restricted to which minimum role level
    # Higher number means higher authority
    COMMAND_AUTHORITY = {
        "MOVE_ARM_JOINT": 2,      # Operator (2) or Administrator (3) required
        "SYSTEM_SHUTDOWN": 3,     # Administrator (3) required
        "SYSTEM_REBOOT": 3,
        "EMERGENCY_STOP": 2,
        "CLEAR_ERROR_LOGS": 2,
        "UPDATE_FIRMWARE": 3,
        "GET_TELEMETRY_DATA": 1,  # Observer (1) or higher
        "GET_SYSTEM_INFO": 1,
    }

    # Map roles to their authority level
    ROLE_LEVELS = {
        "Unauthenticated": 0,
        "Guest": 0,
        "Observer": 1,
        "Operator": 2,
        "Administrator": 3,
    }

    def __init__(self, robot: MockRobotState):
        self.current_role = "Unauthenticated"
        self.robot = robot
        self.last_result = None

    def login(self, role: str):
        """Sets the current role for the command context."""
        if role not in self.ROLE_LEVELS:
            raise ValueError(f"Unknown role: {role}")
        self.current_role = role

    def send_command(self, command: str) -> str:
        """Simulates command execution with RBAC check and input validation."""
        
        # 1. Input Validation Check (for injection scenario)
        if any(char in command for char in [';', '&&', '||', '`']):
            self.robot.security_log.append("Command Injection")
            self.last_result = "Strictly Rejected" # Ensure last_result is set here
            return "Strictly Rejected"

        # Extract the base command name (e.g., "MOVE_ARM_JOINT(5)" -> "MOVE_ARM_JOINT")
        command_name = command.split('(')[0].strip()
        
        required_level = self.COMMAND_AUTHORITY.get(command_name, 99) # Default to high authority if command is unknown
        user_level = self.ROLE_LEVELS.get(self.current_role, 0)
        
        # 2. RBAC Check
        if user_level < required_level:
            
            # Handle the specific "Authentication Required" case
            if self.current_role == "Unauthenticated" and command_name == "GET_SYSTEM_INFO":
                 self.last_result = "Authentication Required"
            else:
                self.last_result = "Access Denied"
                
            return self.last_result
        
        # 3. Successful Execution Mock
        self.last_result = "Success"
        self.robot.last_command = command
        
        # Mock State Change for specific commands
        if command_name == "EMERGENCY_STOP":
            self.robot.state = "Stopped"
             
        return self.last_result


# --- PYTEST-BDD FIXTURES AND STEPS ---

@pytest.fixture
def security_context():
    """Provides the security and robot context objects for all tests."""
    robot = MockRobotState()
    security = MockSecuritySystem(robot)
    return {"robot": robot, "security": security}


@given("the simulated robot is connected and operational")
def robot_operational(security_context):
    """Resets the robot state to operational for a new scenario."""
    security_context["robot"].state = "Operational"
    security_context["robot"].security_log = []
    security_context["security"].current_role = "Unauthenticated"
    assert security_context["robot"].state == "Operational"


# --- SCENARIO OUTLINE STEPS (@security @access_control) ---

@given(parsers.parse('the user logs in with the role of "{role}"'))
def user_logs_in(security_context, role):
    """Sets the user role for the current test iteration."""
    security_context["security"].login(role)
    assert security_context["security"].current_role == role


@when(parsers.parse('the user attempts to send the critical command "{command}"'))
def user_sends_command(security_context, command):
    """Sends the command and captures the result."""
    security_context["security"].send_command(command)


@then(parsers.parse('the system should return a "{expected_result}" status'))
def system_returns_status(security_context, expected_result):
    """Asserts the security system returned the expected access status."""
    actual_result = security_context["security"].last_result
    assert actual_result == expected_result, \
        f"Expected status '{expected_result}' but got '{actual_result}' for role '{security_context['security'].current_role}'"

# Simplify the step definition to resolve StepDefinitionNotFoundError
# We use only the body of the step, as the @then decorator and pytest-bdd's
# internal logic handle the 'Then' and 'And' keywords.
@then(parsers.parse("the robot's state should remain \"{expected_state}\""))
def robot_state_remains(security_context, expected_state):
    """Asserts the final state of the mock robot."""
    actual_state = security_context["robot"].state
    
    # Handle the specific "Unchanged" case from the BDD table
    if expected_state == "Unchanged":
        # We assume "Unchanged" means it must still be the initial "Operational" state
        assert actual_state == "Operational", \
            f"Expected state 'Operational' (Unchanged) but robot is in state '{actual_state}'"
    else:
        assert actual_state == expected_state, \
            f"Expected robot state '{expected_state}' but found '{actual_state}'"


# --- COMMAND INJECTION STEPS (@security @input_validation) ---

@given("the simulated robot is connected and awaiting commands")
def robot_awaiting_commands(security_context):
    """Reuses the initial operational setup."""
    robot_operational(security_context)


# FIX: Use the 'docstring' fixture, which is the most reliable way to capture the Gherkin DocString (triple-quoted content).
@when('an unauthenticated user attempts to send a command with a shell injection payload')
def attempt_injection(security_context, docstring):
    """Sends the multi-line payload to the system for input validation."""
    security_context["security"].login("Unauthenticated")
    
    # 'docstring' explicitly captures the triple-quoted content from the Gherkin feature file.
        
    security_context["security"].send_command(docstring.strip())


# FIX 1: Removed "And " from the step string to match the user's Gherkin (e.g., "Then the robot should not execute...")
@then("the robot should not execute any part of the payload")
def robot_should_not_execute(security_context):
    """Asserts the robot state is completely unchanged."""
    assert security_context["robot"].state == "Operational", \
        "Robot state changed. Payload may have executed."
    assert security_context["robot"].last_command == "" , \
        "Robot executed a command after injection attempt."


@then("the system should strictly reject the command due to invalid characters")
def system_strictly_rejects(security_context):
    """Asserts that the system's input validation rejected the command."""
    actual_result = security_context["security"].last_result
    assert actual_result == "Strictly Rejected", \
        f"Expected 'Strictly Rejected' but got '{actual_result}'. Injection vulnerability may exist."


# FIX 2: Removed "And " from the step string to match the Gherkin file's natural flow
@then(parsers.parse('the system should log an attempt at "{log_message}"'))
def system_logs_injection(security_context, log_message):
    """Asserts the injection attempt was recorded in the security log."""
    assert log_message in security_context["robot"].security_log, \
        f"Expected log message '{log_message}' not found in security logs: {security_context['robot'].security_log}"
