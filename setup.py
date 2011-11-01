import os
from setuptools import setup, find_packages
import django_oauth2_lite


def read(fname):
    try:
        return open(os.path.join(os.path.dirname(__file__), fname)).read()
    except IOError:
        return ''


setup(
    name="django-oauth2-lite",
    version=django_oauth2_lite.__version__,
    description=read('DESCRIPTION'),
    long_description=read('README.rst'),
    keywords='oauth2',
    packages=find_packages(),
    author='Leif Johansson',
    author_email='leifj@sunet.se',
    url="",
    include_package_data=True,
    test_suite='django-oauth2-lite.tests.runtests.runtests',
)
