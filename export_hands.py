# export_hands.py
from pokerstars import PokerStars 

# Create an instance (object) of the class
account = PokerStars()

# Test the methods
account.login()
account.export_hands()
account.logout()