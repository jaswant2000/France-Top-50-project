from pathlib import Path
import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "Atlantic_France.csv"
st.set_page_config(page_title="France Top 50 Content Analysis", page_icon="🎵", layout="wide")

@st.cache_data
def load_data():
    d = pd.read_csv(DATA)
    d["date"] = pd.to_datetime(d["date"], format="%d-%m-%Y", errors="coerce")
    d["duration_min"] = d["duration_ms"] / 60000
    d["album_type"] = d["album_type"].astype(str).str.strip().str.lower()
    d["is_explicit"] = d["is_explicit"].astype("boolean")
    d["rank_tier"] = pd.cut(d["position"], bins=[0, 10, 25, 50, 100], labels=["Top 10", "11–25", "26–50", "51–100"])
    return d

df = load_data()
st.title("🎵 France Top 50 Playlist: Audience Sensitivity & Format Analysis")
st.caption("Interactive descriptive analytics using the supplied Atlantic_France.csv dataset")
st.info("This dashboard analyses playlist snapshots and popularity scores. It does not directly measure cultural sensitivity, listener attitudes, or causal effects.")

with st.sidebar:
    st.header("Filters")
    min_date, max_date = df["date"].min().date(), df["date"].max().date()
    dates = st.date_input("Date range", value=(min_date, max_date), min_value=min_date, max_value=max_date)
    tiers = st.multiselect("Rank tier", ["Top 10", "11–25", "26–50", "51–100"], default=["Top 10", "11–25", "26–50"])
    explicit_choice = st.selectbox("Explicit content", ["All", "Explicit only", "Non-explicit only"])
    album_choices = sorted(df["album_type"].dropna().unique().tolist())
    chosen_albums = st.multiselect("Album type", album_choices, default=album_choices)

if len(dates) == 2:
    start, end = dates
else:
    start, end = min_date, max_date

view = df[(df["date"].dt.date >= start) & (df["date"].dt.date <= end)].copy()
if tiers:
    view = view[view["rank_tier"].astype(str).isin(tiers)]
view = view[view["album_type"].isin(chosen_albums)]
if explicit_choice == "Explicit only":
    view = view[view["is_explicit"] == True]
elif explicit_choice == "Non-explicit only":
    view = view[view["is_explicit"] == False]

if view.empty:
    st.warning("No records match these filters. Widen the filters.")
    st.stop()

c1,c2,c3,c4 = st.columns(4)
c1.metric("Records in view", f"{len(view):,}")
c2.metric("Explicit share", f"{view['is_explicit'].mean()*100:.1f}%")
c3.metric("Average popularity", f"{view['popularity'].mean():.1f}")
c4.metric("Average duration", f"{view['duration_min'].mean():.2f} min")

tab1,tab2,tab3,tab4,tab5 = st.tabs(["Compliance overview","Explicit vs clean","Release format","Duration & album size","Data quality"])
with tab1:
    st.subheader("Explicit-content share")
    st.bar_chart((view["is_explicit"].value_counts(normalize=True)*100).rename(index={True:"Explicit",False:"Non-explicit"}))
    st.subheader("Content profile by rank tier")
    tier_summary = view.groupby("rank_tier", observed=True).agg(
        records=("song","size"),
        explicit_share=("is_explicit","mean"),
        avg_popularity=("popularity","mean"),
        avg_duration_min=("duration_min","mean"),
        avg_album_tracks=("total_tracks","mean")
    ).reset_index()
    tier_summary["explicit_share"] = (tier_summary["explicit_share"]*100).round(2)
    st.dataframe(tier_summary.round(2), use_container_width=True)
    st.caption("The term 'compliance' here describes the explicit-content flag distribution; it is not a legal compliance audit.")
with tab2:
    st.subheader("Popularity and rank: explicit vs non-explicit")
    comp = view.groupby("is_explicit").agg(records=("song","size"),mean_popularity=("popularity","mean"),median_popularity=("popularity","median"),mean_position=("position","mean"),mean_duration_min=("duration_min","mean")).rename(index={True:"Explicit",False:"Non-explicit"})
    st.dataframe(comp.round(2),use_container_width=True)
    st.bar_chart(view.groupby("is_explicit")["popularity"].mean().rename(index={True:"Explicit",False:"Non-explicit"}))
    st.bar_chart(view.groupby("is_explicit")["position"].mean().rename(index={True:"Explicit",False:"Non-explicit"}))
with tab3:
    st.subheader("Release format distribution")
    st.bar_chart(view["album_type"].value_counts())
    st.subheader("Popularity and rank by album type")
    st.dataframe(view.groupby("album_type").agg(records=("song","size"),share=("song",lambda s:len(s)/len(view)*100),avg_popularity=("popularity","mean"),avg_position=("position","mean"),avg_album_tracks=("total_tracks","mean")).round(2),use_container_width=True)
    st.bar_chart(view.groupby("album_type")["popularity"].mean())
with tab4:
    st.subheader("Song duration distribution")
    fig,ax=plt.subplots()
    ax.hist(view["duration_min"].dropna(),bins=25)
    ax.set_xlabel("Duration (minutes)"); ax.set_ylabel("Track records"); ax.set_title("Duration distribution")
    st.pyplot(fig)
    st.subheader("Duration bucket analysis")
    bins=[0,2.5,3.5,100]; labels=["Short (<2.5 min)","Medium (2.5–3.5 min)","Long (>3.5 min)"]
    tmp=view.copy(); tmp["duration_bucket"]=pd.cut(tmp["duration_min"],bins=bins,labels=labels,right=False)
    st.dataframe(tmp.groupby("duration_bucket",observed=True).agg(records=("song","size"),avg_popularity=("popularity","mean"),avg_position=("position","mean"),explicit_share=("is_explicit","mean")).assign(explicit_share=lambda x:x["explicit_share"]*100).round(2),use_container_width=True)
    st.subheader("Album size vs popularity")
    st.scatter_chart(view, x="total_tracks", y="popularity", color="album_type")
with tab5:
    st.subheader("Data quality checks")
    full = load_data()
    date_counts=full.groupby("date").size()
    quality=pd.DataFrame([
        ["Rows",len(full)],
        ["Source columns",10],
        ["Missing cells",int(pd.read_csv(DATA).isna().sum().sum())],
        ["Exact duplicate rows",int(pd.read_csv(DATA).duplicated().sum())],
        ["Distinct dates",int(full["date"].nunique())],
        ["Dates with exactly 50 rows",int((date_counts==50).sum())],
        ["Dates with non-50 row count",int((date_counts!=50).sum())],
    ],columns=["Check","Result"])
    st.dataframe(quality,use_container_width=True)
    st.write("Dates with unusual record counts:")
    st.dataframe(date_counts[date_counts!=50].rename("rows").reset_index(),use_container_width=True)
    st.caption("Duplicates are reported, not automatically removed: repeated songs can legitimately appear in different daily snapshots.")
st.subheader("Filtered track records")
cols=["date","position","song","artist","popularity","duration_min","album_type","total_tracks","is_explicit"]
st.dataframe(view[cols].sort_values(["date","position"]),use_container_width=True, height=350)
csv=view[cols].to_csv(index=False).encode("utf-8")
st.download_button("Download filtered records as CSV",csv,"france_top50_filtered.csv","text/csv")
