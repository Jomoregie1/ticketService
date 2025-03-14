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
    def get_all_tickets():
        """Retrieve all tickets for admin and sort by date."""
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
        SELECT ticket.ticketid, ticket.description, ticket.date, ticket.status, 
               user.email AS user_email, ticket.itemid
        FROM ticket
        JOIN user ON ticket.userid = user.id
        """
        cursor.execute(query)
        tickets = cursor.fetchall()

        sorted_tickets = TicketService.merge_sort_tickets(tickets, key="date")  # Sort by date

        cursor.close()
        conn.close()
        return sorted_tickets

    @staticmethod
    def update_ticket_status(ticket_id, new_status):
        conn = get_db_connection()
        cursor = conn.cursor()
        query = "UPDATE ticket SET status = %s WHERE ticketid = %s"
        cursor.execute(query, (new_status, ticket_id))
        conn.commit()
        cursor.close()
        conn.close()
        return {"message": "Ticket status updated successfully!"}, 200

    @staticmethod
    def add_manufacturer(name):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            query = "INSERT INTO manufacturers (name) VALUES (%s)"
            cursor.execute(query, (name,))
            conn.commit()
            cursor.close()
            conn.close()
            return {"message": "Manufacturer added successfully"}, 201
        except Exception as e:
            return {"error": str(e)}, 500

    @staticmethod
    def get_tickets_by_user(userid):
        """
        Retrieve all tickets for a specific user and sort them by date (newest first).
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            query = "SELECT * FROM ticket WHERE userid = %s"
            cursor.execute(query, (userid,))
            tickets = cursor.fetchall()

            sorted_tickets = TicketService.merge_sort_tickets(tickets, key="date")  # Sort by date
            return sorted_tickets
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
            query = "SELECT * FROM ticket WHERE ticketid = %s AND userid = %s"
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
    def delete_ticket_superuser(ticket_id, userid=None, is_superuser=False):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            if is_superuser:
                query = "DELETE FROM ticket WHERE ticketid = %s"
                cursor.execute(query, (ticket_id,))
            else:
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

    @staticmethod
    def get_all_manufacturers():
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            query = "SELECT * FROM manufacturer"
            cursor.execute(query)
            manufacturers = cursor.fetchall()
            cursor.close()
            conn.close()
            return manufacturers
        except Exception as e:
            return []

    @staticmethod
    def merge_sort_tickets(tickets, key="date"):
        """
        Sorts a list of tickets using Merge Sort based on the specified key.
        Default sorting key is 'date'.
        """
        if len(tickets) <= 1:
            return tickets

        mid = len(tickets) // 2
        left_half = TicketService.merge_sort_tickets(tickets[:mid], key)
        right_half = TicketService.merge_sort_tickets(tickets[mid:], key)

        return TicketService.merge(left_half, right_half, key)

    @staticmethod
    def merge(left, right, key):
        """Helper function to merge two sorted halves."""
        sorted_tickets = []
        i = j = 0

        while i < len(left) and j < len(right):
            if left[i][key] >= right[j][key]:  # Sort by date descending (latest first)
                sorted_tickets.append(left[i])
                i += 1
            else:
                sorted_tickets.append(right[j])
                j += 1

        # Append remaining items
        sorted_tickets.extend(left[i:])
        sorted_tickets.extend(right[j:])

        return sorted_tickets
