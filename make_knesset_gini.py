"""Gini coefficient of Knesset seat distribution, 1st to 26th Knesset (1949 to 2026).

Data: data/knesset_data.csv, the lists that won seats and their seats as declared
after each election, from the English Wikipedia election pages (one per Knesset,
e.g. https://en.wikipedia.org/wiki/2026_Israeli_legislative_election), read on
6/11/2026; the 26th Knesset rows match the Central Elections Committee final
results. data/knesset_data_dates.csv holds the election dates.

Writes data/knesset_gini.csv (one row per Knesset) and knesset_gini.png, in
Hebrew and in the brand style of the book לא כאוס ולא בטיח׳.
Run: python make_knesset_gini.py
"""
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from bidi.algorithm import get_display as he

HERE = Path(__file__).parent
plt.style.use("/Users/boris/Documents/podcasts/hashavua/presentations/_brand/minimal.mplstyle")
plt.rcParams["font.sans-serif"] = ["Noto Sans Hebrew", "Inter"]
INK, MUTED, ORANGE = "#0B0B0B", "#52514E", "#EB6834"

DIRECT_FROM, DIRECT_TO = pd.Timestamp("1996-05-29"), pd.Timestamp("2003-01-28")  # 14th and 16th elections


def gini(values):
    # http://planspace.org/2013/06/21/how-to-calculate-gini-coefficient-from-raw-data-in-python/
    height, area = 0, 0
    for v in sorted(values):
        height += v
        area += height - v / 2
    fair_area = height * len(values) / 2
    return (fair_area - area) / fair_area


assert gini([1, 1, 1, 1]) == 0
assert gini([0, 0, 0, 1]) == 0.75  # one holder among n: (n - 1) / n

seats = pd.read_csv(HERE / "data/knesset_data.csv")
dates = pd.read_csv(HERE / "data/knesset_data_dates.csv", parse_dates=["date_from"])
assert (seats.groupby("number").seats.sum() == 120).all()
assert sorted(seats.number.unique()) == list(range(1, 27))

tbl = seats.groupby("number").seats.agg(gini=gini, lists="count", largest="max").reset_index()
tbl = tbl.merge(dates[["number", "date_from"]], on="number").rename(columns={"date_from": "election"})
tbl = tbl[["number", "election", "lists", "largest", "gini"]]
tbl.to_csv(HERE / "data/knesset_gini.csv", index=False, float_format="%.3f")
print(tbl.to_string(index=False))

fig, ax = plt.subplots()
fig.subplots_adjust(top=.84, bottom=.08, left=.06, right=.98)
x = list(tbl.election) + [pd.Timestamp("2027-06-30")]  # hold the last step open past the 26th election
y = list(tbl.gini) + [tbl.gini.iloc[-1]]
ax.axvspan(DIRECT_FROM, DIRECT_TO, color=ORANGE, alpha=.12, lw=0)
ax.step(x, y, where="post", color=INK)
ax.plot(tbl.election, tbl.gini, "o", color=INK, ms=5)
ax.text(DIRECT_FROM + (DIRECT_TO - DIRECT_FROM) / 2, .575, he("בחירה ישירה\nלראש הממשלה"),
        ha="center", va="center", color=ORANGE, fontsize=13, fontweight="bold", linespacing=1.4)
ax.text(pd.Timestamp("2020-12-01"), .50, he("חמש מערכות בחירות\nבשלוש וחצי שנים"),
        ha="center", va="bottom", color=MUTED, fontsize=10.5, linespacing=1.4)
last = tbl.iloc[-1]
ax.text(last.election - pd.Timedelta(days=120), last.gini, he(f"הכנסת ה־26: {last.gini:.2f}"),
        ha="right", va="center", color=MUTED, fontsize=10.5)
ax.set_xlim(pd.Timestamp("1948-01-01"), pd.Timestamp("2027-06-30"))
ax.set_ylim(.25, .7)
ax.set_yticks([.3, .4, .5, .6, .7])
ax.set_xticks([pd.Timestamp(f"{y}-01-01") for y in range(1950, 2030, 10)])
ax.set_xticklabels([str(y) for y in range(1950, 2030, 10)])
fig.text(.06, .95, he("הבחירה הישירה בוטלה. המפלגות הגדולות לא חזרו"),
         ha="left", va="top", fontsize=15, fontweight="bold", color=INK)
fig.text(.06, .895, he("מדד ג׳יני של חלוקת המושבים בין הרשימות שנבחרו לכנסת, לפי מועד הבחירות"),
         ha="left", va="top", fontsize=11, color=MUTED)
fig.savefig(HERE / "knesset_gini.png")
print("saved knesset_gini.png")
