"""
Profit and Loss calculation utilities.

This module calculates estimated profit and loss from
prices and transaction costs supplied by the application.
It does not connect to a live trading exchange.
"""


def calculate_net_profit(
    buy_price,
    sell_price,
    quantity=1.0,
    buy_fee=0.0,
    sell_fee=0.0,
    other_costs=0.0,
):
    """
    Calculate estimated net profit for a simulated trade.

    Parameters:
        buy_price: Price per unit when buying.
        sell_price: Price per unit when selling.
        quantity: Number of units.
        buy_fee: Total buying transaction fee.
        sell_fee: Total selling transaction fee.
        other_costs: Other estimated costs.

    Returns:
        Dictionary containing gross spread, costs,
        estimated net profit, and result status.
    """

    values = [
        buy_price,
        sell_price,
        quantity,
        buy_fee,
        sell_fee,
        other_costs,
    ]

    try:
        values = [float(value) for value in values]
    except (TypeError, ValueError):
        raise ValueError("All inputs must be valid numbers.")

    buy_price, sell_price, quantity, buy_fee, sell_fee, other_costs = values

    if not all(__import__("math").isfinite(value) for value in values):
        raise ValueError("Inputs must be finite numbers.")

    if buy_price < 0 or sell_price < 0:
        raise ValueError("Prices cannot be negative.")

    if quantity <= 0:
        raise ValueError("Quantity must be greater than zero.")

    if buy_fee < 0 or sell_fee < 0 or other_costs < 0:
        raise ValueError("Costs cannot be negative.")

    gross_spread = (sell_price - buy_price) * quantity
    total_costs = buy_fee + sell_fee + other_costs
    net_profit = gross_spread - total_costs

    if net_profit > 0:
        status = "PROFIT"
    elif net_profit < 0:
        status = "LOSS"
    else:
        status = "NEUTRAL"

    return {
        "buy_price": buy_price,
        "sell_price": sell_price,
        "quantity": quantity,
        "gross_spread": round(gross_spread, 8),
        "total_costs": round(total_costs, 8),
        "net_profit": round(net_profit, 8),
        "status": status,
    }


if __name__ == "__main__":
    # Example test only; these values are not live market data.
    result = calculate_net_profit(
        buy_price=90000,
        sell_price=90500,
        quantity=1,
        buy_fee=75,
        sell_fee=75,
    )

    print("\n--- Profit/Loss Test ---")
    print(f"Gross spread: {result['gross_spread']:.2f}")
    print(f"Total costs:  {result['total_costs']:.2f}")
    print(f"Net profit:   {result['net_profit']:.2f}")
    print(f"Status:       {result['status']}")