# pnl_calculator/client.py
import sys
from covalent import CovalentClient

from .config import API_KEY


def get_covalent_client():
    client = CovalentClient(API_KEY)
    if not client.balance_service:
        print("Invalid API key.")
        sys.exit(1)
    return client