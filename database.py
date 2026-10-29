import psycopg2


def get_connection():
    """
    Create and return a PostgreSQL database connection.
    """

    try:
        connection = psycopg2.connect(
            host="localhost",
            port="5432",
            database="HFT_Arbitrage",
            user="postgres",
            password="MyTCR@2005"
        )

        return connection

    except Exception as error:

        print("Database connection error:")
        print(error)

        return None