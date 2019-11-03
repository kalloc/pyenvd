from setuptools import setup

setup(
   name='envd',
   version='0.1',
   description='',
   packages=['envd'],
   install_requires=[
       'click==7.0',
       'aiorpcx==0.18.3',
       'aiofiles==0.4.0',
       'daemonize==2.4.7'
   ],
)
