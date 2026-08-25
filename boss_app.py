"""老闆雲端唯讀 Dashboard — CrunCheese × CoCo。
讀 boss_data.json（由 Mac 每天 push），密碼保護、唯讀顯示兩店營運數字。"""

import json
from datetime import date
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

st.set_page_config(page_title="CrunCheese × CoCo 營運", page_icon="🧋", layout="wide")

STORE_COLOR = {"Azusa": "#e07b2a", "Southridge": "#2c8ac9"}
DATA = Path(__file__).parent / "boss_data.json"


# ── 密碼閘 ──────────────────────────────────────────────────
def check_password() -> bool:
    if st.session_state.get("boss_auth"):
        return True
    expected = st.secrets.get("boss_password", None)
    st.markdown("### 🧋 CrunCheese × CoCo 營運")
    if not expected:
        st.info("管理員尚未設定密碼（部署時於 Streamlit Cloud secrets 設定 `boss_password`）。")
        return False
    pw = st.text_input("密碼 Password", type="password")
    if pw:
        if pw == expected:
            st.session_state["boss_auth"] = True
            st.rerun()
        else:
            st.error("密碼錯誤 Wrong password")
    return False


@st.cache_data(ttl=300)
def load_data():
    return json.loads(DATA.read_text(encoding="utf-8"))


def _kpi(col, label, value, delta=None):
    col.metric(label, value, delta)


def render():
    try:
        d = load_data()
    except Exception:
        st.error("目前讀不到資料，請稍後再試。")
        return

    gen = d.get("generated_at", "—")
    st.title("🧋 營運總覽 Operations")
    st.caption(f"資料更新於 {gen}　·　唯讀 Read-only")

    # ── 本週 KPI（合計＋各店，含週比較）──
    tw, lw = d["week"]["this"], d["week"]["last"]

    def _side(side, key):
        """取某側（this/last）某店或合計的數字；相容舊格式（扁平＝合計）。"""
        if isinstance(side, dict) and "total" in side:
            return side.get(key, {"sales": 0, "cups": 0, "tc": 0})
        return side if key == "total" else {"sales": 0, "cups": 0, "tc": 0}

    def delta(cur, prev):
        if not prev:
            return None
        return f"{(cur - prev) / prev * 100:+.0f}% vs 上週"

    def kpi_row(this_d, last_d):
        c1, c2, c3, c4 = st.columns(4)
        _kpi(c1, "營業額 Sales", f"${this_d['sales']:,.0f}", delta(this_d['sales'], last_d['sales']))
        _kpi(c2, "杯數 Cups", f"{this_d['cups']:,}", delta(this_d['cups'], last_d['cups']))
        _kpi(c3, "食物份數 Food Items", f"{this_d.get('food', 0):,}",
             delta(this_d.get('food', 0), last_d.get('food', 0)))
        _kpi(c4, "來客 Orders", f"{this_d['tc']:,}", delta(this_d['tc'], last_d['tc']))

    st.subheader("本週 This Week（近 7 天）")
    st.markdown("**合計 Total（兩店）**")
    kpi_row(_side(tw, "total"), _side(lw, "total"))
    for store in d["stores"]:
        st.markdown(f"**{store}**")
        kpi_row(_side(tw, store), _side(lw, store))

    st.divider()

    # ── 每日銷售趨勢 ──
    st.subheader("每日銷售趨勢 Daily Sales")
    win = st.radio("區間", [30, 60, 90], index=0, horizontal=True,
                   format_func=lambda x: f"近 {x} 天")
    rows = []
    for store in d["stores"]:
        for r in d["daily"].get(store, [])[-win:]:
            rows.append({"date": r["date"], "store": store, "sales": r["sales"]})
    if rows:
        df = pd.DataFrame(rows)
        chart = alt.Chart(df).mark_line(point=False).encode(
            x=alt.X("date:T", title=None, axis=alt.Axis(format="%m/%d")),
            y=alt.Y("sales:Q", title="營業額 $"),
            color=alt.Color("store:N", title="店別",
                            scale=alt.Scale(domain=list(STORE_COLOR.keys()),
                                            range=list(STORE_COLOR.values()))),
            tooltip=[alt.Tooltip("date:T", title="日期", format="%m/%d"),
                     "store:N", alt.Tooltip("sales:Q", title="營業額", format="$,.0f")],
        ).properties(height=320)
        st.altair_chart(chart, use_container_width=True)

    st.divider()

    # ── 每月總計 ──
    st.subheader("每月總計 Monthly")
    mrows = []
    for store in d["stores"]:
        for r in d["monthly"].get(store, []):
            mrows.append({"月份": r["month"], "店別": store,
                          "營業額": r["sales"], "杯數": r["cups"], "來客": r["tc"]})
    if mrows:
        mdf = pd.DataFrame(mrows)
        mbar = alt.Chart(mdf).mark_bar().encode(
            x=alt.X("月份:N", title=None),
            xOffset="店別:N",
            y=alt.Y("營業額:Q", title="營業額 $"),
            color=alt.Color("店別:N", scale=alt.Scale(domain=list(STORE_COLOR.keys()),
                                                      range=list(STORE_COLOR.values()))),
            tooltip=["月份", "店別", alt.Tooltip("營業額:Q", format="$,.0f"), "杯數", "來客"],
        ).properties(height=300)
        st.altair_chart(mbar, use_container_width=True)
        pivot = mdf.pivot_table(index="月份", columns="店別", values="營業額",
                                aggfunc="sum").fillna(0)
        st.dataframe(pivot.style.format("${:,.0f}"), use_container_width=True)

    st.divider()

    # ── 本週熱銷品項：兩店分開、食物/飲料分開，含佔同類百分比 ──
    tw_items = d.get("top_items_week", {})
    st.subheader("本週熱銷品項 Top Sellers This Week（近 7 天）")
    if not tw_items:
        st.caption("品項資料暫無（下次資料更新後顯示）。")
    else:
        for store in d["stores"]:
            st.markdown(f"##### {store}")
            c1, c2 = st.columns(2)
            for col, cat_key, label in ((c1, "drinks", "🥤 飲料 Drinks"),
                                        (c2, "food", "🍽️ 食物 Food")):
                col.caption(label)
                rows = tw_items.get(store, {}).get(cat_key, [])
                if rows:
                    tdf = pd.DataFrame(rows)
                    tdf["佔比"] = tdf["pct"].map(lambda p: f"{p:.1f}%")
                    tdf = tdf.rename(columns={"item": "品項", "qty": "數量"})
                    col.dataframe(tdf[["品項", "數量", "佔比"]], hide_index=True,
                                  use_container_width=True)
                else:
                    col.caption("—")
        st.caption("佔比＝該品項佔同店同類（飲料或食物）本週總數量的百分比。")

    st.caption(f"CrunCheese × CoCo · 資料更新於 {gen} · 每日自動更新")


if check_password():
    render()
