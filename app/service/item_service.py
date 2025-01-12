from config import get_db_connection


class ItemService:
    @staticmethod
    def get_all_items():
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            query = "SELECT itemid AS id, model AS name FROM item"  # Map database fields to 'id' and 'name'
            cursor.execute(query)
            items = cursor.fetchall()
            print("Fetched items:", items)  # Debug log
            return items
        except Exception as e:
            print("Error fetching items:", e)
            raise
        finally:
            cursor.close()
            conn.close()