#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
SLEEP_SECONDS = int(os.environ.get("SLEEP_SECONDS", "20"))

if os.path.isfile(SEEN_DB):
    seen = json.load(open(SEEN_DB))
else:
    seen = {}

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
twitter = tweepy.API(auth)


def main():
    feed = ElementTree.parse(urllib.urlopen(FEED_URL)).getroot()
    for item in feed.findall('.//item'):
        if tweet(item):
            time.sleep(SLEEP_SECONDS)


def tweet(item):
    link = item.find('link').text
    if link in seen:
        return False

    title = item.find('title').text
    desc = item.find('description').text
    encl = item.find('enclosure')
    if encl is not None: 
        img = encl.attrib['url']
    else:
        img = None

    soup = BeautifulSoup(desc, 'html.parser')
    desc = first(soup, 'div[id="dublin-core-description"] div')
    creator = first(soup, 'div[id="dublin-core-creator"] div')

    status = get_status_text(title, desc, creator, link, img)
    png = get_image(img)

    if png:
        twitter.update_with_media(png, status)
        os.remove(png)
    else:
        twitter.update_status(status=status)

    seen[link] = True
    json.dump(seen, open(SEEN_DB, "w"), indent=2)

    return True


def get_status_text(title, desc, creator, link, img):
    # urls for web pages and embedded media take up 23 chars so adjust
    # the status message to fit within the allotted 140 characters
    limit = 140 - 23
    if img:
        limit -= 23

    # not all Omeka items have titles
    if title != "[Untitled]":
        msg = title
    else:
        msg = desc

    # see if we can add the creator to the message
    if len(msg) > limit or not creator:
        msg = unicode(msg[0:limit-1]) + u'…'
    elif len(msg + ' by ' + creator) < limit:
        msg = msg + ' by ' + creator

    return "%s %s" % (msg, link)


def get_image(url):
    if not url:
        return None

    fh, path = tempfile.mkstemp()
    urllib.urlretrieve(url, path)

    # twitter doesn't like all jpegs so convert to png
    # omeka requires a login for some images, so catch those

    try:
        i = Image.open(path)
    except:
        return None

    png = path + '.png'
    i.save(png, 'png')

    # clean up original
    os.close(fh)
    os.remove(path)

    return png

def first(soup, path):
    e = soup.select(path)
    if len(e) > 0:
        return e[0].text
    return None

if __name__ == "__main__":
    main()
