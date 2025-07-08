import streamlit as st
import polars as pl

from process_data import fill_null_with_unknown, get_unique_values, read_data

df = read_data()
filtered_df = df.filter(
    (pl.col("Type").is_null()) |
    (pl.col("Type") != "Special") &
    (pl.col("Type") != "OVA") &
    (pl.col("Type") != "Music") &
    (~pl.col("Genres").str.contains_any(["Hentai", "Erotica"])))

filtered_df = fill_null_with_unknown(filtered_df)

st.title("Overview")

unique_count_cols = ["Genres", "Type", "Licensors", "Producers", "Studios", "Source"]
for col in filtered_df.columns:
    if col in unique_count_cols:
        st.subheader(col.capitalize())
        data = get_unique_values(filtered_df, col)
        st.write(data)


top_100_df = filtered_df.sort("Score", descending=True).drop_nulls().head(100).select(["Name", "Score"])
st.subheader("Top 100 Anime by Score")
st.write(top_100_df)

bottom_100_df = filtered_df.sort("Score", descending=False).drop_nulls().head(100).select(["Name", "Score"])
st.subheader("Bottom 100 Anime by Score")
st.write(bottom_100_df)
