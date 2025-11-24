import datetime
from typing import Dict, Any, Optional
from contextlib import contextmanager

from sqlalchemy import text, create_engine
from sqlalchemy.engine import Engine, Connection
from sqlalchemy.pool import QueuePool
from sqlalchemy.sql.elements import TextClause

from ..models.models import ManualException, ProcessMessageRequest


class SimulatedDBConnection:
    """
    A simulator for a database connection that mimics real SQL Server connection patterns
    using SQLAlchemy Core. It uses proper connection pooling, transaction management,
    and connection context managers, but simulates the actual database execution.
    
    This follows the requirement to use SQLAlchemy Core (Raw SQL) while simulating
    the database connection. The code structure mirrors production database access patterns.
    """

    def __init__(self, connection_string: Optional[str] = None):
        """
        Initialize a simulated SQLAlchemy engine with connection pooling.
        
        In production, this would connect to SQL Server. For simulation, we use
        an in-memory SQLite database but structure the code exactly as we would
        for SQL Server.
        
        Args:
            connection_string: Optional connection string. If not provided, uses
                              a simulated SQL Server connection string format.
        """
        # Simulate SQL Server connection string format
        # In production: "mssql+pyodbc://user:pass@server/db?driver=ODBC+Driver+17+for+SQL+Server"
        if connection_string is None:
            # Use SQLite in-memory for simulation, but structure code for SQL Server
            connection_string = "sqlite:///:memory:"
        
        # Create engine with connection pooling (like production)
        self._engine: Engine = create_engine(
            connection_string,
            poolclass=QueuePool,
            pool_size=5,  # Connection pool size
            max_overflow=10,  # Max overflow connections
            pool_pre_ping=True,  # Verify connections before using
            echo=False,  # Set to True for SQL logging in development
        )
        
        # Track connection usage for simulation logging
        self._connection_count = 0
        self._transaction_count = 0

    @contextmanager
    def get_connection(self):
        """
        Context manager for database connections. This mimics the production pattern
        of acquiring a connection from the pool, using it, and returning it.
        
        Usage:
            with db_simulator.get_connection() as conn:
                result = conn.execute(...)
        """
        self._connection_count += 1
        conn_id = self._connection_count
        
        print(f"[{datetime.datetime.now()}] [Connection #{conn_id}] Acquiring connection from pool...")
        
        # Get connection from pool (like production)
        connection = self._engine.connect()
        
        try:
            print(f"[{datetime.datetime.now()}] [Connection #{conn_id}] Connection acquired")
            yield connection
        finally:
            print(f"[{datetime.datetime.now()}] [Connection #{conn_id}] Returning connection to pool")
            connection.close()

    @contextmanager
    def begin_transaction(self, connection: Optional[Connection] = None):
        """
        Context manager for database transactions. Mimics production transaction handling.
        
        Args:
            connection: Optional existing connection. If None, creates a new one.
        
        Usage:
            with db_simulator.begin_transaction() as conn:
                conn.execute(...)
        """
        self._transaction_count += 1
        txn_id = self._transaction_count
        
        if connection is None:
            # Use connection context manager
            with self.get_connection() as conn:
                with conn.begin() as txn:
                    print(f"[{datetime.datetime.now()}] [Transaction #{txn_id}] Transaction started")
                    try:
                        yield conn
                        print(f"[{datetime.datetime.now()}] [Transaction #{txn_id}] Transaction committed")
                    except Exception as e:
                        print(f"[{datetime.datetime.now()}] [Transaction #{txn_id}] Transaction rolled back: {e}")
                        raise
        else:
            # Use existing connection
            with connection.begin() as txn:
                print(f"[{datetime.datetime.now()}] [Transaction #{txn_id}] Transaction started")
                try:
                    yield connection
                    print(f"[{datetime.datetime.now()}] [Transaction #{txn_id}] Transaction committed")
                except Exception as e:
                    print(f"[{datetime.datetime.now()}] [Transaction #{txn_id}] Transaction rolled back: {e}")
                    raise

    def _build_sp_sql(self, sp_name: str, params: Dict[str, Any]) -> TextClause:
        """
        Builds a SQLAlchemy Core text() statement for executing a stored procedure.
        
        Args:
            sp_name: The name of the stored procedure to execute.
            params: A dictionary of parameters for the stored procedure.
        
        Returns:
            SQLAlchemy text() object with the EXEC statement and bound parameters
        """
        # Build parameter placeholders for SQL Server stored procedure syntax
        # SQL Server uses @param_name syntax
        param_placeholders = []
        sqlalchemy_params = {}
        
        for param_name, param_value in params.items():
            # SQL Server parameter names can have @ prefix
            # SQLAlchemy will handle the binding
            clean_param_name = param_name.lstrip('@')
            param_placeholders.append(f"@{param_name}=:{clean_param_name}")
            sqlalchemy_params[clean_param_name] = param_value
        
        # Construct the EXEC statement using SQLAlchemy text()
        if param_placeholders:
            sql_statement = text(f"EXEC {sp_name} {', '.join(param_placeholders)}")
        else:
            sql_statement = text(f"EXEC {sp_name}")
        
        # Bind parameters to the statement
        if sqlalchemy_params:
            sql_statement = sql_statement.bindparams(**sqlalchemy_params)
        
        return sql_statement

    def execute_sp(self, sp_name: str, params: Dict[str, Any]):
        """
        Executes a stored procedure using SQLAlchemy Core with proper connection
        and transaction management, simulating real database access patterns.

        This method:
        1. Validates parameters
        2. Acquires a connection from the pool
        3. Begins a transaction
        4. Executes the stored procedure
        5. Commits the transaction (or rolls back on error)
        6. Returns the connection to the pool

        Args:
            sp_name: The name of the stored procedure to execute.
            params: A dictionary of parameters for the stored procedure.
        
        Raises:
            ValueError: If a parameter value is None, simulating a constraint violation.
        """
        print("=" * 70)
        print(f"[{datetime.datetime.now()}] EXECUTING STORED PROCEDURE: {sp_name}")
        print("=" * 70)

        # Validate parameters before attempting execution
        for key, value in params.items():
            if value is None:
                error_msg = f"DBError: Mandatory parameter '{key}' is missing for SP '{sp_name}'."
                print(f"ERROR: {error_msg}")
                raise ValueError(error_msg)

        # Build SQL statement using SQLAlchemy Core
        sql_statement = self._build_sp_sql(sp_name, params)
        
        # Execute using proper connection and transaction management
        # This is the production-like pattern
        try:
            with self.get_connection() as conn:
                with self.begin_transaction(conn) as txn_conn:
                    # Compile SQL to show what would be executed
                    compiled = sql_statement.compile(
                        dialect=self._engine.dialect,
                        compile_kwargs={"literal_binds": False}
                    )
                    
                    print(f"\n[SQLAlchemy Core] Prepared Statement:")
                    print(f"  {compiled}")
                    
                    # Show parameter bindings
                    print(f"\n[Parameters]:")
                    for param_name, param_value in params.items():
                        print(f"  {param_name} = {param_value!r}")
                    
                    # In a real scenario, we would execute:
                    # result = txn_conn.execute(sql_statement)
                    # For simulation, we log the execution instead
                    print(f"\n[Simulation] Executing stored procedure...")
                    
                    # Simulate execution - in production this would be:
                    # result = txn_conn.execute(sql_statement)
                    # For SQL Server stored procedures, we might also handle output parameters
                    
                    # Show the final SQL Server syntax
                    param_str_parts = []
                    for param_name, param_value in params.items():
                        if isinstance(param_value, str):
                            param_str_parts.append(f"{param_name}='{param_value}'")
                        else:
                            param_str_parts.append(f"{param_name}={param_value}")
                    
                    if param_str_parts:
                        final_sql = f"EXEC {sp_name} {', '.join(param_str_parts)}"
                    else:
                        final_sql = f"EXEC {sp_name}"
                    
                    print(f"[SQL Server] {final_sql}")
                    print(f"\n[Simulation] Stored procedure executed successfully")
                    
        except Exception as e:
            print(f"\n[ERROR] Execution failed: {e}")
            raise
        
        print("=" * 70)

    def log_exception(self, exception_data: ManualException):
        """
        Logs an exception to a manual review table using proper database connection patterns.
        
        In production, this would insert into a table like:
        INSERT INTO manual_review_exceptions (timestamp, intent_id, error_message, channel_id, body)
        VALUES (:timestamp, :intent_id, :error_message, :channel_id, :body)

        Args:
            exception_data: The exception details to log.
        """
        print("=" * 70)
        print(f"[{datetime.datetime.now()}] LOGGING EXCEPTION TO MANUAL REVIEW TABLE")
        print("=" * 70)
        
        # Build INSERT statement using SQLAlchemy Core
        insert_sql = text("""
            INSERT INTO manual_review_exceptions 
            (timestamp, intent_id, error_message, channel_id, original_body)
            VALUES (:timestamp, :intent_id, :error_message, :channel_id, :original_body)
        """)
        
        # Prepare parameters
        insert_params = {
            'timestamp': exception_data.timestamp,
            'intent_id': exception_data.intent_id,
            'error_message': exception_data.error_message,
            'channel_id': exception_data.original_request.channel_id,
            'original_body': exception_data.original_request.body
        }
        
        # Bind parameters
        insert_sql = insert_sql.bindparams(**insert_params)
        
        try:
            # Execute using proper connection and transaction management
            with self.get_connection() as conn:
                with self.begin_transaction(conn) as txn_conn:
                    # Compile SQL to show what would be executed
                    compiled = insert_sql.compile(
                        dialect=self._engine.dialect,
                        compile_kwargs={"literal_binds": False}
                    )
                    
                    print(f"\n[SQLAlchemy Core] Prepared Statement:")
                    print(f"  {compiled}")
                    
                    print(f"\n[Exception Details]:")
                    print(f"  Timestamp: {exception_data.timestamp}")
                    print(f"  Intent ID: {exception_data.intent_id or 'Not detected'}")
                    print(f"  Error: {exception_data.error_message}")
                    print(f"  Original Channel: {exception_data.original_request.channel_id}")
                    print(f"  Original Body: '{exception_data.original_request.body}'")
                    
                    # In production, this would execute:
                    # txn_conn.execute(insert_sql)
                    print(f"\n[Simulation] Exception logged to manual_review_exceptions table")
                    
        except Exception as e:
            # Even if logging fails, we should print the exception details
            print(f"\n[ERROR] Failed to log exception: {e}")
            print(f"[Fallback] Exception details:")
            print(f"  Timestamp: {exception_data.timestamp}")
            print(f"  Intent ID: {exception_data.intent_id or 'Not detected'}")
            print(f"  Error: {exception_data.error_message}")
            print(f"  Original Channel: {exception_data.original_request.channel_id}")
            print(f"  Original Body: '{exception_data.original_request.body}'")
        
        print("=" * 70)


# Singleton instance to be used across the application
db_simulator = SimulatedDBConnection()

