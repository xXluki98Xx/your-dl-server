﻿from setuptools import setup, find_packages

setup(
    name='your_dl_server',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'requests[socks]==2.32.3',
        'click>=8.1.3',
        'beautifulsoup4==4.12.3',
        'safer==4.12.3',
        'bottle==0.12.25',
        'yt-dlp==2024.8.6',
        'ffmpeg-python==0.2.0',
        'stem==1.8.2'
    ],
    entry_points={
        'console_scripts': [
            'dl=your_dl_server.dl:main',
        ],
    },
)
