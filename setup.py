import os
from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='nla_client',
    version='0.1.3',
    packages=['nla_client'],
    install_requires=['requests',
                      'python_dateutil',
    ],
    include_package_data=True,
    license='BSD License',  # example license
    description='A command line client to access the near-line archive (NLA) on JASMIN.',
    long_description=README,
    url='http://www.ceda.ac.uk/',
    author='Neil Massey',
    author_email='support@ceda.ac.uk',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: HTTP API',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License', # example license
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    entry_points = {
        'console_scripts': ['nla=nla_client.nla:main'],
    }
)
