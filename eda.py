from pathlib import Path
import json
import pandas as pd
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parent
OUT=ROOT/"reports"; OUT.mkdir(exist_ok=True)
raw=pd.read_csv(ROOT/"Atlantic_France.csv")
df=raw.copy()
df["date"]=pd.to_datetime(df["date"],format="%d-%m-%Y",errors="coerce")
df["duration_min"]=df["duration_ms"]/60000
df["album_type"]=df["album_type"].astype(str).str.strip().str.lower()
per_date=df.groupby("date").size()
summary={
 "rows":int(len(df)),
 "source_columns":int(len(raw.columns)),
 "missing_cells":int(raw.isna().sum().sum()),
 "duplicate_rows":int(raw.duplicated().sum()),
 "date_min":str(df["date"].min().date()),
 "date_max":str(df["date"].max().date()),
 "unique_dates":int(df["date"].nunique()),
 "dates_with_50_rows":int((per_date==50).sum()),
 "dates_with_unusual_row_count":int((per_date!=50).sum()),
 "unusual_dates":{str(k.date()):int(v) for k,v in per_date[per_date!=50].items()},
 "explicit_counts":{str(k):int(v) for k,v in df["is_explicit"].value_counts(dropna=False).items()},
 "album_type_counts":{str(k):int(v) for k,v in df["album_type"].value_counts(dropna=False).items()},
 "mean_popularity_by_explicit":df.groupby("is_explicit")["popularity"].mean().round(3).to_dict(),
 "mean_popularity_by_album_type":df.groupby("album_type")["popularity"].mean().round(3).to_dict(),
 "mean_duration_min":float(df["duration_min"].mean()),
}
json.dump(summary,open(OUT/"eda_summary.json","w"),indent=2,default=str)
print(json.dumps(summary,indent=2,default=str))
counts=df["is_explicit"].value_counts().rename(index={True:"Explicit",False:"Non-explicit"})
plt.figure(figsize=(7,4)); counts.plot(kind="bar"); plt.title("Explicit vs Non-explicit Track Records"); plt.ylabel("Records"); plt.tight_layout(); plt.savefig(OUT/"explicit_distribution.png",dpi=160); plt.close()
plt.figure(figsize=(7,4)); df["album_type"].value_counts().plot(kind="bar"); plt.title("Album Type Distribution"); plt.ylabel("Records"); plt.tight_layout(); plt.savefig(OUT/"album_type_distribution.png",dpi=160); plt.close()
plt.figure(figsize=(7,4)); plt.hist(df["duration_min"].dropna(),bins=30); plt.title("Track Duration Distribution"); plt.xlabel("Minutes"); plt.ylabel("Records"); plt.tight_layout(); plt.savefig(OUT/"duration_distribution.png",dpi=160); plt.close()
print("\\nPopularity by explicit flag:\\n",df.groupby("is_explicit")["popularity"].agg(["count","mean","median"]))
print("\\nPopularity by album type:\\n",df.groupby("album_type")["popularity"].agg(["count","mean","median"]))
