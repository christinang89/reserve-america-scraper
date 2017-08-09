Scrape Reserve America
======================

Scrape Reserve America for your favorite campsite

Usage
-----

Set the `desired_trips` variable in scraper.py.

Run the setup script, and call the scraper.py script!

```sh
> pip install -r requirements.txt
> ./scraper.py
```


Then the scraper will search the given campsite for the date with the length of stay.

cron
======================
You can also set up the script to run under cron, and notify you on macOS using one of the provided cron scripts ( [`cron-desktop-notification.sh`](./cron-desktop-notification.sh) or [`cron-sms-notification.sh`](./cron-sms-notification.sh) ).

To run with cron, setup a crontab by calling `crontab -e`

SMS notifications
-----
An example of a crontab for the `cron-desktop-notifications.sh` is:

```cron
SHELL=/bin/bash

*/5 * * * * path/to/reserve-america-scraper/cron-sms-notifications.sh 2>&1 > /dev/null
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

Desktop notifications
-----
An example of a crontab for the the `cron-desktop-notifications.sh` is:

```cron
SHELL=/bin/bash

*/15 * * * * RESERVE_AMERICA_VENV_BASE='path/to/your/virtualenv' path/to/reserve-america-scraper/cron-sms-notifications.sh 2>&1 > /dev/null
```

Note that the `cron-desktop-notification.sh` wants you to run it inside of a python virtual environment by running with the env var `RESERVE_AMERICA_VENV_BASE` set to the path of your virtual environment.

Also, make sure that you have `terminal-notifier` installed. That's easy to do with Homebrew:

```sh
> brew install terminal-notifier
```

License
-------

[MIT](./LICENSE)
