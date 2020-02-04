import pandas as pd


def load_structures_as_df(structures_file_path):
    return pd.read_csv(structures_file_path, sep=",", header=0, quotechar='"')
