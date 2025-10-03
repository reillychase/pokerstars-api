# pokerstars.py
import stealth_requests as requests
import poplib
import email
from email.parser import BytesParser
import re
from email import policy
import os
from dotenv import load_dotenv
import time

# Load .env early (before class)
load_dotenv()  # Loads from .env in current dir; skips if not found

class PokerStars:
    """
    A simple class to query PokerStars account info
    """
    def __init__(self):
        # Settings
        self.POP3_SERVER = 'pop.gmail.com'
        self.POP3_PORT = 995
        self.EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
        self.EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')  # Your app-specific password
        self.POKERSTARS_USERNAME = os.getenv('POKERSTARS_USERNAME')
        self.POKERSTARS_PASSWORD = os.getenv('POKERSTARS_PASSWORD')
        self.POKERSTARS_WEBSITE = os.getenv('POKERSTARS_WEBSITE')
        self.POKERSTARS_FQDN = os.getenv('POKERSTARS_FQDN')
        self.DEV_PIN = int(os.getenv('DEV_PIN')) # For testing only, set to 0 for prod
        self.s = requests.StealthSession()
        self.x = self.s.get(self.POKERSTARS_WEBSITE)
    
    def login(self):
        """
        Logs in after requesting a PIN and retrieving it from email via POP3
        """
        def connect_to_pop3():
            # Connect to Gmail POP3 server with SSL
            try:
                server = poplib.POP3_SSL(self.POP3_SERVER, self.POP3_PORT)  # Use self. for attributes
                server.user(self.EMAIL_ADDRESS)
                server.pass_(self.EMAIL_PASSWORD)
                return server
            except Exception as e:
                print(f"Error connecting to POP3 server: {str(e)}")
                raise

        def fetch_and_search_pin_email(server, max_emails=100):
            # Get the number of emails
            pin = None  # Initialize outside try for clarity
            try:
                response, msg_list, octets = server.list()  # Unpack all three values
                num_messages = len(msg_list)
                print(f"Debug: Found {num_messages} emails in the inbox via POP3.")
                if num_messages == 0:
                    print("No emails found in the inbox.")
                    return None
               
                # Limit to recent emails to avoid timeouts
                search_limit = min(num_messages, max_emails)
                print(f"Debug: Searching up to {search_limit} most recent emails for PINs.")
               
                # Store matching emails (msg_num, PIN)
                pin_emails = []
               
                # Search backwards from newest to oldest
                for msg_num in range(num_messages, num_messages - search_limit, -1):
                    if msg_num < 1:
                        break  # Prevent invalid message numbers
                    try:
                        retr_response = server.retr(msg_num)
                        print(f"Debug: retr_response structure for Msg {msg_num}: {len(retr_response)} elements")
                        msg_lines = retr_response[1]  # Extract message lines
                        msg_content = b'\r\n'.join(msg_lines)
                       
                        # Parse and check for PIN email
                        msg = BytesParser(policy=policy.default).parsebytes(msg_content)
                        print(f"Debug: Checking Msg {msg_num} - From: {msg['from'][:50]}... Subject: {msg['subject'][:100]}...")
                       
                        if (msg['from'] and str('no_reply2@' + self.POKERSTARS_FQDN) in msg['from'].lower() and
                            msg['subject'] and 'one time pin' in msg['subject'].lower()):
                           
                            # Handle multipart email
                            if msg.is_multipart():
                                for part in msg.walk():
                                    if part.get_content_type() == 'text/plain':
                                        body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                                        print(f"Debug: Text/plain body excerpt (Msg {msg_num}): {body[:200]}...")
                                        # Search for PIN using flexible regex
                                        pin_match = re.search(r'PokerStars PIN[:\s]*(\d{6})', body, re.IGNORECASE)
                                        if pin_match:
                                            pin = pin_match.group(1)
                                            break
                            else:
                                body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
                                print(f"Debug: Non-multipart body excerpt (Msg {msg_num}): {body[:200]}...")
                                pin_match = re.search(r'PokerStars PIN[:\s]*(\d{6})', body, re.IGNORECASE)
                                if pin_match:
                                    pin = pin_match.group(1)
                           
                            if pin:
                                print(f"Debug: Found PIN {pin} in Msg {msg_num}")
                                pin_emails.append((msg_num, pin))
                               
                    except Exception as e:
                        print(f"Debug: Error processing Msg {msg_num}: {str(e)}")
                        continue
               
                if not pin_emails:
                    print("Debug: No PIN emails found in the searched messages.")
                    return None
               
                # Select the newest PIN email (highest msg_num)
                newest_pin_email = max(pin_emails, key=lambda x: x[0])
                print(f"Debug: Using newest PIN email (Msg {newest_pin_email[0]} with PIN {newest_pin_email[1]})")
                return newest_pin_email[1]
           
            except Exception as e:  # ADD THIS: Catch-all for the main try block (e.g., server.list() failures)
                print(f"Error in fetch_and_search_pin_email: {str(e)}")
                return None

        # Login to get PIN email sent
        url = self.POKERSTARS_WEBSITE + '/api/v1-preview/auth/session'  # Use self. for clarity
        myobj = {'installId': '102133820445328422', 'userId': self.POKERSTARS_USERNAME, 'password': self.POKERSTARS_PASSWORD}
        x = self.s.post(url, json=myobj)
        print(x.status_code)
        print(x.content)
        print(x.cookies)
        if self.DEV_PIN == 0:  # Use == instead of is for int comparison (minor, but best practice)
            # Sleep for 10 seconds to wait for PIN email to arrive
            time.sleep(10)
        # Connect to the POP3 server
        server = connect_to_pop3()
       
        # Fetch and search for the PIN email
        if self.DEV_PIN == 0:
            pin = fetch_and_search_pin_email(server)
        else:
            pin = self.DEV_PIN
        if pin:
            print(f"\n✅ Extracted PIN: {pin}")
        else:
            print("\n❌ No matching PIN email found via POP3.")
            print("\n💡 Quick Fix: Ensure the email has the 'Inbox' label in Gmail web interface.")
            print(" Go to gmail.com > Search for the email > Labels > Check 'Inbox'.")
       
        # Close the connection
        server.quit()
        # Try to Login again now with the pin
        url = self.POKERSTARS_WEBSITE + '/api/v1-preview/auth/session'
        myobj = {'installId': '102133820445328422','userId': self.POKERSTARS_USERNAME, 'password': self.POKERSTARS_PASSWORD, 'pin': pin,'errorCode': 'TEMP_PIN_REQUIRED'}
        x = self.s.post(url, json=myobj)
        print(x.status_code)
        print(x.content)
        print(x.cookies)
        r = x.json()
        token = r["token"]
        print("Token")
        print(token)
       
        # Force session transfer from other devices
        url = self.POKERSTARS_WEBSITE + '/api/v1-preview/auth/session'
        myobj = {
            "installId": "102133820445328422",
            "token": token,
            "remainingSeconds": 82,
            "idleSeconds": 698,
            "userId": self.POKERSTARS_USERNAME,
            "password": self.POKERSTARS_PASSWORD,
            "errorCode": "TEMP_PIN_REQUIRED",
            "pin": pin,
            "sessionTransfer": True }
        x = self.s.post(url, json=myobj)
        print(x.status_code)
        print(x.content)
        print(x.cookies)

    def logout(self):
        url = self.POKERSTARS_WEBSITE + '/api/v1-preview/auth/session'
        x = self.s.delete(url)
        print(x.status_code)
        print(x.content)
    
    def export_hands(self):
        """
        Exports last 7 days of hand history, but in my experience only 200 hands max will be provided by PokerStars
        """
        url = self.POKERSTARS_WEBSITE + '/api/v1-preview/account/history/client-history'
        myobj = {'locale': 0, 'requestType': 1, 'param': 604800}
        x = self.s.post(url, json=myobj)
        print(x.status_code)
        print(x.content)
    
    def get_balance(self):
        """
        Returns the current balance, assumes USD.
        """
        print("Made it here")
        url = self.POKERSTARS_WEBSITE + '/api/v1-preview/account'
        x = self.s.get(url)
        print(x.status_code)
        print(x.content)
        r = x.json()
        balance = "$" + str(r["totalBalanceInUsd"]/100)
        print("Balance")
        print(balance)



