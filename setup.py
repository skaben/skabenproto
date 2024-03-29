from setuptools import setup, find_packages

with open("README.md", 'r') as f:
    long_description = f.read()

setup(
   name='skabenproto',
   version='2.00',
   description='SKABEN protocol',
   license="MIT",
   long_description=long_description,
   author='Zerthmonk',
   author_email='zerthmonk@pm.me',
   url="yantratekk.me",
   packages=['skabenproto'], 
)
