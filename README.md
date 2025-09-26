# PokerStars Hand History Export
Export hand history from PokerStars with a script, now with the new email PIN login support and a webpage to toggle the cron on/off or run once

This is only tested with pokerstarsmi.com but might work for other PokerStars variants

I play PokerStars on iOS but want to review my hand history on macOS using PokerTracker 4

I wrote this script so I can automatically export hand history on a cron job every half hour

Even though the API call is for 7 days of hand history, in my experience PokerStars only sends 200 hands max, so I run it every 15 minutes to make sure I get all hands

The export goes to my email and I have a rule in Gmail

I configured PokerTracker 4 with the email address POP3 credentials and it can retrieve the exported hand history from there

For security, to not share my actual email password with this script or PokerTracker 4, I have created a throwaway email address for my PokerStars account for this purpose

# How to use
Install git and download this repo
```
apt-get install git
cd /root/
git clone https://github.com/reillychase/pokerstars-handhistory-export.git
```

Update these in main.py

```
POP3_SERVER = 'pop.gmail.com'
POP3_PORT = 995
EMAIL_ADDRESS = ''  # Replace with your email
EMAIL_PASSWORD = ''  # Replace with your app-specific password
POKERSTARS_USERNAME = ''
POKERSTARS_PASSWORD = ''
POKERSTARS_WEBSITE = 'https://www.pokerstarsmi.com'
```
Install the webserver
```
apt install apache2-utils -y
```
Move files into place
```
cd /root/pokerstars-handhistory-export
mv * /var/www/scripts
cd /var/www/scripts
mv index.php /var/www/html
python3 -m venv .venv
source .venv/bin/activate
pip install stealth_requests

```
Create the 15 minute cron
```
crontab -e
*/15 * * * * /var/www/scripts/main.sh >> /var/www/scripts/main.log 2>&1
```

