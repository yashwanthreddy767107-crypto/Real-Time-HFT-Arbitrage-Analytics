import time
from decimal import Decimal
from database import get_connection


# ============================================================
# CONFIGURATION
# ============================================================

DETECTOR_INTERVAL = 5

TRADING_FEE_PERCENTAGE = Decimal("0.001")

SLIPPAGE = Decimal("0.50")

MINIMUM_PROFIT = Decimal("10")


# ============================================================
# GET LATEST MARKET DATA
# ============================================================

def get_latest_market_data(cursor):

    query = """
    SELECT DISTINCT ON (exchange, symbol)
        exchange,
        symbol,
        bid_price,
        ask_price,
        timestamp
    FROM public.market_data
    ORDER BY exchange, symbol, timestamp DESC;
    """

    cursor.execute(query)

    return cursor.fetchall()


# ============================================================
# GROUP MARKET DATA BY SYMBOL
# ============================================================

def group_market_data(market_data):

    grouped_data = {}

    for row in market_data:

        exchange = row[0]
        symbol = row[1]
        bid_price = Decimal(str(row[2]))
        ask_price = Decimal(str(row[3]))
        timestamp = row[4]

        if symbol not in grouped_data:

            grouped_data[symbol] = []

        grouped_data[symbol].append(
            {
                "exchange": exchange,
                "bid_price": bid_price,
                "ask_price": ask_price,
                "timestamp": timestamp
            }
        )

    return grouped_data


# ============================================================
# FIND ARBITRAGE OPPORTUNITY
# ============================================================

def find_arbitrage_opportunity(market_data):

    if len(market_data) < 2:

        return None

    # Find exchange with lowest ASK price
    lowest_ask_record = min(
        market_data,
        key=lambda x: x["ask_price"]
    )

    # Find exchange with highest BID price
    highest_bid_record = max(
        market_data,
        key=lambda x: x["bid_price"]
    )

    buy_exchange = lowest_ask_record["exchange"]

    sell_exchange = highest_bid_record["exchange"]

    buy_price = lowest_ask_record["ask_price"]

    sell_price = highest_bid_record["bid_price"]

    # Cannot buy and sell on the same exchange
    if buy_exchange == sell_exchange:

        return None

    # Calculate spread
    spread = sell_price - buy_price

    # No arbitrage if spread is zero or negative
    if spread <= 0:

        return None

    # Calculate spread percentage
    spread_percent = (
        spread / buy_price
    ) * Decimal("100")

    # Calculate trading fees
    buy_fee = (
        buy_price *
        TRADING_FEE_PERCENTAGE
    )

    sell_fee = (
        sell_price *
        TRADING_FEE_PERCENTAGE
    )

    estimated_fees = buy_fee + sell_fee

    # Calculate net profit
    net_profit = (
        spread
        - estimated_fees
        - SLIPPAGE
    )

    return {

        "buy_exchange": buy_exchange,

        "sell_exchange": sell_exchange,

        "buy_price": buy_price,

        "sell_price": sell_price,

        "spread": spread,

        "spread_percent": spread_percent,

        "estimated_fees": estimated_fees,

        "estimated_slippage": SLIPPAGE,

        "net_profit": net_profit
    }


# ============================================================
# SAVE ARBITRAGE OPPORTUNITY
# ============================================================

def save_arbitrage_opportunity(
    cursor,
    symbol,
    opportunity
):

    query = """
    INSERT INTO public.arbitrage_opportunities (
        timestamp,
        symbol,
        buy_exchange,
        sell_exchange,
        buy_price,
        sell_price,
        spread,
        spread_percent,
        estimated_fees,
        estimated_slippage,
        net_profit
    )
    VALUES (
        CURRENT_TIMESTAMP,
        %s,
        %s,
        %s,
        %s,
        %s,
        %s,
        %s,
        %s,
        %s,
        %s
    );
    """

    cursor.execute(
        query,
        (
            symbol,

            opportunity["buy_exchange"],

            opportunity["sell_exchange"],

            opportunity["buy_price"],

            opportunity["sell_price"],

            opportunity["spread"],

            opportunity["spread_percent"],

            opportunity["estimated_fees"],

            opportunity["estimated_slippage"],

            opportunity["net_profit"]
        )
    )


