#!/usr/bin/env python

"""
Tweet items found in an Omeka feed that haven't been tweeted before.
"""

import os
import json
import time
import urllib
import tweepy
import tempfile

from PIL import Image
from bs4 import BeautifulSoup
from xml.etree import ElementTree

CONSUMER_KEY = os.environ.get("CONSUMER_KEY")
CONSUMER_SECRET = os.environ.get("CONSUMER_SECRET")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
ACCESS_SECRET = os.environ.get("ACCESS_SECRET")
SEEN_DB = os.environ.get("SEEN_DB", "omeka-tweet.json")
FEED_URL = os.environ.get("FEED_URL")

if os.path.isfile(SEEN_DB):
    seen = json.load(open(SEEN_DB))
else:
    seen = {}

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
twitter = tweepy.API(auth)

feed = ElementTree.parse(urllib.urlopen(FEED_URL)).getroot()

for item in feed.findall('.//item'):
    title = item.find('title').text
    link = item.find('link').text
    desc = item.find('description').text
    encl = item.find('enclosure')
    if encl is not None: 
        img = encl.attrib['url']
    else:
        img = None

    soup = BeautifulSoup(desc)
    desc = soup.select('div[id="dublin-core-description"] div')[0].text
    creator = soup.select('div[id="dublin-core-creator"] div')[0].text

    if link not in seen:
        if title != "[Untitled]":
            status = "%s by %s %s" % (title, creator, link)
        else:
            status = "%s by %s %s" % (desc, creator, link)

        if img:
            fh, path = tempfile.mkstemp()
            urllib.urlretrieve(img, path)

            # twitter doesn't like all jpegs so convert to png
            i = Image.open(path)
            png = path + '.png'
            i.save(png, 'png')
            twitter.update_with_media(png, status)
            os.remove(path)
            os.remove(png)
        else:
            twitter.update_status(status=status)

        seen[link] = True
        json.dump(seen, open(SEEN_DB, "w"), indent=2)

        time.sleep(20)
