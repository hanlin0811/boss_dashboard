"""老闆雲端唯讀 Dashboard — CrunCheese × CoCo。
讀 boss_data.json（由 Mac 每天 push），密碼保護、唯讀顯示兩店營運數字。"""

import json
from datetime import date, datetime, timedelta, timezone
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
def _load(_sig):
    return json.loads(DATA.read_text(encoding="utf-8"))


def load_data():
    # 以檔案修改時間當快取鍵：boss_data.json 一更新就自動載入新資料
    try:
        sig = DATA.stat().st_mtime_ns
    except OSError:
        sig = 0
    return _load(sig)


def _kpi(col, label, value, delta=None):
    col.metric(label, value, delta)


def _avg_ticket(x):
    return x["sales"] / x["tc"] if x.get("tc") else 0


# ── 響應式 KPI 卡片（手機自動換行，桌機一排）────────────────────────
_KPI_CSS = """
<style>
.k-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(104px,1fr));
        gap:.5rem;margin:.2rem 0 .6rem}
.k-card{background:#fffdf9;border:1px solid #eadfce;border-radius:10px;
        padding:.5rem .6rem}
.k-l{font-size:.72rem;color:#8a7d6d;margin-bottom:.1rem;white-space:nowrap}
.k-v{font-size:1.28rem;font-weight:700;line-height:1.15;color:#2a2320}
.k-d{font-size:.72rem;font-weight:600;white-space:nowrap}
.k-d small{color:#a99;font-weight:400}
.k-up{color:#1a9850}.k-dn{color:#d73027}.k-na{color:#9aa0a6}
.ch-store{font-size:.82rem;font-weight:700;color:#2a2320;margin:.5rem 0 .2rem}
.ch-bar{display:flex;height:30px;border-radius:7px;overflow:hidden;
        font-size:.72rem;font-weight:600;box-shadow:inset 0 0 0 1px rgba(0,0,0,.04)}
.ch-seg{display:flex;align-items:center;justify-content:center;color:#fff;
        white-space:nowrap;overflow:hidden}
.ch-legend{font-size:.72rem;color:#8a7d6d;margin:.1rem 0 .3rem}
.ch-detail{font-size:.76rem;color:#6b5f52;margin:.2rem 0 .1rem}
.ch-dot{display:inline-block;width:9px;height:9px;border-radius:2px;
        margin:0 .25rem 0 .7rem;vertical-align:middle}
</style>
"""


def _delta_pct(cur, prev):
    return (cur - prev) / prev * 100 if prev else None


def _kpi_cards(items, cmp_label="vs 上週"):
    """items: [{label, value, delta}] → 響應式卡片格。
    無 'delta' 鍵＝不顯示比較行；delta=None＝顯示「—」。"""
    cards = []
    for it in items:
        if "delta" not in it:
            dh = ""
        elif (dp := it["delta"]) is None:
            dh = '<span class="k-d k-na">—</span>'
        else:
            cls, arr = ("k-up", "▲") if dp >= 0 else ("k-dn", "▼")
            dh = f'<span class="k-d {cls}">{arr} {abs(dp):.0f}% <small>{cmp_label}</small></span>'
        cards.append(f'<div class="k-card"><div class="k-l">{it["label"]}</div>'
                     f'<div class="k-v">{it["value"]}</div>{dh}</div>')
    st.markdown('<div class="k-grid">' + ''.join(cards) + '</div>',
                unsafe_allow_html=True)


def _day_row(daily, stores, target_date):
    """回傳某日 {合計, 各店} 的彙總 dict；抓不到該店該日回 None。"""
    out = {"total": {"sales": 0.0, "cups": 0, "food": 0, "tc": 0}}
    for s in stores:
        row = next((r for r in daily.get(s, []) if r["date"] == target_date), None)
        out[s] = row
        if row:
            for k in ("sales", "cups", "tc"):
                out["total"][k] += row.get(k, 0)
            out["total"]["food"] += row.get("food", 0)
    return out


def _latest_two_dates(daily, stores):
    """所有店最新兩個有資料的日期（昨日、前一日）。"""
    dates = sorted({r["date"] for s in stores for r in daily.get(s, [])})
    return (dates[-1] if dates else None,
            dates[-2] if len(dates) >= 2 else None)


