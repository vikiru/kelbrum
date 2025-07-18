import polars as pl
import streamlit as st

@st.cache_resource
def read_data():
    df = pl.read_csv("./data/anime-dataset-2023.csv", null_values=["UNKNOWN"])
    return df

def filter_data(df: pl.DataFrame) -> pl.DataFrame:
    return df

def get_unique_values(df: pl.DataFrame, column_name: str) -> pl.DataFrame:
    splitted_str_col = df[column_name].str.split(",").list.eval(pl.element().str.strip_chars())
    exploded_df = splitted_str_col.explode().fill_null("Unknown")
    unique_values = exploded_df.unique().to_frame()
    unique_counts = exploded_df.unique_counts().to_frame()
    unique_df = pl.DataFrame({f"{column_name.capitalize()}": unique_values, "Counts": unique_counts})
    return unique_df

def fill_null_with_unknown(df: pl.DataFrame) -> pl.DataFrame:
    return df.fill_null("Unknown")



# TODO: create clean.py -> conv cols into better format (i.e. str sep -> list, premiered/aired -> season, year, episodes -> minutes and remove <24 mins)
# TODO: see if there is anything else worth removing/cleaning
# TODO: create sep module dedicated to fetching data. Must be able to 1) update existing data efficiently 2) fetch new data (check latest year/season and start from there)
# TODO: create sep module for feature engineering, normalization and kmeans clustering
# TODO: streamlit app -> create pages for overview of raw csv data (metadata, top anime by criteria, total unique values/counts, etc), 
# page for showcasing clusters (total # of anime per cluster, cluster stats, error metrics, etc)
# page for selecting two anime and seeing their metadata, tensors, distance/similarity
