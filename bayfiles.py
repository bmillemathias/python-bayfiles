# coding:utf-8
#
import requests
import sys
import os

BASE_URL = "http://api.bayfiles.com/v1"


class FileBasicException(requests.ConnectionError):
    """Exception """
    pass


class FileUploadException(FileBasicException):
    """Exception triggered in upload() method."""
    pass


class FileDeleteException(FileBasicException):
    """Exception triggered in delete() method."""
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

        if not os.path.isfile(self.filepath):
            raise Exception('%s is not a file' % (self.filepath))

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
        request = requests.get(url)

        if not request.ok:
            request.raise_for_status()

        self.metadata = request.json()

        if self.metadata['error'] != u'':
            raise FileUploadException(self.metadata['error'])

    def __get_sha1hash(self):
        """Return the sha1 hash on the entire content of the file passed."""

        # Don't know if it's "right" to import a module in a function
        import hashlib

        sha1_obj = hashlib.sha1()
        with open(self.filepath, 'rb') as file_r:
            while True:
                buffr = file_r.read(0x100000)
                if not buffr:
                    break
                sha1_obj.update(buffr)

        sha1hash = sha1_obj.hexdigest()
        return sha1hash

    def upload(self, validate=True):
        """Upload the file to bayfiles server.

        Keywords arguments:
        validate -- a boolean, if set to True, it will ensure there was no
        corruption during the transfert by comparing the sha1 hash of the local
        file and the one computed by bayfile.

        Should an error arise an exception FileUploadException is raised.

        """
        with open(self.filepath, 'rb') as file_fd:
            files = {'file': file_fd}
            request = requests.post(self.metadata['uploadUrl'], files=files)

        if not request.ok:
            request.raise_for_status()

        json = request.json()
        if json['error'] == '':
            self.metadata.update(json)
        else:
            raise FileUploadException(json['error'])

        # If we ask the sha1 hash validation
        if validate:
            sha1hash = self.__get_sha1hash()
            if not self.metadata['sha1'] == sha1hash:
                raise FileUploadException(
                    "The file was corrupted during the upload")

    def delete(self):
        """Delete the download url and the file stored in bayfiles."""
        try:
            url = BASE_URL +\
                '/file/delete/{0}/{1}'.format(self.metadata['fileId'],
                                            self.metadata['deleteToken'])

            request = requests.get(url)

            if not request.ok:
                request.raise_for_status()

            json = request.json()
            if json['error'] == u'':
                return
            else:
                raise FileDeleteException(json['error'])
        except:
            raise FileDeleteException(sys.exc_info()[0])

    def info(self):
        """Return public information about the file instance."""
        try:
            url = BASE_URL +\
                '/file/info/{0}/{1}'.format(self.metadata['fileId'],
                                            self.metadata['infoToken'])

            request = requests.get(url)

            if not request.ok:
                request.raise_for_status()
            return request.json()

        except KeyError:
            print "Need to call upload() before info()"


class Account(object):
    """
    Represent an account on the site bayfiles.com.

    Keywords arguments:
    username -- a string which is the username of the account
    password -- a string which is the password of the account
    """
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.__login()

    def __login(self):
        """Authenticate and receive a session identifier."""
        url = BASE_URL + '/account/login/{0}/{1}'.format(self.username,
                                                         self.password)
        try:
            request = requests.get(url)

            if not request.ok:
                request.raise_for_status()

            json = request.json()

            if json['error'] == u'':
                self.session = json['session']
            else:
                raise Exception(json['error'])
        except:
            raise Exception(sys.exc_info()[0])

    def logout(self):
        """Delete the session related to the account on bayfiles.com."""
        url = BASE_URL + '/account/logout'
        url += '?session={0}'.format(self.session)

        try:
            request = requests.get(url)

            if not request.ok:
                request.raise_for_status()

            json = request.json()
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
            request = requests.get(url)

            if not request.ok:
                request.raise_for_status()

            json = request.json()

            if json['error'] == u'':
                return json
            else:
                raise Exception(json['error'])
        except:
            raise Exception(sys.exc_info()[0])

    def edit(self, key, value):
        """Replace value from a key with a new value.

        Keywords arguments:
        key -- a string, the key to update the value of
        value -- a string, the new value for the key
        """
        url = BASE_URL + '/account/edit/{0}/{1}'.format(key, value)
        url += '?session={0}'.format(self.session)
        try:
            request = requests.get(url)

            if not request.ok:
                request.raise_for_status()

            json = request.json()

            if json['error'] == u'':
                return json
            else:
                raise Exception(json['error'])
        except:
            raise Exception(sys.exc_info()[0])

    def files(self):
        """Return a dictionnary with the files belonging to the account."""
        url = BASE_URL + '/account/files'
        url += '?session={0}'.format(self.session)

        try:
            request = requests.get(url)

            if not request.ok:
                request.raise_for_status()

            json = request.json()

            if json['error'] == u'':
                return json
            else:
                raise Exception(json['error'])
        except:
            raise Exception(sys.exc_info()[0])
