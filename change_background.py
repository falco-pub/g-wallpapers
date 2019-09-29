#!/usr/bin/python


# Setup the Photo v1 API
# from https://github.com/ido-ran/google-photos-api-python-quickstart/blob/master/quickstart.py
from apiclient import discovery
from httplib2 import Http
from oauth2client import file, client, tools
import argparse, random, subprocess, shlex, urllib.request, os.path
import logging as log


def parse_arg_verbose_log():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v",
                        "--verbose",
                        help="verbose logging",
                        action="store_true")
    parser.add_argument("-c",
                        "--creds",
                        help="credentials file")
    args = parser.parse_args()

    if args.verbose:
        log.basicConfig(format="%(levelname)s %(relativeCreated)d " +
                        "%(filename)s(%(funcName)s):%(lineno)d " +
                        # "%(filename)s(%(funcName)s):%(lineno)d %(name)s: "+
                        "%(message)s", level=log.DEBUG)
        log.info("Verbose output.")
    else:
        log.basicConfig(format="%(levelname)s: %(message)s")
    log.getLogger('googleapiclient.discovery_cache').setLevel(log.ERROR)
    log.getLogger('googleapiclient.discovery').setLevel(log.WARNING)
    return args


class API():
    """Constructs a Resource for interacting with an API from
    https://developers.google.com/discovery/v1/reference
    based on document file load from
    https://www.googleapis.com/discovery/v1/apis/${name}/v1/rest
    You can use the 'service' method to acceed to that resource
    """
    def __init__(self, name, scope, storefile, credsfile):
        _store = file.Storage(storefile)
        _creds = _store.get()
        if not _creds or _creds.invalid:
            _flow = client.flow_from_clientsecrets(credsfile, scope)
            _creds = tools.run_flow(_flow, _store,
                                    flags=tools.argparser.parse_args([]))
        self.service = discovery.build(name, 'v1', http=_creds.authorize(Http()))


class Photoslibrary(API):
    """Constructs methods for interacting with Google Photos APIs
    https://www.googleapis.com/discovery/v1/apis/photoslibrary/v1/rest
    """
    def __init__(self, scope, storefile, credsfile):
        super().__init__('photoslibrary', scope, storefile, credsfile)

    def albums(self, *args, **kwargs):
        return self.service.albums(*args, **kwargs)

    def mediaItems(self, *args, **kwargs):
        return self.service.mediaItems(*args, **kwargs)

    def sharedAlbums(self, *args, **kwargs):
        return self.service.sharedAlbums(*args, **kwargs)

    def album_search(self, title, _tk=None):
        "return id of album which title is 'title'"

        _results = self.albums().list(
            pageSize=50, fields="nextPageToken,albums(id,title)",
            pageToken=_tk).execute()
        if 'albums' in _results:
            for _i in _results['albums']:
                if _i['title'] == title:
                    return _i['id']
        try:
            return self.album_search(title, _tk=_results['nextPageToken'])
        except KeyError:
            log.info("No album found")
            return None

    def list_media_album(self, albumId, _tk=None, _r=[]):
        "return a list of media items in album"
        _results = self.mediaItems().search(body={
            'albumId': albumId,
            'pageToken': _tk}).execute()
        if 'mediaItems' in _results:
            _r.extend(_results['mediaItems'])
        try:
            return self.list_media_album(albumId, _tk=_results['nextPageToken'], _r=_r)
        except KeyError:
            log.info("Found a list of %d media elements" % len(_r))
            return _r

    def list_album_search(self, title):
        "return a list of ID's of media in album 'title'"
        _id_album = self.album_search(title)
        if _id_album:
            log.info("Album id found: %s" % _id_album)
            return self.list_media_album(_id_album, _r=[])
        else:
            log.warning("No album called '%s' found" % title)
            raise LookupError("No album called '%s' found" % title)


def session_gphotos(scope='https://www.googleapis.com/auth/photoslibrary.readonly',
                    storefile='token.json',
                    credsfile='creds.json'):
    return Photoslibrary(scope, storefile, credsfile)


args = parse_arg_verbose_log()

if __name__ == "__main__" and not __doc__:

    # Sets the paths to the files containing the credentials
    credsfile = args.creds if args.creds else 'creds.json'
    storefile = os.path.join(os.path.dirname(credsfile), "token.json")
    log.info("credsfile = %s, storefile = %s" % (credsfile, storefile))

    # Sets an authenticated session to Google Api photoslibrary
    # using discovery: https://www.googleapis.com/discovery/v1/apis/photoslibrary/v1/rest
    s = session_gphotos(credsfile=credsfile, storefile=storefile)

    # Choses a random wallpaper and appends wanted resolution to URL
    l = s.list_album_search('wallpapers')
    url = random.choice(l)['baseUrl'] + "=w1920-h1080"
    log.info("photo URL: %s" % url)

    # Saves the wallpaper to /tmp/ and invokes gnome-settings through shell
    file_name, headers = urllib.request.urlretrieve(url, '/tmp/g-api.jpg')
    cl = 'gsettings set org.cinnamon.desktop.background picture-uri ' + \
        'file://' + file_name
    subprocess.Popen(shlex.split(cl))





