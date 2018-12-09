#!/usr/bin/python


# Setup the Photo v1 API
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

class Photos():
    def __init__(self, scope, storefile, credsfile):
        _store = file.Storage(storefile)
        _creds = _store.get()
        if not _creds or _creds.invalid:
            _flow = client.flow_from_clientsecrets(credsfile, scope)
            _creds = tools.run_flow(_flow, _store)
        self.service = build('photoslibrary', 'v1', http=_creds.authorize(Http()))

    def albums(self, *args, **kwargs):
        return self.service.albums(*args, **kwargs)

    def album_search(self, title):
        "return id of album which title is 'title'"
        tk = None;
        while True:
            album_id=None
            results = self.albums().list(
                pageSize=50, fields="nextPageToken,albums(id,title)",
                pageToken=tk).execute()
            try:
                tk = results['nextPageToken']
            except KeyError:
                tk = None
            try:
                items = results['albums']
            except keyError:
                return None
            for item in items:
                if item['title']==title:
                    return(item['id'])
            if not tk:
                return None


if __name__ == "__main__" and not __doc__:
    p = Photos(scope='https://www.googleapis.com/auth/photoslibrary.readonly',
               storefile='token.json',
               credsfile='creds.json'
               )
    print(p.album_search('wallpapers'))
