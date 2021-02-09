from requests import Session

from frank.config import config


session = Session()
session.headers['user-agent'] = config['user-agent']

requests = session