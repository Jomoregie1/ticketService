from config import get_db_connection
from app.service.base_service import BaseService


#service class for item related operations
class ItemService:
    @staticmethod
    def get_all_items():
        #fetches all the items from DB. takes the id, manufacturer, model, type and market price
        try:
            conn = BaseService.get_db_connection()
            cursor = conn.cursor(dictionary=True)

            # Fetch items
            query = "SELECT itemid AS id, manufacturerid, model AS name, typeid, market_price FROM item"
            cursor.execute(query)
            items = cursor.fetchall()

            # Fetch type names separately
            cursor.execute("SELECT typeid, typename FROM type")
            types = {row["typeid"]: row["typename"] for row in cursor.fetchall()}  # Dictionary {typeid: typename}

            # Fetch manufacturer names separately
            cursor.execute("SELECT manufacturerid, manufacturername FROM manufacturers")
            manufacturers = {row["manufacturerid"]: row["manufacturername"] for row in
                             cursor.fetchall()}

            #stores both of them in a dicionary

            print("Manufacturers Dictionary:", manufacturers)  # Debugging Print

            # attaches type and manufacturer names to the items
            for item in items:
                item["typename"] = types.get(item["typeid"], "Unknown")  # Default to 'Unknown'
                item["manufacturername"] = manufacturers.get(item["manufacturerid"], "Unknown")

            print("Fetched items with manufacturer:", items)  # Debug log
            return items
        except Exception as e:
            print("Error fetching items:", e)
            raise
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def get_item_by_id(itemid):

        #Fetch item details by ID for update and estimations where specific ticket needed

        try:
            conn = BaseService.get_db_connection()
            cursor = conn.cursor(dictionary=True)
            query = "SELECT model AS name, itemid, market_price FROM item WHERE itemid = %s"
            cursor.execute(query, (itemid,))
            item = cursor.fetchone()
            return item
        except Exception as e:        #more exception handling with debug
            print(f"ERROR: Could not fetch item {itemid} - {e}")
            return None
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def add_item(manufacturer_id, model, type_id, market_price): #admin enters values

        #adds a new item to the database

        try:
            conn = BaseService.get_db_connection()
            cursor = conn.cursor()

            query = "INSERT INTO item (manufacturerid, model, typeid, market_price) VALUES (%s, %s, %s, %s)" #values the admin enters
            cursor.execute(query, (manufacturer_id, model, type_id, market_price))
            conn.commit()
            item_id = cursor.lastrowid
            cursor.close()
            conn.close()
            return item_id, {"message": "Item added successfully"}, 201
        except Exception as e:
            return None, {"error": str(e)}, 500

    @staticmethod
    def get_all_item_types():

        #Retrieve all item types from the database. used when populating the dropdown menu in the selection for creating an item.

        try:
            conn = BaseService.get_db_connection()
            cursor = conn.cursor(dictionary=True)

            query = "SELECT typeid, typename FROM type"
            cursor.execute(query)
            types = cursor.fetchall()

            cursor.close()
            conn.close()
            return types
        except Exception as e:
            print("Error fetching item types:", e)
            return []