import time
import random
from decimal import Decimal
from database import get_connection


# ============================================================
# CONFIGURATION
# ============================================================

SYMBOLS = [
    "BTC/USDT",
    "ETH/USDT",
    "SOL/USDT",
    "BNB/USDT",
    "XRP/USDT"
]

EXCHANGES = [
    "SIM_EXCHANGE_A",
    "SIM_EXCHANGE_B",
    "SIM_EXCHANGE_C",
    "SIM_EXCHANGE_D",
    "SIM_EXCHANGE_E"
]

BASE_PRICES = {
    "BTC/USDT": Decimal("90000.00"),
    "ETH/USDT": Decimal("3500.00"),
    "SOL/USDT": Decimal("150.00"),
    "BNB/USDT": Decimal("600.00"),
    "XRP/USDT": Decimal("2.50")
}

UPDATE_INTERVAL = 5


# ============================================================
# GENERATE MARKET PRICE
# ============================================================

def generate_market_price(symbol, exchange):

    base_price = BASE_PRICES[symbol]

    # General market movement
    random_change = Decimal(
        str(
            random.uniform(
                float(base_price * Decimal("-0.003")),
                float(base_price * Decimal("0.003"))
            )
        )
    )

    # Exchange-specific price difference
    exchange_difference = Decimal("0")

    if exchange == "SIM_EXCHANGE_A":
        exchange_difference = Decimal(
            str(
                random.uniform(
                    float(base_price * Decimal("-0.001")),
                    float(base_price * Decimal("0.001"))
                )
            )
        )

    elif exchange == "SIM_EXCHANGE_B":
        exchange_difference = Decimal(
            str(
                random.uniform(
                    float(base_price * Decimal("-0.003")),
                    float(base_price * Decimal("0.003"))
                )
            )
        )

    elif exchange == "SIM_EXCHANGE_C":
        exchange_difference = Decimal(
            str(
                random.uniform(
                    float(base_price * Decimal("-0.002")),
                    float(base_price * Decimal("0.002"))
                )
            )
        )

    elif exchange == "SIM_EXCHANGE_D":
        exchange_difference = Decimal(
            str(
                random.uniform(
                    float(base_price * Decimal("-0.004")),
                    float(base_price * Decimal("0.004"))
                )
            )
        )

    elif exchange == "SIM_EXCHANGE_E":
        exchange_difference = Decimal(
            str(
                random.uniform(
                    float(base_price * Decimal("-0.0025")),
                    float(base_price * Decimal("0.0025"))
                )
            )
        )

    # Calculate bid price
    bid_price = base_price + random_change + exchange_difference

    # Spread depends on the asset
    if symbol == "BTC/USDT":
        spread = Decimal(str(random.uniform(3, 15)))

    elif symbol == "ETH/USDT":
        spread = Decimal(str(random.uniform(1, 8)))

    elif symbol == "SOL/USDT":
        spread = Decimal(str(random.uniform(0.10, 1.0)))

    elif symbol == "BNB/USDT":
        spread = Decimal(str(random.uniform(0.50, 3.0)))

    else:
        spread = Decimal(str(random.uniform(0.01, 0.05)))

    ask_price = bid_price + spread

    return (
        bid_price.quantize(Decimal("0.00000001")),
        ask_price.quantize(Decimal("0.00000001"))
    )


# ============================================================
# INSERT MARKET DATA
# ============================================================

def insert_market_data(
    cursor,
    exchange,
    symbol,
    bid_price,
    ask_price
):

    query = """
    INSERT INTO public.market_data (
        timestamp,
        exchange,
        symbol,
        bid_price,
        ask_price
    )
    VALUES (
        CURRENT_TIMESTAMP,
        %s,
        %s,
        %s,
        %s
    );
    """

    cursor.execute(
        query,
        (
            exchange,
            symbol,
            bid_price,
            ask_price
        )
    )


# ============================================================
# MAIN PROGRAM
# ============================================================

def main():

    print("=" * 70)
    print("MULTI-CRYPTO HFT MARKET DATA SIMULATOR")
    print("=" * 70)

    print("\nCryptocurrencies:")
    for symbol in SYMBOLS:
        print(f"  - {symbol}")

    print("\nExchanges:")
    for exchange in EXCHANGES:
        print(f"  - {exchange}")

    connection = get_connection()

    if connection is None:

        print("\nCould not connect to PostgreSQL.")
        return

    print("\nConnected to PostgreSQL successfully!")

    try:

        cursor = connection.cursor()

        while True:

            print("\n")
            print("=" * 70)
            print("GENERATING MARKET DATA")
            print("=" * 70)

            total_records = 0

            for symbol in SYMBOLS:

                print(f"\n📊 {symbol}")

                for exchange in EXCHANGES:

                    bid_price, ask_price = generate_market_price(
                        symbol,
                        exchange
                    )

                    insert_market_data(
                        cursor,
                        exchange,
                        symbol,
                        bid_price,
                        ask_price
                    )

                    total_records += 1

                    print(
                        f"{exchange:<20} "
                        f"Bid: {bid_price:<15} "
                        f"Ask: {ask_price}"
                    )

            connection.commit()

            print("\n" + "-" * 70)
            print(f"Saved {total_records} market records to PostgreSQL.")
            print(f"Waiting {UPDATE_INTERVAL} seconds...")
            print("-" * 70)

            time.sleep(UPDATE_INTERVAL)

    except KeyboardInterrupt:

        print("\n\nMarket simulator stopped by user.")

    except Exception as error:

        print("\nSimulator Error:")
        print(error)

    finally:

        if connection:

            connection.close()

            print("\nDatabase connection closed.")


# ============================================================
# START PROGRAM
# ============================================================

if __name__ == "__main__":
    main()