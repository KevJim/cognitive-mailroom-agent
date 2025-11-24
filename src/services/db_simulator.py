import datetime
from typing import Dict, Any

from ..models.models import ManualException, ProcessMessageRequest


class SimulatedDBConnection:
    """
    A simulator for a database connection that logs actions to the console
    instead of interacting with a real database.
    """

    def _format_params(self, params: Dict[str, Any]) -> str:
        """Formats parameters into a SQL-like string."""
        if not params:
            return ""
        
        formatted = []
        for key, value in params.items():
            if isinstance(value, str):
                # Enclose string values in single quotes
                formatted.append(f"{key}='{value}'")
            elif value is None:
                formatted.append(f"{key}=NULL")
            else:
                formatted.append(f"{key}={value}")
        return ", ".join(formatted)

    def execute_sp(self, sp_name: str, params: Dict[str, Any]):
        """
        Simulates the execution of a stored procedure.

        It prints the full EXEC command to the console. It also includes
        a simple failure simulation if a required parameter is missing.

        Args:
            sp_name: The name of the stored procedure to execute.
            params: A dictionary of parameters for the stored procedure.
        
        Raises:
            ValueError: If a parameter value is None, simulating a constraint violation.
        """
        print("-" * 50)
        print(f"[{datetime.datetime.now()}] SIMULATING DATABASE EXECUTION")

        # Simulate failure if a parameter is missing (is None)
        for key, value in params.items():
            if value is None:
                error_msg = f"Simulated DBError: Mandatory parameter '{key}' is missing for SP '{sp_name}'."
                print(f"ERROR: {error_msg}")
                raise ValueError(error_msg)

        # Format and print the simulated SQL command
        params_str = self._format_params(params)
        print(f"EXEC {sp_name} {params_str}")
        print("-" * 50)

    def log_exception(self, exception_data: ManualException):
        """
        Simulates logging an exception to a manual review table.

        Prints the details of the exception to the console.
        """
        print("=" * 50)
        print(f"[{datetime.datetime.now()}] SIMULATING EXCEPTION LOGGING")
        print("An error occurred that requires manual review:")
        print(f"  Timestamp: {exception_data.timestamp}")
        print(f"  Intent ID: {exception_data.intent_id or 'Not detected'}")
        print(f"  Error: {exception_data.error_message}")
        print(f"  Original Channel: {exception_data.original_request.channel_id}")
        print(f"  Original Body: '{exception_data.original_request.body}'")
        print("=" * 50)


# Singleton instance to be used across the application
db_simulator = SimulatedDBConnection()

