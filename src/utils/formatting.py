def format_currency(amount: float) -> str:
    """Format a float amount to Indian Rupee string."""
    return f"₹{amount:,.2f}"

def format_percentage(value: float) -> str:
    """Format a float to percentage string."""
    return f"{value:.1f}%"
