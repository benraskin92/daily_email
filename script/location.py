#!/usr/bin/env python

import forecastio
import json
import requests
import pprint
import smtplib
import re
import evernote
# import datetime
from datetime import timedelta
# from dateutil import tz
from datetime import datetime
import datetime
import dateutil
import sqlite3
from email.mime.text import MIMEText
from collections import OrderedDict
# from lxml import html
from random import randint, randrange, sample


def change_time(time):
    utc = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
    new_time = utc + timedelta(hours=-4)
    return new_time


def add_weather(api, lng, lat, file):
    forcast = forecastio.load_forecast(api, lat, lng)

    by_hourly = forcast.hourly()

    with open(file, 'a') as f:
        f.write("Weather for today:\n\n")

    with open(file, 'a') as f:

        for datapoint in by_hourly.data[:12]:
            try:
                datapoint.precipType
                PRECIPTYPE = datapoint.precipType
            except:
                PRECIPTYPE = ''

            ny_time = change_time(str(datapoint.time))

            if datapoint.precipIntensity == 0:
                precipitation = "no precipitation"
            elif datapoint.precipIntensity > 0.000 and datapoint.precipIntensity <= 0.0020:
                precipitation = "very light"
            elif datapoint.precipIntensity > 0.0020 and datapoint.precipIntensity <= 0.0170:
                precipitation = "light"
            elif datapoint.precipIntensity > 0.0170 and datapoint.precipIntensity <= 0.1000:
                precipitation = "moderate"
            elif datapoint.precipIntensity > 0.4:
                precipitation = "heavy"

            if PRECIPTYPE == '':
                f.write("{} > {} degrees > {} with {} ({}% chance).\n".format(ny_time, datapoint.temperature,
                                                                              datapoint.summary, precipitation,
                                                                              datapoint.precipProbability))
            else:
                f.write("{} > {} degrees > {} with {} {} ({}% chance).\n".format(ny_time, datapoint.temperature,
                                                                                 datapoint.summary, precipitation,
                                                                                 PRECIPTYPE,
                                                                                 datapoint.precipProbability * 100))
        f.write("\n")


def add_ny_times_news(file):
    link = requests.get("https://api.nytimes.com/svc/topstories/v2/home.json",
                        headers={"api-key": "f337d597cbd84ee4b28b8f9c91381299"})
    data = json.loads(link.text)

    times_list = []
    for i in data['results']:
        d = OrderedDict()
        d['title'] = i['title']
        d['abstract'] = i['abstract']
        d['url'] = i['url']
        times_list.append(d)

    my_randoms = sample(xrange(2, 12), 6)
    print my_randoms

    # print times_list

    with open(file, 'a') as f:
        f.write("NY Times articles:\n")
        for x in my_randoms:
            for item in times_list[x - 1:x]:
                f.write("\n")
                for k, v in item.items():
                    f.write('{}: {}'.format(k, v.encode('utf-8')))
                    f.write("\n")


def create_email_msg(FROM, to, SUBJECT, text):
    message = 'Subject: %s\n\n%s' % (SUBJECT, text)

    return message


def send_mail(FROM, to, email_body):
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.ehlo()
    server.starttls()
    server.login('benraskin92', 'nwdlnohawesdcemi')
    server.sendmail(FROM, to, email_body)
    server.quit()


def get_info(email):
    list = []
    conn = sqlite3.connect("/Users/BenjaminRaskin/Desktop/daily_email/email.sqlite")
    c = conn.cursor()
    for ind in email:
        dict = {}
        ny_times = (c.execute("""SELECT ny_times FROM email WHERE email_address = ?""", (ind,))).fetchall()
        weather = (c.execute("""SELECT weather FROM email WHERE email_address = ?""", (ind,))).fetchall()
        ny_times = [''.join(w) for w in ny_times]
        weather = [''.join(w) for w in weather]
        dict["email"] = ind
        dict["ny_times"] = ny_times[0]
        dict["weather"] = weather[0]
        list.append(dict)
    return list


my_file = '/Users/BenjaminRaskin/Desktop/daily_email/daily.txt'

FROM = "benraskin92@gmail.com"
# all_recipients = [] # must be a list

conn = sqlite3.connect("/Users/BenjaminRaskin/Desktop/daily_email/email.sqlite")
c = conn.cursor()

query = c.execute("""SELECT email_address FROM email""")
all_recipients = query.fetchall()
email_addresses = []

for email_tup in all_recipients:
    email_addresses.append(''.join(email_tup))

conn.commit()
conn.close()

d = datetime.date.today()
SUBJECT = "Daily summary for {}!".format(d)

peeps = get_info(email_addresses)

for i in peeps:
    with open(my_file, 'w') as f:
        f.write("Hello Ben:\n\n")

    to = i["email"]
    # print i["email"]
    if i["weather"] == "true":
        api_key = "928651a61968e82c41830db516b250d9"
        lat = 40.70942639999999
        lng = -74.0067062
        add_weather(api_key, lng, lat, my_file)

    if i["ny_times"] == "true":
        add_ny_times_news(my_file)

    with open(my_file, 'r') as f:
        TEXT = f.read()

    email_msg = create_email_msg(FROM, to, SUBJECT, TEXT)

    print email_msg

    send_mail(FROM, to, email_msg)



# for k in email_addresses:
#     with open(my_file, 'w') as f:
#         f.write("Hello Ben:\n\n")
#     to = k
#     api_key = "928651a61968e82c41830db516b250d9"
#     lat = 40.70942639999999
#     lng = -74.0067062
#
#     # add_weather(api_key, lng, lat, my_file)
#
#     # add_ny_times_news(my_file)
#
#     with open(my_file, 'r') as f:
#         TEXT = f.read()
#
#     email_msg = create_email_msg(FROM, to, SUBJECT, TEXT)

# print email_msg

# send_mail(FROM, to, email_msg)
