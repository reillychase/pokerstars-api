# get_balance.py
from pokerstars import PokerStars 

# Create an instance (object) of the class
account = PokerStars()

# Test the methods
account.login()
account.get_balance()
account.logout()