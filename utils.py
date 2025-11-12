"""
Utility functions for PNL Calculator.
"""

from decimal import Decimal
from typing import Optional
from datetime import datetime


def format_balance(balance: Optional[int], decimals: Optional[int]) -> float:
    """
    Scale raw balance from wei/smallest unit to human-readable decimal.
    
    Args:
        balance: Raw balance in smallest unit (e.g., wei for ETH)
        decimals: Number of decimals for the token
        
    Returns:
        Scaled balance as float
        
    Example:
        >>> format_balance(1000000000000000000, 18)  # 1 ETH
        1.0
        >>> format_balance(1000000, 6)  # 1 USDC
        1.0
    """
    if balance is None or decimals is None:
        return 0.0
    
    if balance == 0:
        return 0.0
        
    return float(Decimal(balance) / Decimal(10 ** decimals))


def format_currency(amount: float, currency: str = "USD") -> str:
    """
    Format currency amount for display.
    
    Args:
        amount: Numeric amount
        currency: Currency code (default: USD)
        
    Returns:
        Formatted currency string
        
    Example:
        >>> format_currency(1234.56)
        '$1,234.56'
        >>> format_currency(-123.45)
        '-$123.45'
    """
    sign = "-" if amount < 0 else ""
    abs_amount = abs(amount)
    
    if currency == "USD":
        return f"{sign}${abs_amount:,.2f}"
    else:
        return f"{sign}{abs_amount:,.2f} {currency}"


def format_percentage(value: float) -> str:
    """
    Format percentage for display.
    
    Args:
        value: Percentage value (e.g., 25.5 for 25.5%)
        
    Returns:
        Formatted percentage string
        
    Example:
        >>> format_percentage(25.5)
        '+25.50%'
        >>> format_percentage(-10.25)
        '-10.25%'
    """
    sign = "+" if value >= 0 else ""
    return f"{sign}{value:.2f}%"


def calculate_roi(invested: float, current_value: float) -> float:
    """
    Calculate Return on Investment percentage.
    
    Args:
        invested: Total amount invested
        current_value: Current value of investment
        
    Returns:
        ROI as percentage
        
    Example:
        >>> calculate_roi(1000, 1500)
        50.0
        >>> calculate_roi(1000, 800)
        -20.0
    """
    if invested == 0:
        return 0.0
    
    return ((current_value - invested) / invested) * 100


def is_address_equal(addr1: Optional[str], addr2: Optional[str]) -> bool:
    """
    Compare two Ethereum addresses (case-insensitive).
    
    Args:
        addr1: First address
        addr2: Second address
        
    Returns:
        True if addresses match (case-insensitive)
    """
    if addr1 is None or addr2 is None:
        return False
    
    return addr1.lower() == addr2.lower()


def truncate_address(address: str, prefix: int = 6, suffix: int = 4) -> str:
    """
    Truncate Ethereum address for display.
    
    Args:
        address: Full Ethereum address
        prefix: Number of characters to show at start
        suffix: Number of characters to show at end
        
    Returns:
        Truncated address string
        
    Example:
        >>> truncate_address("0x1234567890abcdef1234567890abcdef12345678")
        '0x1234...5678'
    """
    if len(address) <= prefix + suffix + 2:  # +2 for '0x'
        return address
    
    return f"{address[:prefix]}...{address[-suffix:]}"


def format_timestamp(dt: datetime) -> str:
    """
    Format datetime for display.
    
    Args:
        dt: Datetime object
        
    Returns:
        Formatted date string
    """
    return dt.strftime("%Y-%m-%d %H:%M:%S UTC")


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safely divide two numbers, returning default if denominator is 0.
    
    Args:
        numerator: Numerator value
        denominator: Denominator value
        default: Value to return if division by zero
        
    Returns:
        Result of division or default
    """
    if denominator == 0:
        return default
    
    return numerator / denominator


def clamp(value: float, min_val: float, max_val: float) -> float:
    """
    Clamp a value between min and max.
    
    Args:
        value: Value to clamp
        min_val: Minimum allowed value
        max_val: Maximum allowed value
        
    Returns:
        Clamped value
    """
    return max(min_val, min(value, max_val))


def is_approximately_equal(a: float, b: float, tolerance: float = 0.0001) -> bool:
    """
    Check if two floats are approximately equal within tolerance.
    
    Args:
        a: First value
        b: Second value
        tolerance: Allowed difference
        
    Returns:
        True if values are within tolerance
        
    Example:
        >>> is_approximately_equal(1.0, 1.00001, 0.001)
        True
        >>> is_approximately_equal(1.0, 1.1, 0.01)
        False
    """
    return abs(a - b) <= tolerance
