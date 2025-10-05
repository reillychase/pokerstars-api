# PokerStars API

This is only tested with pokerstarsmi.com but might work for other PokerStars variants

I recommend using a throwaway email address so you can give this script access to your email via POP3 to get the PIN for login

I wrote this script so I can automatically export hand history on a cron job

Even though the API call for export_hands is for 7 days of hand history, in my experience PokerStars only sends 200 hands max, so I run it on a cron every 15 minutes to make sure I always get all hands while playing on iOS

I am working on adding more features, I would like to, for example, sum the withdrawals and deposits but the Authorization header for cashier.pokerstarsmi.com is complicated to figure out

DM me on X to collab