# ============================================================
# PRINT ARBITRAGE OPPORTUNITY
# ============================================================

def print_opportunity(
    symbol,
    opportunity
):

    print("\n")

    print("=" * 70)

    print(
        f"ARBITRAGE ANALYSIS - {symbol}"
    )

    print("=" * 70)

    print()

    print(
        f"BUY EXCHANGE  : "
        f"{opportunity['buy_exchange']}"
    )

    print(
        f"BUY PRICE     : "
        f"{opportunity['buy_price']}"
    )

    print()

    print(
        f"SELL EXCHANGE : "
        f"{opportunity['sell_exchange']}"
    )

    print(
        f"SELL PRICE    : "
        f"{opportunity['sell_price']}"
    )

    print()

    print(
        f"SPREAD        : "
        f"{opportunity['spread']:.2f}"
    )

    print(
        f"SPREAD %      : "
        f"{opportunity['spread_percent']:.4f}%"
    )

    print(
        f"EST. FEES     : "
        f"{opportunity['estimated_fees']:.2f}"
    )

    print(
        f"SLIPPAGE      : "
        f"{opportunity['estimated_slippage']:.2f}"
    )

    print()

    print(
        f"NET PROFIT    : "
        f"{opportunity['net_profit']:.2f}"
    )


# ============================================================
# MAIN PROGRAM
# ============================================================

def main():

    print("=" * 70)

    print(
        "MULTI-CRYPTO HFT ARBITRAGE DETECTOR"
    )

    print("=" * 70)

    print()

    print(
        "Monitoring multiple cryptocurrencies "
        "and exchanges..."
    )

    while True:

        connection = get_connection()

        if connection is None:

            print(
                "\nDatabase connection failed."
            )

            time.sleep(
                DETECTOR_INTERVAL
            )

            continue

        try:

            cursor = connection.cursor()

            # Get latest prices
            market_data = get_latest_market_data(
                cursor
            )

            print("\n")

            print("=" * 70)

            print("LATEST MARKET DATA")

            print("=" * 70)

            for row in market_data:

                print(
                    f"{row[1]:<10} | "
                    f"{row[0]:<20} | "
                    f"Bid: {row[2]:<15} | "
                    f"Ask: {row[3]}"
                )

            # Group by cryptocurrency
            grouped_data = group_market_data(
                market_data
            )

            print("\n")

            print("=" * 70)

            print("ARBITRAGE SCAN")

            print("=" * 70)

            # Analyze every cryptocurrency
            for symbol, symbol_data in grouped_data.items():

                print(
                    f"\nScanning {symbol}..."
                )

                opportunity = (
                    find_arbitrage_opportunity(
                        symbol_data
                    )
                )

                if opportunity is None:

                    print(
                        f"No valid arbitrage "
                        f"opportunity for {symbol}."
                    )

                    continue

                print_opportunity(
                    symbol,
                    opportunity
                )

                # Check minimum profit
                if (
                    opportunity["net_profit"]
                    >= MINIMUM_PROFIT
                ):

                    print()

                    print("=" * 70)

                    print(
                        f"🚨 PROFITABLE OPPORTUNITY: "
                        f"{symbol}"
                    )

                    print("=" * 70)

                    save_arbitrage_opportunity(
                        cursor,
                        symbol,
                        opportunity
                    )

                    connection.commit()

                    print(
                        "\nOpportunity saved "
                        "to PostgreSQL!"
                    )

                else:

                    print()

                    print(
                        f"Net profit is below "
                        f"minimum threshold "
                        f"${MINIMUM_PROFIT}"
                    )

            print("\n")

            print(
                f"Waiting "
                f"{DETECTOR_INTERVAL} seconds..."
            )

            time.sleep(
                DETECTOR_INTERVAL
            )

        except KeyboardInterrupt:

            print(
                "\n\nArbitrage detector "
                "stopped by user."
            )

            break

        except Exception as error:

            print("\nDetector Error:")

            print(error)

        finally:

            if connection:

                connection.close()


# ============================================================
# START PROGRAM
# ============================================================

if __name__ == "__main__":

    main()