# PokerStars Hand History Export
Export hand history from PokerStars with a script


This is only tested with pokerstarsmi.com but might work for other PokerStars variants


I play PokerStars on iOS but want to review my hand history on macOS using PokerTracker 4

I wrote this script so I can automatically export hand history on a cron job every half hour

Even though the API call is for 7 days of hand history, in my experience PokerStars only sends 200 hands max, so I run it every half hour

The export goes to my email and then I have a rule in Gmail to auto-forward it to a throwaway email address

I configured PokerTracker 4 with the throwaway email address POP3 credentials and it can retrieve the exported hand history from there

# How to use
git clone https://github.com/reillychase/pokerstars-handhistory-export.git


Replace YOUR_USERNAME and YOUR_PASSWORD

(Optional) Change pokerstarsmi.com to the PokerStars website you are using


pip3 install stealth_requests

python3 main.py
