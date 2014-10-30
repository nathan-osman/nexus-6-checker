#!/usr/bin/env python

import argparse
import bs4
import json
import logging
import requests
import time


class Nexus6Checker:
    """
    Monitor the Nexus 6 product pages for changes and push notifications for changes.
    """

    STORE_BASE_URL = 'https://play.google.com/store/devices/details?id=%s'
    STORE_PRODUCT_IDS = {
        'Nexus 6 White 32GB': 'nexus_6_white_32gb',
        'Nexus 6 Blue 32GB': 'nexus_6_blue_32gb',
        'Nexus 6 White 64GB': 'nexus_6_white_64gb',
        'Nexus 6 Blue 64GB': 'nexus_6_blue_64gb',
    }
    PUSH_URL = 'https://api.pushbullet.com/v2/pushes'

    def __init__(self, args):
        """
        Initialize the checker.
        """
        self._args, self._inventory = args, {}
        self._logger = logging.getLogger('n6check')
        if self._args.debug:
            self._logger.setLevel(logging.DEBUG)

    def check(self):
        """
        Enter a loop that continously monitors the pages.
        """
        while True:
            self._logger.debug('Checking all products')
            for name, id in self.STORE_PRODUCT_IDS.items():
                self._logger.debug('Checking %s...', name)
                old = self._inventory.get(id, None)
                new = self._check_product_inventory(id).strip()
                if old is not None and old != new:
                    self._logger.info('Change detected in %s!', name)
                    self._push_message(
                        'Page Content Has Changed!',
                        'The inventory of the %s now states: "%s"' % (name, new),
                    )
                self._inventory[id] = new
                # Prevent too many simultaneous requests
                time.sleep(1)
            time.sleep(self._args.interval)

    def _check_product_inventory(self, id):
        """
        Retrieve the inventory text for the specified product.
        """
        req = requests.get(self.STORE_BASE_URL % id)
        soup = bs4.BeautifulSoup(req.content)
        inv = soup.find_all('div', class_='inventory-info', limit=1)
        return inv[0].get_text() if len(inv) else '[Inventory Removed]'

    def _push_message(self, title, body):
        """
        Push the specified message to the Pushbullet channel.
        """
        auth = requests.auth.HTTPBasicAuth(self._args.access_token, '')
        data = {
            'channel_tag': self._args.channel,
            'type': 'note',
            'title': title,
            'body': body,
        }
        headers = {'content-type': 'application/json'}
        req = requests.post(self.PUSH_URL, auth=auth, data=json.dumps(data), headers=headers)
        if req.status_code != 200:
            self._logger.error(req.json()[u'error'][u'message'])


if __name__ == '__main__':
    # Set up logging
    logging.basicConfig(format='[%(levelname)s] %(asctime)s %(name)s - %(message)s')
    logging.getLogger('requests').setLevel(logging.WARNING)

    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Monitors Nexus 6 product pages for inventory updates')
    parser.add_argument(
        'channel',
        metavar='CHANNEL',
        help='Pushbullet channel to push notifications to',
    )
    parser.add_argument(
        'access_token',
        metavar='ACCESS_TOKEN',
        help='Pushbullet access token for authentication',
    )
    parser.add_argument(
        '--interval',
        metavar='SECONDS',
        type=int,
        default=50,
        help='time between successive checks (in seconds)',
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='enable debug logs',
    )

    # Start checking...
    Nexus6Checker(parser.parse_args()).check()
