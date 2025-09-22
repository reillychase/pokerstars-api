import stealth_requests as requests
import poplib
import email
from email.parser import BytesParser
import re
from email import policy
import time

# Settings
POP3_SERVER = 'pop.gmail.com'
POP3_PORT = 995
EMAIL_ADDRESS = ''  # Replace with your email
EMAIL_PASSWORD = ''  # Replace with your app-specific password
POKERSTARS_USERNAME = ''
POKERSTARS_PASSWORD = ''
POKERSTARS_WEBSITE = 'https://www.pokerstarsmi.com'

def connect_to_pop3():
    # Connect to Gmail POP3 server with SSL
    try:
        server = poplib.POP3_SSL(POP3_SERVER, POP3_PORT)
        server.user(EMAIL_ADDRESS)
        server.pass_(EMAIL_PASSWORD)
        return server
    except Exception as e:
        print(f"Error connecting to POP3 server: {str(e)}")
        raise

def fetch_and_search_pin_email(server, max_emails=100):
    # Get the number of emails
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
                
                if (msg['from'] and 'no_reply2@pokerstarsmi.com' in msg['from'].lower() and 
                    msg['subject'] and 'one time pin' in msg['subject'].lower()):
                    
                    # Handle multipart email
                    pin = None
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
        
    except Exception as e:
        print(f"Error listing/fetching emails: {str(e)}")
        return None

def main():
    try:

        s = requests.StealthSession()

        x = s.get(POKERSTARS_WEBSITE)
        print(x.status_code)


        # Login to get PIN email sent
        url = 'https://www.pokerstarsmi.com/api/v1-preview/auth/session'
        myobj = {'installId': '102133820445328422', 'userId': POKERSTARS_USERNAME, 'password': POKERSTARS_PASSWORD}
        x = s.post(url, json=myobj)
        print(x.status_code)
        print(x.content)
        print(x.cookies)

        # Sleep for 10 seconds to wait for PIN email to arrive
        time.sleep(10)

        # Connect to the POP3 server
        server = connect_to_pop3()
        
        # Fetch and search for the PIN email
        pin = fetch_and_search_pin_email(server)
        if pin:
            print(f"\n✅ Extracted PIN: {pin}")
        else:
            print("\n❌ No matching PIN email found via POP3.")
            print("\n💡 Quick Fix: Ensure the email has the 'Inbox' label in Gmail web interface.")
            print("   Go to gmail.com > Search for the email > Labels > Check 'Inbox'.")
        
        # Close the connection
        server.quit()

        # Try to Login again now with the pin
        url = 'https://www.pokerstarsmi.com/api/v1-preview/auth/session'
        myobj = {'installId': '102133820445328422', 'userId': POKERSTARS_USERNAME, 'password': POKERSTARS_PASSWORD, 'pin': pin,'errorCode': 'TEMP_PIN_REQUIRED'}
        x = s.post(url, json=myobj)
        print(x.status_code)
        print(x.content)
        print(x.cookies)

        # Export 7 days of hand history
        url = 'https://www.pokerstarsmi.com/api/v1-preview/account/history/client-history'
        myobj = {'locale': 0, 'requestType': 1, 'param': 604800}
        x = s.post(url, json=myobj)
        print(x.status_code)
        print(x.content)

        # Logout
        url = 'https://www.pokerstarsmi.com/api/v1-preview/auth/session'
        x = s.delete(url)
        print(x.status_code)
        print(x.content)

    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
