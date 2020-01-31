import csv
import pandas as pd


def load_structures(structures_file_path):
    with open(structures_file_path, "r") as structures_file:
        structures_reader = csv.reader(
            structures_file, delimiter=",", quotechar='"'
        )
        structures = list(structures_reader)
        header = structures[0]
        structures = structures[1:]
        return header, structures


def load_structures_as_df(structures_file_path):
    return pd.read_csv(structures_file_path, sep=",", header=0, quotechar='"')
