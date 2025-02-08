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
                INSERT INTO ticket (description, date, status, userid, itemid)
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
            query = "SELECT * FROM ticket WHERE userid = %s ORDER BY date DESC"
            cursor.execute(query, (userid,))
            tickets = cursor.fetchall()
            return tickets
        except Exception as e:
            raise Exception(f"An error occurred while retrieving tickets: {e}")
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def get_ticket_by_id(ticket_id, userid):
        """
        Fetch a single ticket by ID and ensure it belongs to the logged-in user.
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            query = "SELECT * FROM tickets WHERE ticketid = %s AND userid = %s"
            cursor.execute(query, (ticket_id, userid))
            ticket = cursor.fetchone()
            return ticket
        except Exception as e:
            return None
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def delete_ticket(ticket_id, userid):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            query = "DELETE FROM ticket WHERE ticketid = %s AND userid = %s"
            cursor.execute(query, (ticket_id, userid))
            conn.commit()

            if cursor.rowcount > 0:
                return {"message": "Ticket deleted successfully"}, 200
            else:
                return {"error": "Ticket not found or unauthorized"}, 404
        except Exception as e:
            return {"error": str(e)}, 500
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def update_ticket(ticket_id, userid, description, itemid):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            query = "UPDATE ticket SET description = %s, itemid = %s WHERE ticketid = %s AND userid = %s"
            cursor.execute(query, (description, itemid, ticket_id, userid))
            conn.commit()

            if cursor.rowcount > 0:
                return {"message": "Ticket updated successfully"}, 200
            else:
                return {"error": "Ticket not found or unauthorized"}, 404
        except Exception as e:
            return {"error": str(e)}, 500
        finally:
            cursor.close()
            conn.close()