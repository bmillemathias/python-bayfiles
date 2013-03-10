#!/usr/bin/env python
# coding:utf-8
#
import requests
import hashlib

class BasicException(requests.ConnectionError):
    pass

class UploadException(BasicException):
    pass

class DeleteException(BasicException):
    pass

class File(object):
    """
    File instance represent
    """

    BASE_URL = "http://api.bayfiles.com/v1"

    def __init__(self, filepath, session=''):
        self.metadata = {}
        self.filepath = filepath
        self.session = session

        # ask for an upload URL
        self.__register_url()

    def __register_url(self):
        """
        This function will request an upload url to post the file you need to store 
        and a progress url that can be polled to know the progress of the upload
        """

        url = self.BASE_URL + '/file/uploadUrl'
        #if self.session:
        #    url += '?session={0}'.format(self.session)
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
            files = {'file': file_fd }
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
                raise UploadException("The file was corrupted during the upload")

    def delete(self):
        """Delete the download url and the file stored in bayfiles."""
        try:
            r = requests.get(
                self.BASE_URL + '/file/delete/{0}/{1}'.format(
                    self.metadata['fileId'],
                    self.metadata['deleteToken']))

            if not r.ok:
                r.raise_for_status()

            json = r.json()
            if json['error'] == u'':
                return
        except:
            raise DeleteException(json['error'])

    def info(self):
        """Return public information about the file instance."""
        try:
            r = requests.get(
                    self.BASE_URL + '/file/info/{0}/{1}'.format(
                        self.metadata['fileId'],
                        self.metadata['infoToken']))

            if not r.ok:
                r.raise_for_status()
            return r.json()

        except AttributeError:
            print "Need to use upload() before info()"

class Account(object):
    pass
