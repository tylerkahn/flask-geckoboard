from setuptools import setup, Command
import os

import flask_geckoboard


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

def build_long_description():
    return "\n\n".join([
        flask_geckoboard.__doc__,  #@UndefinedVariable
        read('CHANGELOG.rst'),
    ])


setup(
    name = 'Flask-Geckoboard',
    version = flask_geckoboard.__version__,
    license = flask_geckoboard.__license__,
    description = 'Geckoboard custom widgets for Flask projects',
    long_description = build_long_description(),
    author = flask_geckoboard.__author__,
    author_email = flask_geckoboard.__email__,
    packages = [
        'flask_geckoboard',
        'tests',
    ],
    install_requires = (
        'flask'
    ),
    extras_require = {
        'encryption': ['pycrypto']
    },
    keywords = ['flask', 'geckoboard'],
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Flask',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    platforms = ['any'],
    url = 'http://github.com/PolymathVentures/flask-geckoboard',
    download_url = 'http://github.com/PolymathVentures/flask-geckoboard/archives/master',
)
