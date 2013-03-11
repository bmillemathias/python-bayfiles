#!/usr/bin/env python
# coding:utf-8
#
import requests
import sys

BASE_URL = "http://api.bayfiles.com/v1"

class BasicException(requests.ConnectionError):
    pass


class UploadException(BasicException):
    pass


class DeleteException(BasicException):
    pass


class File(object):
    """
    File instance represents the file to send to bayfiles.com.

    Keywords arguments:
    filepath -- the file to upload to bayfiles.com
    account -- a bayfiles.Account instance
    """

    def __init__(self, filepath, account=None):
        self.metadata = {}
        self.filepath = filepath
        self.account = account

        # ask for an upload URL
        self.__register_url()

    def __register_url(self):
        """
        This function will request an upload url to post the file you need to
        store and a progress url that can be polled to know the progress of the
        upload.
        """

        url = BASE_URL + '/file/uploadUrl'
        if self.account and hasattr(self.account, "session"):
            url += '?session={0}'.format(self.account.session)
        r = requests.get(url)

        if not r.ok:
            r.raise_for_status()

        self.metadata = r.json()

        if self.metadata['error'] != u'':
            raise UploadException(self.metadata['error'])

    def __get_sha1hash(self):
        """Return the sha1 hash on the entire content of the file passed."""

        # Don't know if it's "right" to import a module in a function
        import hashlib

        SHA1 = hashlib.sha1()
        with open(self.filepath, 'rb') as file:
            while True:
                buffr = file.read(0x100000)
                if not buffr:
                    break
                SHA1.update(buffr)

        sha1hash = SHA1.hexdigest()
        return sha1hash

    def upload(self, validate=True):
        """Upload the file to bayfiles server.

        Keywords arguments:
        validate -- a boolean, if set to True, it will ensure there was no
        corruption during the transfert by comparing the sha1 hash of the local
        file and the one computed by bayfile.

        """
        with open(self.filepath, 'rb') as file_fd:
            files = {'file': file_fd}
            r = requests.post(self.metadata['uploadUrl'], files=files)

        if not r.ok:
            r.raise_for_status()

        json = r.json()
        if json['error'] == '':
            self.metadata.update(json)
        else:
            raise UploadException(json['error'])

        # If we ask the sha1 hash validation
        if validate:
            sha1hash = self.__get_sha1hash()
            if not self.metadata['sha1'] == sha1hash:
                raise UploadException(
                    "The file was corrupted during the upload")

    def delete(self):
        """Delete the download url and the file stored in bayfiles."""
        url = BASE_URL + '/file/delete/{0}/{1}'.format(self.metadata['fileId'],
            self.metadata['deleteToken'])
        try:
            r = requests.get(url)

            if not r.ok:
                r.raise_for_status()

            json = r.json()
            if json['error'] == u'':
                return
            else:
                raise DeleteException(json['error'])
        except:
            raise DeleteException(sys.exc_info()[0])

    def info(self):
        """Return public information about the file instance."""
        url = BASE_URL + '/file/info/{0}/{1}'.format(self.metadata['fileId'],
            self.metadata['infoToken'])
        try:
            r = requests.get(url)

            if not r.ok:
                r.raise_for_status()
            return r.json()

        except AttributeError:
            print "Need to use upload() before info()"


class Account(object):

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.__login()

    def __login(self):
        """Authenticate and receive a session identifier."""
        url = BASE_URL + '/account/login/{0}/{1}'.format(self.username,
                                                         self.password)
        try:
            r = requests.get(url)

            if not r.ok:
                r.raise_for_status()

            json = r.json()

            if json['error'] == u'':
                self.session = json['session']
            else:
                raise Exception(json['error'])
        except:
            raise Exception(sys.exc_info()[0])

    def logout(self):
        """Delete the session related to the account."""
        url = BASE_URL + '/account/logout'
        url += '?session={0}'.format(self.session)

        try:
            r = requests.get(url)

            if not r.ok:
                r.raise_for_status()

            json = r.json()
            if json['error'] == u'':
                self.session = None
                return
            else:
                raise Exception(json['error'])
        except:
            raise Exception(sys.exc_info()[0])

    def info(self):
        """Return a dictionnary with information about the account."""
        url = BASE_URL + '/account/info'
        url += '?session={0}'.format(self.session)

        try:
            r = requests.get(url)

            if not r.ok:
                r.raise_for_status()

            json = r.json()

            if json['error'] == u'':
                return json
            else:
                raise Exception(json['error'])
        except:
            raise Exception(sys.exc_info()[0])

    def edit(self, key, value):
        """Not yet implemented"""
        raise NotImplementedError

    def files(self):
        """Return a dictionnary with the files belonging to the account."""
        url = BASE_URL + '/account/files'
        url += '?session={0}'.format(self.session)

        try:
            r = requests.get(url)

            if not r.ok:
                r.raise_for_status()

            json = r.json()

            if json['error'] == u'':
                return json
            else:
                raise Exception(json['error'])
        except:
            raise Exception(sys.exc_info()[0])
