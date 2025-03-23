from config import get_db_connection

class BaseService:

    @staticmethod
    def get_db_connection():

        return get_db_connection()