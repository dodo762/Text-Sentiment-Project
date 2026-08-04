import os

import mysql.connector
#to load environment variables from a .env file
from dotenv import load_dotenv
#to handle MySQL connection errors
from mysql.connector import Error

#Load variables stored inside the .env file(Load database settings from .env)
load_dotenv()

#When we need to access database, can call this function 
def get_database_connection():
    """
    Create and return a new MySQL database connection  
    """
    try:
        #Establish a connection to the MySQL database using environment variables
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT", "3306")),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )

        return connection
    
    #Handle any errors that occur during the connection attempt
    except Error as error:
        print("Database connection failed:", error)
        return None

#Temporary test to check if the database connection works when running this script directly
if __name__ == "__main__":
    connection = get_database_connection()

    if connection is not None and connection.is_connected():
        print("Python connected to MySQL successfully.")
        print("Database:", connection.database)

        connection.close()
        print("Database connection closed.")