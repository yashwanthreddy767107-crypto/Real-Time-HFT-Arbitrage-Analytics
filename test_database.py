import psycopg2

try:
    connection = psycopg2.connect(
        host="localhost",
        port="5432",
        database="HFT_Arbitrage",
        user="postgres",
        password="MyTCR@2005"
    )

    print("Database connection successful!")

    connection.close()

except Exception as error:
    print("Database connection failed!")
    print(error)