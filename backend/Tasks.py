import sqlite3
import uuid

class Tasks:
    def __init__(self):
        try:
            self.database = './db/database.db'
            print("Database configuration initialized")
        except sqlite3.Error as error:
            print("Error during initialization", error)
            
    def _get_connection(self):
        return sqlite3.connect(self.database)
      
    def get_tasks(self, user_id):
        """ Return all tasks from a user

        Args:
            user_id (string): id of the user to get tasks

        Returns:
            list: list of tasks
        """
        try:
            connection = self._get_connection()
            cursor = connection.cursor()
            query = "SELECT * FROM Tasks WHERE user_id = ?"
            cursor.execute(query, (user_id,))
            tasks = cursor.fetchall()
            connection.close()
            tasks = [{'id': task[0], 'name': task[1], 'description': task[2], 'status': task[3]} for task in tasks]
            return tasks
        except Exception as e:
            print(e)
            return None
          
    def create_task(self, user_id, name, description):
        """ Create a task for a user

        Args:
            user_id (string): id of the user to create the task
            name (string): name of the task
            description (string): description of the task

        Returns:
            string: id of the created task
            if the task already exists, return 400
            if there is an error, return 500
        """
        try:
            connection = self._get_connection()
            cursor = connection.cursor()
            id = str(uuid.uuid4())
            query = "INSERT INTO Tasks (id, user_id, name, description) VALUES (?, ?, ?, ?)"
            cursor.execute(query, (id, user_id, name, description))
            connection.commit()
            connection.close()
            return id
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed" in str(e):
                print("Error: Task already exists.")
            else:
                print("Integrity error:", e)
            return 400
        except Exception as e:
            print(e)
            return 500
          
    def update_task(self, task_id, name, description):
        """ Update a task
            Updates only the fields that are not empty

        Args:
            task_id (string): id of the task to update
            name (string): new name of the task
            description (string): new description of the task

        Returns:
            bool: True if the task was updated, False otherwise
            int: status code
        """
        try:
            connection = self._get_connection()
            cursor = connection.cursor()
            query = ""
            if name == "" and description != "":
                query = "UPDATE Tasks SET description = ? WHERE id = ?"
                cursor.execute(query, (description, task_id))
            elif name != "" and description == "":
                query = "UPDATE Tasks SET name = ? WHERE id = ?"
                cursor.execute(query, (name, task_id))
            elif name != "" and description != "":
                query = "UPDATE Tasks SET name = ?, description = ? WHERE id = ?"
                cursor.execute(query, (name, description, task_id))
            connection.commit()
            connection.close()
            return True, 200
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed" in str(e):
                print("Error: Task already exists.")
            else:
                print("Integrity error:", e)
            return False, 400
        except Exception as e:
            print(e)
            return False, 500
          
    def delete_task(self, task_id):
        """ Delete a task

        Args:
            task_id (string): id of the task to delete

        Returns:
            bool: True if the task was deleted, False otherwise
        """
        try:
            connection = self._get_connection()
            cursor = connection.cursor()
            query = "DELETE FROM Tasks WHERE id = ?"
            cursor.execute(query, (task_id,))
            connection.commit()
            connection.close()
            return True
        except Exception as e:
            print(e)
            return False
          
    def change_task_status(self, task_id, status):
        """ Change the status of a task to 'pendente' or 'completa'

        Args:
            task_id (string): id of the task to change status
            status (string): status to change the task to

        Returns:
            bool: True if the status was changed, False otherwise
        """
        try:
            connection = self._get_connection()
            cursor = connection.cursor()
            query = "UPDATE Tasks SET status = ? WHERE id = ?"
            cursor.execute(query, (status, task_id))
            connection.commit()
            connection.close()
            return True
        except Exception as e:
            print(e)
            return False