def find_alerts(daily, stores, lookback=10, hist_days=28):
    """從每日序列自動抓紅燈：營業額 0、食物 0（有賣飲料卻沒食物）、單日暴跌。
    回傳 [(date, store, level, msg)]，level: 'red' / 'amber'。"""
    alerts = []
    for store in stores:
        rows = daily.get(store, [])
        if not rows:
            continue
        hist = rows[-hist_days:]
        svals = sorted(r["sales"] for r in hist if r["sales"])
        med = svals[len(svals) // 2] if svals else 0
        for r in rows[-lookback:]:
            if r["tc"] and not r["sales"]:
                alerts.append((r["date"], store, "red", "營業額 $0（可能未匯入或休店）"))
            elif r["sales"] and r["cups"] and not r.get("food", 0):
                alerts.append((r["date"], store, "amber", "食物份數 0（可能漏記錄）"))
            if med and r["sales"] and r["sales"] < 0.6 * med:
                alerts.append((r["date"], store, "amber",
                               f"營業額 ${r['sales']:,.2f}，低於近月中位 ${med:,.2f} 的 6 成"))
    alerts.sort(key=lambda a: a[0], reverse=True)
    return alerts


def render():
    try:
        d = load_data()
    except Exception:
        st.error("目前讀不到資料，請稍後再試。")
        return

    gen = d.get("generated_at", "—")
    st.markdown(_KPI_CSS, unsafe_allow_html=True)
    st.title("🧋 營運總覽 Operations")
    st.caption(f"資料更新於 {gen}　·　唯讀 Read-only")

    stores = d["stores"]
    daily = d.get("daily", {})

    # ── 資料新鮮度警示（夜間同步可能失敗）──
    # 優先用帶時區的時間戳算「絕對小時」，避免雲端(UTC)與 Mac(PDT)日期偏移誤報；
    # 夜跑每 24h 一次 → 超過 36h 未更新才示警。舊資料無 ts 時退回日期比較（放寬到 3 天）。
    stale_hint = None
    gts = d.get("generated_ts")
    if gts:
        try:
            dt = datetime.fromisoformat(gts).astimezone(timezone.utc)
            hrs = (datetime.now(timezone.utc) - dt).total_seconds() / 3600
            if hrs > 36:
                stale_hint = f"約 {hrs / 24:.0f} 天前"
        except (ValueError, TypeError):
            pass
    else:
        try:
            age = (date.today() - date.fromisoformat(gen)).days
            if age >= 3:
                stale_hint = f"{age} 天前"
        except (ValueError, TypeError):
            pass
    if stale_hint:
        st.error(f"⚠️ 資料可能未更新：最後更新 {gen}（{stale_hint}）。"
                 f"夜間同步可能失敗，以下數字請當「舊資料」看。")

    # ── 今日（至今）+ 昨日（完整）快照 ──
    def _wd(iso):
        return "一二三四五六日"[date.fromisoformat(iso).weekday()]

    def _snap_items(cur, prev, with_delta):
        """組快照卡片。with_delta=False → 不放比較行（今日至今用，避免半天比整天）。"""
        t = cur["total"]
        tp = prev["total"] if prev else None

        def cell(label, value, cur_v, prev_v):
            it = {"label": label, "value": value}
            if with_delta:
                it["delta"] = _delta_pct(cur_v, prev_v) if prev_v else None
            return it
        items = [cell("營業額 合計", f"${t['sales']:,.2f}", t["sales"],
                      tp["sales"] if tp else None)]
        for s in stores:
            sv = cur[s]["sales"] if cur.get(s) else 0
            spv = prev[s]["sales"] if prev and prev.get(s) else None
            items.append(cell(f"營業額 {s}", f"${sv:,.2f}", sv, spv))
        items.append(cell("來客 合計", f"{t['tc']:,}", t["tc"],
                          tp["tc"] if tp else None))
        at = t["sales"] / t["tc"] if t["tc"] else 0
        atp = tp["sales"] / tp["tc"] if tp and tp["tc"] else None
        items.append(cell("客單價 合計", f"${at:,.2f}", at, atp))
        return items

    latest, _ = _latest_two_dates(daily, stores)
    if latest:
        today_d = latest
        yest_d = (date.fromisoformat(today_d) - timedelta(days=1)).isoformat()
        lw_today = (date.fromisoformat(today_d) - timedelta(days=7)).isoformat()
        lw_yest = (date.fromisoformat(yest_d) - timedelta(days=7)).isoformat()

        # 最新日（至今）：乾淨數字，不放會誤導的「半天 vs 整天」比較
        cur_today = _day_row(daily, stores, today_d)
        st.subheader(f"{today_d}（週{_wd(today_d)}）")
        _kpi_cards(_snap_items(cur_today, None, with_delta=False))
        lw_t = _day_row(daily, stores, lw_today)["total"]
        if lw_t["sales"]:
            st.caption(f"上週同日（整天）合計 ${lw_t['sales']:,.2f}・來客 {lw_t['tc']:,}"
                       f"　— 供對照進度")

        # 前一日（完整）：vs 上週同日
        cur_yest = _day_row(daily, stores, yest_d)
        if cur_yest["total"]["sales"] or any(cur_yest.get(s) for s in stores):
            prev_yest = _day_row(daily, stores, lw_yest)
            st.markdown(f'<div class="ch-store">{yest_d}（週{_wd(yest_d)}）· vs 上週同日</div>',
                        unsafe_allow_html=True)
            _kpi_cards(_snap_items(cur_yest, prev_yest, with_delta=True),
                       cmp_label="vs 上週同日")
        st.divider()

    # ── 本週 KPI（合計＋各店，含週比較）──
    tw, lw = d["week"]["this"], d["week"]["last"]

    def _side(side, key):
        """取某側（this/last）某店或合計的數字；相容舊格式（扁平＝合計）。"""
        if isinstance(side, dict) and "total" in side:
            return side.get(key, {"sales": 0, "cups": 0, "tc": 0})
        return side if key == "total" else {"sales": 0, "cups": 0, "tc": 0}

    def kpi_row(this_d, last_d):
        at, atl = _avg_ticket(this_d), _avg_ticket(last_d)
        items = [
            {"label": "營業額", "value": f"${this_d['sales']:,.2f}",
             "delta": _delta_pct(this_d['sales'], last_d['sales'])},
            {"label": "杯數", "value": f"{this_d['cups']:,}",
             "delta": _delta_pct(this_d['cups'], last_d['cups'])},
            {"label": "食物", "value": f"{this_d.get('food', 0):,}",
             "delta": _delta_pct(this_d.get('food', 0), last_d.get('food', 0))},
            {"label": "來客", "value": f"{this_d['tc']:,}",
             "delta": _delta_pct(this_d['tc'], last_d['tc'])},
            {"label": "客單價", "value": f"${at:,.2f}", "delta": _delta_pct(at, atl)},
        ]
        lab, labl = this_d.get("labor"), last_d.get("labor")
        if lab:
            splh = this_d["sales"] / lab
            items.append({"label": "人效 $/工時", "value": f"${splh:,.1f}",
                          "delta": _delta_pct(splh, last_d["sales"] / labl) if labl else None})
        else:
            items.append({"label": "人效 $/工時", "value": "未匯入", "delta": None})
        _kpi_cards(items)

    # ── 🚦 紅燈警示（近 10 天異常）──
    alerts = find_alerts(daily, stores)
    if alerts:
        st.subheader("🚦 需要注意 Alerts（近 10 天）")
        for dt, store, level, msg in alerts:
            icon = "🔴" if level == "red" else "🟠"
            st.markdown(f"{icon} **{dt}　{store}**　{msg}")
        st.divider()

    st.subheader("本週 This Week（近 7 天）")
    st.markdown("**合計 Total（兩店）**")
    kpi_row(_side(tw, "total"), _side(lw, "total"))
    for store in d["stores"]:
        st.markdown(f"**{store}**")
        kpi_row(_side(tw, store), _side(lw, store))

    st.divider()

    # ── 通路 Channel Mix（本週訂單佔比 + 週變化）──
    cm = d.get("channel_mix", {})
    if cm:
        CH_ORDER = ["Dine In", "Pickup", "Delivery"]
        CH_LABEL = {"Dine In": "堂食", "Pickup": "外帶自取", "Delivery": "外送"}
        CH_COLOR = {"堂食": "#d9822b", "外帶自取": "#6b8e23", "外送": "#3a7ca5"}
        st.subheader("通路 Channel Mix（本週訂單）")

        legend = "".join(
            f'<span class="ch-dot" style="background:{CH_COLOR[CH_LABEL[ch]]}"></span>'
            f'{CH_LABEL[ch]}' for ch in CH_ORDER)
        st.markdown(f'<div class="ch-legend">{legend}</div>', unsafe_allow_html=True)

        for store in stores:
            twc = cm.get(store, {}).get("this", {})
            lwc = cm.get(store, {}).get("last", {})
            tot = sum(twc.values()) or 1
            segs = ""
            for ch in CH_ORDER:
                share = twc.get(ch, 0) / tot * 100
                if share <= 0:
                    continue
                lbl = f"{share:.0f}%" if share >= 8 else ""
                segs += (f'<div class="ch-seg" style="width:{share:.2f}%;'
                         f'background:{CH_COLOR[CH_LABEL[ch]]}" '
                         f'title="{CH_LABEL[ch]} {twc.get(ch, 0)} 單（{share:.0f}%）">{lbl}</div>')
            # 每條 bar 下方一行：各通路訂單數 + 週變化（HTML，手機也穩）
            parts = []
            for ch in CH_ORDER:
                n, ln = twc.get(ch, 0), lwc.get(ch, 0)
                wow = (n - ln) / ln * 100 if ln else None
                if wow is None:
                    wtag = '<span style="color:#9aa0a6">—</span>'
                else:
                    c = "#1a9850" if wow >= 0 else "#d73027"
                    wtag = (f'<span style="color:{c};font-weight:700">'
                            f'{"▲" if wow >= 0 else "▼"}{abs(wow):.0f}%</span>')
                parts.append(f'{CH_LABEL[ch]} {n} {wtag}')
            st.markdown(f'<div class="ch-store">{store}（{tot} 單）</div>'
                        f'<div class="ch-bar">{segs}</div>'
                        f'<div class="ch-detail">{" ・ ".join(parts)}</div>',
                        unsafe_allow_html=True)

        st.caption("外帶自取＝自助機＋人工外帶（兩店 POS 標籤不同已合併）。"
                   "每條下方為各通路本週訂單數 + WoW（vs 上週同通路，▲綠/▼紅）。")

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
                     "store:N", alt.Tooltip("sales:Q", title="營業額", format="$,.2f")],
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
            tooltip=["月份", "店別", alt.Tooltip("營業額:Q", format="$,.2f"), "杯數", "來客"],
        ).properties(height=300)
        st.altair_chart(mbar, use_container_width=True)
        pivot = mdf.pivot_table(index="月份", columns="店別", values="營業額",
                                aggfunc="sum").fillna(0)
        st.dataframe(pivot.style.format("${:,.2f}"), use_container_width=True)

    # ── 同比 YoY（今年 vs 去年同月）──
    yrows = []
    for store in d["stores"]:
        for r in d["monthly"].get(store, []):
            ly = r.get("sales_ly")
            yoy = (r["sales"] - ly) / ly * 100 if ly else None
            yrows.append({"月份": r["month"], "店別": store,
                          "今年": r["sales"], "去年同月": ly,
                          "YoY": round(yoy, 0) if yoy is not None else None})
    if any(row["去年同月"] for row in yrows):
        st.subheader("同比 YoY（今年 vs 去年同月）")
        ydf = pd.DataFrame(yrows)

        def _money(v):
            return "—" if v is None or pd.isna(v) else f"${v:,.2f}"

        def _yoy_text(v):
            if v is None or pd.isna(v):
                return "—"
            return f"{'▲' if v >= 0 else '▼'} {abs(v):.0f}%"

        def _yoy_color(v):
            if v is None or pd.isna(v):
                return "color:#9aa0a6"
            return ("color:#1a9850;font-weight:700" if v >= 0
                    else "color:#d73027;font-weight:700")

        cols = st.columns(len(d["stores"]))
        for col, store in zip(cols, d["stores"]):
            sub = ydf[ydf["店別"] == store][["月份", "今年", "去年同月", "YoY"]]
            col.markdown(f"##### {store}")
            sty = (sub.style
                   .format({"今年": _money, "去年同月": _money, "YoY": _yoy_text})
                   .map(_yoy_color, subset=["YoY"]))
            col.dataframe(sty, hide_index=True, use_container_width=True)
        st.caption("YoY＝(今年−去年同月) ÷ 去年同月，正成長▲綠、衰退▼紅。去年同月已套用同比修正（如缺失月份）。")

    st.divider()

    # ── 品項期間選單（同時控制新品佔比 + 熱銷品項）──
    PERIOD_LABELS = {"7d": "近 7 天", "14d": "近 14 天", "30d": "近 30 天",
                     "last_week": "上週", "last_month": "上個月"}
    top_all = d.get("top_items", {})
    new_all = d.get("new_items_share", {})
    avail = [k for k in PERIOD_LABELS if k in top_all or k in new_all]
    if avail:
        period = st.radio("品項期間 Period", avail, horizontal=True,
                          format_func=lambda k: PERIOD_LABELS[k], key="item_period")
        plabel = PERIOD_LABELS[period]

        # 新品佔比（數量＋銷售額）
        ns = new_all.get(period, {})
        if ns and ns.get("total") and ns["total"].get("qty_all"):
            st.subheader(f"新品佔比 New Items（{plabel}）")

            def _pct(n, a):
                return n / a * 100 if a else 0

            t = ns["total"]
            _kpi_cards([
                {"label": "數量佔比 合計", "value": f"{_pct(t['qty_new'], t['qty_all']):.1f}%"},
                {"label": "銷售額佔比 合計", "value": f"{_pct(t['amt_new'], t['amt_all']):.1f}%"},
            ])
            cols = st.columns(len(stores))
            for col, store in zip(cols, stores):
                x = ns.get(store) or {}
                qp, ap = _pct(x.get("qty_new", 0), x.get("qty_all", 0)), \
                    _pct(x.get("amt_new", 0), x.get("amt_all", 0))
                col.markdown(f"##### {store}　數量 {qp:.1f}%・銷售額 {ap:.1f}%")
                detail = x.get("detail", [])
                if detail:
                    ndf = pd.DataFrame(detail)
                    ndf["銷售額"] = ndf["amt"].map(lambda v: f"${v:,.2f}")
                    ndf["佔比"] = ndf["pct"].map(lambda p: f"{p:.1f}%")
                    ndf = ndf.rename(columns={"item": "品項", "qty": "數量"})
                    col.dataframe(ndf[["品項", "數量", "銷售額", "佔比"]],
                                  hide_index=True, use_container_width=True)
                else:
                    col.caption("無新品銷售")
            st.caption(f"每支新品的{plabel}數量、銷售額；佔比＝該新品數量佔全店同期總數量。"
                       "新品清單手動維護（兩店分開，改 new_items.json）。")
            st.divider()

        # 熱銷品項：兩店分開、食物/飲料分開，含佔同類百分比
        ti = top_all.get(period, {})
        st.subheader(f"熱銷品項 Top Sellers（{plabel}）")
        if not ti:
            st.caption("品項資料暫無（下次資料更新後顯示）。")
        else:
            for store in stores:
                st.markdown(f"##### {store}")
                c1, c2 = st.columns(2)
                for col, cat_key, label in ((c1, "drinks", "🥤 飲料 Drinks"),
                                            (c2, "food", "🍽️ 食物 Food")):
                    col.caption(label)
                    rows = ti.get(store, {}).get(cat_key, [])
                    if rows:
                        tdf = pd.DataFrame(rows)
                        tdf["佔比"] = tdf["pct"].map(lambda p: f"{p:.1f}%")
                        tdf = tdf.rename(columns={"item": "品項", "qty": "數量"})
                        col.dataframe(tdf[["品項", "數量", "佔比"]], hide_index=True,
                                      use_container_width=True)
                    else:
                        col.caption("—")
            st.caption(f"佔比＝該品項佔同店同類（飲料或食物）{plabel}總數量的百分比。")

    st.caption(f"CrunCheese × CoCo · 資料更新於 {gen} · 每日自動更新")


if check_password():
    render()
