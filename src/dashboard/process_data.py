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




