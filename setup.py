from setuptools import setup, find_packages

import os

print(f"Current working directory: {os.getcwd()}")

setup(
    name='hyperp',
    version=open('VERSION.txt', 'r').read(),
    author='Martin Baun',
    author_email='nospam@gmail.com',
    description='Hyper charge your productivity',
    long_description=open('README.md', 'r').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/your-repo-name',
    packages=['hyperp'],
    # packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.10',
)
