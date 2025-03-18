from config import get_db_connection

class BaseService:
    """
    Base service class to provide a common database connection method
    and enforce structure across all service classes.
    Allows for inheritance
    """

    @staticmethod
    def get_db_connection():
        """Provides a reusable database connection."""
        return get_db_connection()