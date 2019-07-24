[![Build Status](https://travis-ci.com/rshanker779/love_island.svg?branch=master)](https://travis-ci.com/rshanker779/love_island)

# Project
This project is designed to collect reddit comments for selected posts on the LoveIslandTV on the love island subreddit, 
store them in appropriate relational structure using SQLAlchemy ORM, apply sentiment analysis and then create metrics of 
popularity throughout the show (this last section is still in progress).

# Packages
The package reddit has files to connect to reddit api, currently via praw
https://praw.readthedocs.io/en/latest/

The data_models pacakage has classes to describe structure of parsed data if using a relational database.

The love_island_reddit package has files to get the data, figure out mentioned islanders, and add sentiment analysis (using VADER in nltk)

# Build
The setup.py details the build. Versioning of packages should be assumed to be latest available.