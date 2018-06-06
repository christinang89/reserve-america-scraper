#!/usr/bin/env python

from __future__ import print_function
import os
import sys
import datetime
import csv

# Read list of campsites and their URLs into Dictionary
dirname = os.path.dirname(os.path.abspath(__file__))
campsites_file = os.path.join(dirname, 'campsites.csv')

with open(campsites_file) as csvfile:
        reader = csv.reader(csvfile)
        campsites = dict((rows[0],rows[1]) for rows in reader)

try:
    import mechanize
    from bs4 import BeautifulSoup
    from twilio.rest import Client
except ImportError:
    print('Unable to import necessary packages!')
    sys.exit(-1)

# Try to import Twilio
try:
    from twilio.rest import Client as TwilioClient
except ImportError:
    TwilioClient = None

# Optional Twilio configuration
twilio_account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
twilio_auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
twilio_from_number = os.environ.get('TWILIO_FROM_NUMBER')
twilio_to_numbers = os.environ.get('TWILIO_TO_NUMBER')
has_twilio = all([
    TwilioClient,
    twilio_account_sid,
    twilio_auth_token,
    twilio_from_number,
    twilio_to_numbers,
])

# Multiple phone numbers are supported if they are colon separated
if has_twilio:
    twilio_to_numbers = twilio_to_numbers.split(':')

USER_AGENT = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) '
              'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.33 '
              'Safari/537.36')

def send_sms(msg):
    if not has_twilio:
        return

    # TODO: only send new SMSes
    client = Client(twilio_account_sid, twilio_auth_token)
    for twilio_to_number in twilio_to_numbers:
        message = client.messages.create(
            to=twilio_to_number,
            from_=twilio_from_number,
            body=msg)

def send_results(result_date, hits, campsite, url):
    message = "Found {} sites on {} at {}: {}".format(len(hits), result_date, campsite, url)
    if has_twilio:
        print("Sent sms at " + datetime.datetime.now().strftime("%a, %d %B %Y %H:%M:%S"))
        send_sms(message)
    else:
        print(message)

def run(date, length_of_stay, campsite, url):
    hits = []

    # Create browser
    br = mechanize.Browser()

    # Browser options
    br.set_handle_equiv(True)
    br.set_handle_redirect(True)
    br.set_handle_referer(True)
    br.set_handle_robots(False)
    br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)
    br.addheaders = [('User-agent', USER_AGENT)]
    br.open(url)

    # Fill out form
    br.select_form(nr=0)
    br.form.set_all_readonly(False)  # allow changing the .value of all controls
    br.form["campingDate"] = date
    br.form["lengthOfStay"] = length_of_stay
    response = br.submit()

    # Scrape result
    soup = BeautifulSoup(response, "html.parser")
    table = soup.findAll("table", {"id": "shoppingitems"})

    if table:
        rows = table[0].findAll("tr", {"class": "br"})

        for row in rows:
            cells = row.findAll("td")
            l = len(cells)
            label = cells[0].findAll("div", {"class": "siteListLabel"})[0].text
            is_ada = bool(cells[3].findAll("img", {"title": "Accessible"}))
            is_group = bool('GROUP' in cells[2].text)
            status = cells[l - 1].text
            if not is_group and not is_ada and status.startswith('available'):
                hits.append(label)

    if hits:
        send_results(date, hits, campsite, response.geturl())
    else:
        print(datetime.datetime.now().strftime("%a, %d %B %Y %H:%M:%S"))
        print("Nothing found for " + length_of_stay + " nights at " + campsite + " on " + date)


if __name__ == '__main__':

    # Read trips from CSV file
    
    trips_file = os.path.join(dirname, 'trips.csv')
    with open(trips_file, 'rb') as csvfile:
        trips = csv.reader(csvfile)

        for trip in trips:

            # Retrieve Date, Length of Stay, Campsite, Campsite URL
            date = trip[0]
            length_of_stay = trip[1]
            campsite = trip[2]
            campsite_url = campsites[campsite]
            
            # Run results
            run(date,length_of_stay, campsite, campsite_url)
