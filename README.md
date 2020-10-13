# FRANK
Frank is a question answering framework that combines multiple forms of reasoning, including deductive, statistical and arithmetic to answer question.

# Reference Papers
Here are links to our academic papers on FRANK. Please reference these papers when you use or extend FRANK.

1. *todo*

# Demo
A demo of this reference implementation of FRANK can be found at http://app.frank.nuamah.com/

# Installation

## Requirements
Requires Python 3.5 or higher. Python dependencies can be found in *`requirements.txt`*.

## External Dependencies
FRANK requires the following third-party tools to run. For the **FRANK API**, the following are required:
* Node4j graph database
* Redis database
* MongoDB
* spaCy: [Install](https://spacy.io/usage#installation) the [en_core_web_md](https://spacy.io/models/en#en_core_web_md) model.

The configuration file `config.py` contains settings for running FRANK on your local computer and for running FRANK on the server.

While running FRANK locally, we advice that you set up the database endpoints to use the databases on remote FRANK server. Alternatively, you can install FRANK and the DBs locally.

`TODO:` Instructions for installing DBs locally will be added soon.

## Launching the API

The FRANK API can be launched from the terminal with the command:

```
python frank_api.py
```

# Launching the UI

The UI is a Javascript application built with `React` on `NodeJS`.
From within the UI source root directory, run this command in the terminal:

```
npm start
```






