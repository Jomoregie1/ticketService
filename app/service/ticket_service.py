from config import get_db_connection


class TicketService:
    @staticmethod
    def create_ticket(description, status, userid, itemid):
        """
        Creates a new ticket in the database.
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Validate itemID
            item_query = "SELECT itemid FROM item WHERE itemid = %s"
            cursor.execute(item_query, (itemid,))
            if cursor.fetchone() is None:
                return {"error": "Invalid itemID. Item does not exist."}, 400

            query = """
                INSERT INTO ticket (description, timestamp, status, userid, itemid)
                VALUES (%s, NOW(), %s, %s, %s)
            """
            cursor.execute(query, (description, status, userid, itemid))
            conn.commit()
            ticket_id = cursor.lastrowid
            return {"message": "Ticket created successfully!", "ticketid": ticket_id}, 201
        except Exception as e:
            return {"error": f"An error occurred: {e}"}, 500
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def get_tickets_by_user(userid):
        """
        Retrieve all tickets for a specific user from the database.
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            query = "SELECT * FROM ticket WHERE userid = %s ORDER BY timestamp DESC"
            cursor.execute(query, (userid,))
            tickets = cursor.fetchall()
            return tickets
        except Exception as e:
            raise Exception(f"An error occurred while retrieving tickets: {e}")
        finally:
            cursor.close()
            conn.close()
