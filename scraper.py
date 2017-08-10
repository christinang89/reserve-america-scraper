#!/usr/bin/env python

from __future__ import print_function
import os
import sys

campsite_urls = {
    # outer Yosemite
    'HODGDON_MEADOW':'https://www.reserveamerica.com/camping/hodgdon-meadow/r/campgroundDetails.do?contractCode=NRSO&parkId=70929',
    'WAWONA':'https://www.reserveamerica.com/camping/wawona/r/campgroundDetails.do?contractCode=NRSO&parkId=70924',
    'CRANE_FLAT':'https://www.reserveamerica.com/camping/crane-flat/r/campgroundDetails.do?contractCode=NRSO&parkId=70930',
    'TUOLUMNE_MEADOWS':'https://www.reserveamerica.com/camping/tuolumne-meadows/r/campgroundDetails.do?contractCode=NRSO&parkId=70926',
    # inner Yosemite
    'UPPER_PINES':'https://www.reserveamerica.com/camping/upper-pines/r/campgroundDetails.do?contractCode=NRSO&parkId=70925',
    'LOWER_PINES':'https://www.reserveamerica.com/camping/lower-pines/r/campgroundDetails.do?contractCode=NRSO&parkId=70928',
    'NORTH_PINES':'https://www.reserveamerica.com/camping/north-pines/r/campgroundDetails.do?contractCode=NRSO&parkId=70927',
    # Point Reyes
    'POINT_REYES':'https://www.reserveamerica.com/camping/point-reyes-national-seashore-campground/r/campgroundDetails.do?contractCode=NRSO&parkId=72393',
    # Sequioa
    'POTWISHA':'https://www.reserveamerica.com/camping/potwisha-campground/r/campgroundDetails.do?contractCode=NRSO&parkId=72461',
    'TUOLUMNE':'https://www.reserveamerica.com/camping/tuolumne-meadows/r/campgroundDetails.do?contractCode=NRSO&parkId=70926',
    # Feel free to add more links here
}

# Update this with the trips you want to take
# Supported format
# Date : Length of stay : Campsite Campsite
desired_trips = ['08/26/17 : 2 : HODGDON_MEADOW CRANE_FLAT TUOLUMNE_MEADOWS',
                 '09/01/17 : 2 : HODGDON_MEADOW',
                 '09/08/17 : 2 : HODGDON_MEADOW',
                 '09/22/17 : 2 : HODGDON_MEADOW']
# TODO: extract desired_trips to a parsable env variable

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

def send_sms(message):
    if not has_twilio:
        return

    msg = "{}. {}".format(message, url)

    # TODO: only send a new SMSes
    client = Client(twilio_account_sid, twilio_auth_token)
    for twilio_to_number in twilio_to_numbers:
        message = client.messages.create(
            to=twilio_to_number,
            from_=twilio_from_number,
            body=msg)

def send_results(result_date, hits):
    message = "On {}, found available sites: {}".format(
        result_date, ', '.join(hits))
    if has_twilio:
        send_sms(message)
    else:
        print(message)

def run(date, length_of_stay, url):
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
        send_results(date, hits)


if __name__ == '__main__':
    for desired_trip in desired_trips:
        date = desired_trip.split(' : ')[0]
        length_of_stay = desired_trip.split(' : ')[1]
        campsites = desired_trip.split(' : ')[2]
        campsites = campsites.split(' ')

        for campsite in campsites:
            campsite_url = campsite_urls[campsite]
            run(date, length_of_stay, campsite_url)
