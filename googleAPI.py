from googleapiclient import discovery
from httplib2 import Http
from oauth2client import file, client, tools
import argparse
import logging


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
            logging.info("No album found")
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
            logging.info("Found a list of %d media elements" % len(_r))
            return _r

    def list_album_search(self, title):
        "return a list of ID's of media in album 'title'"
        _id_album = self.album_search(title)
        if _id_album:
            logging.info("Album id found: %s" % _id_album)
            return self.list_media_album(_id_album, _r=[])
        else:
            logging.warning("No album called '%s' found" % title)
            raise LookupError("No album called '%s' found" % title)


