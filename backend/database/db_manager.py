import os
import logging
import sqlite3
import pymongo
import psycopg2
from typing import Dict, Any, Optional, Union, List, Tuple

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Database manager for handling database connections and operations."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the database manager.
        
        Args:
            config: Database configuration
        """
        self.config = config
        self.db_type = config.get('db_type', 'sqlite').lower()
        self.connection = None
        self.cursor = None
        
        # Connect to database
        self._connect()
        
        logger.info(f"Database manager initialized with {self.db_type} database")
    
    def _connect(self) -> None:
        """Connect to the database based on configuration."""
        try:
            if self.db_type == 'sqlite':
                db_path = self.config.get('db_path', 'biometric_auth.db')
                self.connection = sqlite3.connect(db_path, check_same_thread=False)
                self.connection.row_factory = sqlite3.Row
                
            elif self.db_type == 'postgresql':
                self.connection = psycopg2.connect(
                    host=self.config.get('host', 'localhost'),
                    port=self.config.get('port', 5432),
                    database=self.config.get('database', 'biometric_auth'),
                    user=self.config.get('user', 'postgres'),
                    password=self.config.get('password', '')
                )
                
            elif self.db_type == 'mongodb':
                mongo_uri = self.config.get('uri', 'mongodb://localhost:27017')
                client = pymongo.MongoClient(mongo_uri)
                db_name = self.config.get('database', 'biometric_auth')
                self.connection = client[db_name]
            
            else:
                raise ValueError(f"Unsupported database type: {self.db_type}")
            
            # Create cursor for SQL databases
            if self.db_type in ['sqlite', 'postgresql']:
                self.cursor = self.connection.cursor()
            
            logger.info(f"Connected to {self.db_type} database")
            
        except Exception as e:
            logger.error(f"Error connecting to {self.db_type} database: {e}")
            raise
    
    def execute(self, query: str, params: tuple = ()) -> Any:
        """Execute a SQL query.
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            Query result
        """
        if self.db_type not in ['sqlite', 'postgresql']:
            raise ValueError(f"execute() not supported for {self.db_type} database")
        
        try:
            self.cursor.execute(query, params)
            return self.cursor
        except Exception as e:
            logger.error(f"Error executing query: {e}\nQuery: {query}\nParams: {params}")
            self.connection.rollback()
            raise
    
    def execute_many(self, query: str, params_list: List[tuple]) -> Any:
        """Execute a SQL query with multiple parameter sets.
        
        Args:
            query: SQL query string
            params_list: List of parameter tuples
            
        Returns:
            Query result
        """
        if self.db_type not in ['sqlite', 'postgresql']:
            raise ValueError(f"execute_many() not supported for {self.db_type} database")
        
        try:
            self.cursor.executemany(query, params_list)
            return self.cursor
        except Exception as e:
            logger.error(f"Error executing query: {e}\nQuery: {query}")
            self.connection.rollback()
            raise
    
    def fetch_one(self, query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
        """Execute a query and fetch one result.
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            Single row result as dictionary or None
        """
        if self.db_type not in ['sqlite', 'postgresql']:
            raise ValueError(f"fetch_one() not supported for {self.db_type} database")
        
        try:
            self.cursor.execute(query, params)
            row = self.cursor.fetchone()
            
            if row is None:
                return None
            
            if self.db_type == 'sqlite':
                return dict(row)
            elif self.db_type == 'postgresql':
                columns = [desc[0] for desc in self.cursor.description]
                return dict(zip(columns, row))
            
        except Exception as e:
            logger.error(f"Error fetching one row: {e}\nQuery: {query}\nParams: {params}")
            raise
    
    def fetch_all(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Execute a query and fetch all results.
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            List of row results as dictionaries
        """
        if self.db_type not in ['sqlite', 'postgresql']:
            raise ValueError(f"fetch_all() not supported for {self.db_type} database")
        
        try:
            self.cursor.execute(query, params)
            rows = self.cursor.fetchall()
            
            if self.db_type == 'sqlite':
                return [dict(row) for row in rows]
            elif self.db_type == 'postgresql':
                columns = [desc[0] for desc in self.cursor.description]
                return [dict(zip(columns, row)) for row in rows]
            
        except Exception as e:
            logger.error(f"Error fetching all rows: {e}\nQuery: {query}\nParams: {params}")
            raise
    
    def insert(self, table: str, data: Dict[str, Any]) -> Any:
        """Insert data into a table.
        
        Args:
            table: Table name
            data: Data to insert as dictionary
            
        Returns:
            Inserted ID or result
        """
        if self.db_type == 'mongodb':
            try:
                collection = self.connection[table]
                result = collection.insert_one(data)
                return result.inserted_id
            except Exception as e:
                logger.error(f"Error inserting into MongoDB: {e}")
                raise
        else:  # SQL databases
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['?'] * len(data))
            query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
            
            try:
                self.cursor.execute(query, tuple(data.values()))
                self.connection.commit()
                
                if self.db_type == 'sqlite':
                    return self.cursor.lastrowid
                elif self.db_type == 'postgresql':
                    return self.cursor.fetchone()[0]  # Assuming RETURNING id
            except Exception as e:
                logger.error(f"Error inserting into {table}: {e}")
                self.connection.rollback()
                raise
    
    def update(self, table: str, data: Dict[str, Any], condition: str, params: tuple) -> int:
        """Update data in a table.
        
        Args:
            table: Table name
            data: Data to update as dictionary
            condition: WHERE condition
            params: Condition parameters
            
        Returns:
            Number of rows affected
        """
        if self.db_type == 'mongodb':
            try:
                collection = self.connection[table]
                result = collection.update_one(
                    self._parse_mongo_condition(condition, params),
                    {'$set': data}
                )
                return result.modified_count
            except Exception as e:
                logger.error(f"Error updating MongoDB: {e}")
                raise
        else:  # SQL databases
            set_clause = ', '.join([f"{k} = ?" for k in data.keys()])
            query = f"UPDATE {table} SET {set_clause} WHERE {condition}"
            
            try:
                self.cursor.execute(query, tuple(data.values()) + params)
                self.connection.commit()
                return self.cursor.rowcount
            except Exception as e:
                logger.error(f"Error updating {table}: {e}")
                self.connection.rollback()
                raise
    
    def delete(self, table: str, condition: str, params: tuple) -> int:
        """Delete data from a table.
        
        Args:
            table: Table name
            condition: WHERE condition
            params: Condition parameters
            
        Returns:
            Number of rows affected
        """
        if self.db_type == 'mongodb':
            try:
                collection = self.connection[table]
                result = collection.delete_many(
                    self._parse_mongo_condition(condition, params)
                )
                return result.deleted_count
            except Exception as e:
                logger.error(f"Error deleting from MongoDB: {e}")
                raise
        else:  # SQL databases
            query = f"DELETE FROM {table} WHERE {condition}"
            
            try:
                self.cursor.execute(query, params)
                self.connection.commit()
                return self.cursor.rowcount
            except Exception as e:
                logger.error(f"Error deleting from {table}: {e}")
                self.connection.rollback()
                raise
    
    def create_table(self, table: str, schema: str) -> None:
        """Create a table if it doesn't exist.
        
        Args:
            table: Table name
            schema: Table schema
        """
        if self.db_type == 'mongodb':
            # MongoDB creates collections automatically
            return
        else:  # SQL databases
            query = f"CREATE TABLE IF NOT EXISTS {table} ({schema})"
            
            try:
                self.cursor.execute(query)
                self.connection.commit()
                logger.info(f"Table {table} created or already exists")
            except Exception as e:
                logger.error(f"Error creating table {table}: {e}")
                self.connection.rollback()
                raise
    
    def create_index(self, table: str, columns: List[str], index_name: Optional[str] = None, unique: bool = False) -> None:
        """Create an index on a table.
        
        Args:
            table: Table name
            columns: Columns to index
            index_name: Index name (optional)
            unique: Whether the index should be unique
        """
        if self.db_type == 'mongodb':
            try:
                collection = self.connection[table]
                index_spec = [(col, pymongo.ASCENDING) for col in columns]
                collection.create_index(index_spec, unique=unique)
                logger.info(f"Index created on {table} for columns {columns}")
            except Exception as e:
                logger.error(f"Error creating MongoDB index: {e}")
                raise
        else:  # SQL databases
            if index_name is None:
                index_name = f"idx_{table}_{'_'.join(columns)}"
            
            unique_str = "UNIQUE " if unique else ""
            columns_str = ', '.join(columns)
            query = f"CREATE {unique_str}INDEX IF NOT EXISTS {index_name} ON {table} ({columns_str})"
            
            try:
                self.cursor.execute(query)
                self.connection.commit()
                logger.info(f"Index {index_name} created on {table}")
            except Exception as e:
                logger.error(f"Error creating index on {table}: {e}")
                self.connection.rollback()
                raise
    
    def begin_transaction(self) -> None:
        """Begin a transaction."""
        if self.db_type in ['sqlite', 'postgresql']:
            self.connection.begin()
            logger.debug("Transaction started")
    
    def commit(self) -> None:
        """Commit the current transaction."""
        if self.db_type in ['sqlite', 'postgresql']:
            self.connection.commit()
            logger.debug("Transaction committed")
    
    def rollback(self) -> None:
        """Rollback the current transaction."""
        if self.db_type in ['sqlite', 'postgresql']:
            self.connection.rollback()
            logger.debug("Transaction rolled back")
    
    def close(self) -> None:
        """Close the database connection."""
        if self.db_type in ['sqlite', 'postgresql'] and self.connection:
            self.connection.close()
            logger.info("Database connection closed")
        elif self.db_type == 'mongodb' and hasattr(self.connection, 'client'):
            self.connection.client.close()
            logger.info("MongoDB connection closed")
    
    def _parse_mongo_condition(self, condition: str, params: tuple) -> Dict[str, Any]:
        """Parse SQL-like condition to MongoDB query.
        
        This is a simple implementation that handles basic conditions.
        For complex queries, use MongoDB's native query syntax directly.
        
        Args:
            condition: SQL-like condition string (e.g., "id = ?")
            params: Condition parameters
            
        Returns:
            MongoDB query dictionary
        """
        # Very basic implementation - in a real system, use a proper SQL parser
        mongo_query = {}
        
        # Handle simple equality conditions
        if '=' in condition and '!=' not in condition and '<' not in condition and '>' not in condition:
            field = condition.split('=')[0].strip()
            mongo_query[field] = params[0]
        elif 'IN' in condition.upper():
            # Handle IN conditions
            field = condition.split('IN')[0].strip()
            mongo_query[field] = {'$in': list(params)}
        else:
            # For more complex conditions, log a warning
            logger.warning(f"Complex condition '{condition}' might not be correctly translated to MongoDB query")
            # Attempt a basic translation for common operators
            if '!=' in condition:
                field = condition.split('!=')[0].strip()
                mongo_query[field] = {'$ne': params[0]}
            elif '>' in condition:
                field = condition.split('>')[0].strip()
                mongo_query[field] = {'$gt': params[0]}
            elif '<' in condition:
                field = condition.split('<')[0].strip()
                mongo_query[field] = {'$lt': params[0]}
            elif 'LIKE' in condition.upper():
                field = condition.split('LIKE')[0].strip()
                # Convert SQL LIKE pattern to regex
                pattern = params[0].replace('%', '.*')
                mongo_query[field] = {'$regex': pattern, '$options': 'i'}
        
        return mongo_query