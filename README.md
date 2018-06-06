Scrape Reserve America
======================

Scrape Reserve America for your favorite campsite

Usage
-----

Set the campsites wanted in campsites.csv in the following format: Name of Campsite, URL of Campsite
Set the trips desired in  trips.csv in the following format: Date, Length of Stay, Name of Campsite

Run the setup script, and call the scraper.py script!

```sh
> pip install -r requirements.txt
> ./scraper.py
```

Then the scraper will search the given campsite for the date with the length of stay.

cron
======================
You can also set up the script to run under cron.

To run with cron, setup a crontab by calling `crontab -e`

SMS notifications
-----
An example of a crontab is:

Cron job running every 15 min (output to logfile):
```cron
*/15 * * * * python path/to/reserve-america-scraper/scraper.py >> path/to/logfile 2>&1
```

Cron job running every min (discard output):
```cron
* * * * * python path/to/reserve-america-scraper/scraper.py 2>&1 > /dev/null
```

Note that you must export the following env vars for SMS integration
```sh
# Your Account SID from twilio.com/console
export TWILIO_ACCOUNT_SID="ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
# Your Auth Token from twilio.com/console
export TWILIO_AUTH_TOKEN="your_auth_token"
# Your twilio phone number
export TWILIO_FROM_NUMBER="your_twilio_phone_number"
# Your personal phone number
export TWILIO_TO_NUMBER="your_personal_phone_number"
```

Multiple phone numbers are supported as a colon separated string.
```sh
export TWILIO_TO_NUMBER="your_personal_phone_number:your_friends_personal_phone_number"
```

License
-------

[MIT](./LICENSE)
