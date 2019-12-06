#!/usr/bin/python


# Setup the Photo v1 API
# from https://github.com/ido-ran/google-photos-api-python-quickstart/blob/master/quickstart.py
import argparse
import logging
import os.path
import random
import shlex
import subprocess
import urllib.request
import googleAPI


def parse_arg_verbose_log():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v",
                        "--verbose",
                        help="verbose logging",
                        action="store_true")
    parser.add_argument("-c",
                        "--creds",
                        help="credentials file")
    _args = parser.parse_args()

    if _args.verbose:
        logging.basicConfig(format="%(levelname)s %(relativeCreated)d " +
                                   "%(filename)s(%(funcName)s):%(lineno)d " +
                                   # "%(filename)s(%(funcName)s):%(lineno)d %(name)s: "+
                                   "%(message)s", level=logging.DEBUG)
        logging.info("Verbose output.")
    else:
        logging.basicConfig(format="%(levelname)s: %(message)s")
    logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)
    logging.getLogger('googleapiclient.discovery').setLevel(logging.WARNING)
    return _args


args = parse_arg_verbose_log()
# Sets the paths to the files containing the credentials
credsfile = args.creds if args.creds else 'creds.json'
storefile = os.path.join(os.path.dirname(credsfile), "token.json")
logging.info("credsfile = %s, storefile = %s" % (credsfile, storefile))
scope = 'https://www.googleapis.com/auth/photoslibrary.readonly'

if __name__ == "__main__" and not __doc__:
    # Sets an authenticated session to Google Api photoslibrary
    # using discovery: https://www.googleapis.com/discovery/v1/apis/photoslibrary/v1/rest
    s = googleAPI.Photoslibrary(
        scope=scope,
        storefile=storefile,
        credsfile=credsfile)

    # Chooses a random wallpaper and appends wanted resolution to URL
    albums_list = s.list_album_search('wallpapers')
    url = random.choice(albums_list)['baseUrl'] + "=w1920-h1080"
    logging.info("photo URL: %s" % url)

    # Saves the wallpaper to /tmp/ and invokes gnome-settings through shell
    file_name, headers = urllib.request.urlretrieve(url, '/tmp/g-api.jpg')
    cl = 'gsettings set org.cinnamon.desktop.background picture-uri ' + \
         'file://' + file_name
    subprocess.Popen(shlex.split(cl))
