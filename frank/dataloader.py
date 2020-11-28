import os
import re
import pandas as pd


def load_data(filename):
    ''' load wikidata properties in a pandas dataframe from a pickle file'''
    ''

    directory = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), 'data')
    filepath = os.path.join(directory, filename)

    if not os.path.exists(directory):
        os.makedirs(directory)

    csv_file = filepath + '.csv'
    pickle_file = filepath + '.pickle'
    if os.path.isfile(pickle_file) is False:
        if os.path.isfile(pickle_file) is False:
            df = pd.read_csv(
                f'https://franklab.s3-eu-west-1.amazonaws.com/datasets/{filename}.csv')
            df.to_csv(filepath + '.csv')
        else:
            df = pd.read_csv(csv_file)
        df.to_pickle(pickle_file)
    else:
        df = pd.read_pickle(pickle_file)
    return df


def load_wikidata_props():
    return load_data('wikidata_props')


def load_worldbank_props():
    return load_data('worldbank_props')


def load_worldbank_countries():
    return load_data('worldbank_countries')


def load_predicate_priors():
    return load_data('predicate_priors')


def save_predicate_priors(df: pd.DataFrame):
    update_data(df, 'predicate_priors')


def load_source_priors():
    return load_data('source_priors')


def save_source_priors(df: pd.DataFrame):
    update_data(df, 'source_priors')


def update_data(df: pd.DataFrame, filename):
    filepath = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), 'data', filename + '.pickle')
    df.to_pickle(filepath)
