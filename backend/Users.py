import sqlite3
import uuid

class Users:
    def __init__(self):
        try:
            self.database = './db/database.db'
            print("Database configuration initialized")
        except sqlite3.Error as error:
            print("Error during initialization", error)

    def _get_connection(self):
        return sqlite3.connect(self.database)

    def create_user(self, username, email, password):
        """ Create a new user

        Args:
            username (string): username of the user
            email (string): email of the user
            password (string): password of the user

        Returns:
            string: id of the created user
            if the email already exists, return 400
            if there is an error, return 500
        """
        try:
            connection = self._get_connection()
            cursor = connection.cursor()
            id = str(uuid.uuid4())
            query = "INSERT INTO Users (id, username, email, password) VALUES (?, ?, ?, ?)"
            cursor.execute(query, (id, username, email, password))
            connection.commit()
            connection.close()
            return id
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed" in str(e):
                print("Error: Email already exists.")
            else:
                print("Integrity error:", e)
            return 400
        except Exception as e:
            print(e)
            return 500
          
    def get_user_password(self, email):
        """ Get user password for validation
        
        Args:
            email (string): email of the user
            
        Returns:
            string: password of the user
            if the user is not found or any other error, return None
        """
        
        try:
            connection = self._get_connection()
            cursor = connection.cursor()
            query = "SELECT password FROM Users WHERE email = ?"
            cursor.execute(query, (email,))
            password = cursor.fetchone()
            connection.close()
            if password is None:
                return None
            return password[0]
        except Exception as e:
            print(e)
            return None
          
    def login_user(self, email, password):
        """ Login user
        
        Args:
            email (string): email of the user
            password (string): password of the user
            
        Returns:
            string: id of the user
            if the user is not found or any other error, return None
        """
        try:
            connection = self._get_connection()
            cursor = connection.cursor()
            query = "SELECT * FROM Users WHERE email = ? AND password = ?"
            cursor.execute(query, (email, password))
            user = cursor.fetchone()
            connection.close()
            if user is None:
                return None
            return user[0]
        except Exception as e:
            print(e)
            return None