from setuptools import setup

with open('README') as f:
    long_description = f.read()

setup(name='bayfiles',
        version = '0.0.3',
        description = 'A library to upload files to bayfiles.com',
        long_description = long_description,
        py_modules = ['bayfiles'],
        author = 'Baptiste Mille-Mathias',
        author_email = 'baptiste.millemathias@gmail.com',
        url = 'https://github.com/bmillemathias/python-bayfiles',
        license = 'LGPL',
        install_requires = ['requests >= 1.0.0'],
        keywords = ('filesharing', 'upload', 'storage', 'bayfiles.com', 'http'),
        classifiers = ['Development Status :: 2 - Pre-Alpha',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: GNU Lesser General Public License v2 (LGPLv2)',
            'Operating System :: POSIX',
            'Programming Language :: Python :: 2.7',
            'Topic :: Communications :: File Sharing',
            'Topic :: Internet :: WWW/HTTP',
            'Topic :: Software Development :: Libraries :: Python Modules'])
