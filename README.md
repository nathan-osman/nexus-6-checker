## Nexus 6 Checker

This little command-line script monitors the Google Play Store product pages for the four Nexus 6 models. When the inventory of one or more of them changes, a Pushbullet notification is pushed to the specified channel.

### Requirements

This script requires:

* [Python 2.7](https://www.python.org/)
* [Requests](https://pypi.python.org/pypi/requests)
* [BeautifulSoup 4](https://pypi.python.org/pypi/beautifulsoup4)

Assuming you have `pip` installed, you can simply run the following command to install the dependencies:

    pip install requests beautifulsoup4

### Usage

Usage is relatively straightforward:

    python checker.py [--interval SECONDS] [--debug] CHANNEL ACCESS_TOKEN

Use the `--help` switch to find out more about each parameter.
