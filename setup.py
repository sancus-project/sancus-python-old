from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='Sancus',
      version=version,
      description="Another RESTful Web Framework",
      long_description="""\
Another RESTful Web Framework but made my way""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='WSGI RESTful Framework',
      author='Alejandro Mery',
      author_email='amery@geeks.cl',
      url='https://github.com/amery/sancus-python',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
