import psycopg2
from datetime import datetime, timezone

try:
    connection = psycopg2.connect(
        host="localhost",
        port=5432,
        database="HFT_Arbitrage",
        user="postgres",
        password="MyTCR@2005"
    )

    cursor = connection.cursor()

    query = """
        INSERT INTO market_data
        (timestamp, exchange, symbol, bid_price, ask_price, bid_quantity, ask_quantity)
        VALUES (%s, %s, %s, %s, %s, %s, %s);
    """

    data = (
        datetime.now(timezone.utc),
        "TEST_EXCHANGE",
        "BTC/USDT",
        90000.00,
        90005.00,
        0.50,
        0.75
    )

    cursor.execute(query, data)

    connection.commit()

    print("Test market data inserted successfully!")

    cursor.close()
    connection.close()

except Exception as error:
    print("Error:")
    print(error)