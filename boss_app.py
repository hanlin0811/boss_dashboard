"""老闆雲端唯讀 Dashboard — CrunCheese × CoCo。
讀 boss_data.json（由 Mac 每天 push），密碼保護、唯讀顯示兩店營運數字。"""

import html
import json
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

st.set_page_config(page_title="CrunCheese × CoCo 營運", page_icon="🧋", layout="wide")

# 每家店固定一個顏色，所有圖表與列表一致；其餘介面一律黑白灰
STORE_COLOR = {"Azusa": "#c8641e", "Southridge": "#1d5fbf"}
FONT = "Geist, 'Noto Sans TC', 'PingFang TC', 'Microsoft JhengHei', system-ui, sans-serif"
DATA = Path(__file__).parent / "boss_data.json"


# ── 密碼閘 ──────────────────────────────────────────────────
def check_password() -> bool:
    if st.session_state.get("boss_auth"):
        return True
    expected = st.secrets.get("boss_password", None)
    st.markdown("### CrunCheese × CoCo 營運")
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


def _avg_ticket(x):
    return x["sales"] / x["tc"] if x.get("tc") else 0


# ── 樣式：石灰底、白卡、黑字；顏色只用在店別與漲跌 ───────────────────
_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Geist:wght@400;500;700&family=Noto+Sans+TC:wght@400;500;700&display=swap');
:root{--ground:#f4f3f1;--surface:#fff;--border:#e6e6e6;--rule:#f0f0f0;
      --text:#0a0a0a;--ink2:#3d3d3d;--muted:#6b6b6b;--pos:#2e7d32;--neg:#c4242a}
.stApp{font-variant-numeric:tabular-nums}
[data-testid="stCaptionContainer"]{color:var(--muted)}
.stApp [class*="st-key-card"]{background:var(--surface);padding:20px 24px}
.stApp [class*="st-key-card"] .panel-head{margin-bottom:0}
.brand{display:flex;align-items:center;gap:8px;font-size:14px;color:var(--muted)}
.brand b{color:var(--text);font-weight:500}
.finding{font-size:15px;line-height:22px;color:var(--ink2);margin:0}
.stamp{font-size:12px;line-height:18px;color:var(--muted);margin:2px 0 8px}
.notice{background:#fffbeb;border:1px solid #fde68a;color:#92400e;font-size:13px;
        line-height:20px;border-radius:8px;padding:10px 14px;margin-top:10px}
.panel{background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:20px 24px;min-width:0}
.blk{margin-bottom:14px}
.panel-head{display:flex;flex-wrap:wrap;justify-content:space-between;align-items:baseline;
            gap:2px 12px;margin-bottom:14px}
.panel-head h2{white-space:nowrap}
.panel h2,.panel h3{font-size:16px;font-weight:500;line-height:24px;margin:0;padding:0}
.meta{font-size:12px;color:var(--muted);white-space:nowrap}
.d{font-size:12px;line-height:18px;color:var(--muted);white-space:nowrap}
.up{color:var(--pos);font-weight:500}.dn{color:var(--neg);font-weight:500}
.dot{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:8px;vertical-align:1px}
/* 最新一日帳本：兩列同欄位，數字上下對齊 */
.kp{display:grid;grid-template-columns:1.3fr repeat(4,1fr)}
.kp>div{padding:0 20px;border-left:1px solid var(--rule)}
.kp>div:first-child{padding-left:0;border-left:0}
.kp .l{font-size:12px;line-height:18px;color:var(--muted);white-space:nowrap}
.kp .v{font-size:22px;line-height:30px;font-weight:500}
.kp .v.m{font-weight:700}
.kp .lead .v{font-size:30px;line-height:40px}
.kp.sub{margin-top:16px;padding-top:14px;border-top:1px solid var(--rule)}
.kp.sub .v,.kp.sub .lead .v{font-size:16px;line-height:24px}
.al-h{margin-top:18px;padding-top:14px;border-top:1px solid var(--rule);display:flex;
      justify-content:space-between;align-items:baseline}
.al{display:grid;grid-template-columns:auto auto auto 1fr;gap:8px 16px;align-items:center;
    font-size:14px;line-height:20px;margin-top:10px}
.pill{display:inline-block;font-size:12px;font-weight:500;line-height:20px;padding:0 8px;
      border-radius:4px;white-space:nowrap}
.pill.red{background:#ffedea;color:#831c1e}.pill.amber{background:#fffbeb;color:#92400e}
.empty{font-size:14px;color:var(--muted);margin-top:8px}
/* 並排卡片 */
.duo{display:grid;grid-template-columns:minmax(0,7fr) minmax(0,5fr);gap:14px}
.duo.even{grid-template-columns:minmax(0,1fr) minmax(0,1fr)}
.kp.two{grid-template-columns:repeat(2,max-content);margin:4px 0 12px}
.scroll{overflow-x:auto}
table.lg{width:100%;border-collapse:collapse;border:0!important;margin:0}
.lg tr{border:0!important;background:none!important}
.lg th,.lg td{border:0!important}
.lg th{font-size:12px;font-weight:400;color:var(--muted);text-align:right;padding:0 0 8px 16px;white-space:nowrap}
.lg td{text-align:right;padding:11px 0 11px 16px;border-top:1px solid var(--rule)!important;font-size:14px;
       line-height:20px;vertical-align:top;white-space:nowrap}
.lg th:first-child,.lg td:first-child{text-align:left;padding-left:0;position:sticky;left:0;
       background:var(--surface);padding-right:12px}
.lg td .d{display:block}
.lg tr.tot td{font-weight:500}
.lg .na{color:var(--muted)}
/* 通路：同一組灰階，色塊即圖例 */
.ch-key{display:flex;flex-wrap:wrap;gap:6px 16px;font-size:12px;color:var(--ink2)}
.ch-key i{display:inline-block;width:10px;height:10px;margin-right:6px;vertical-align:-1px}
.ch-s{margin-top:16px}
.ch-n{display:flex;justify-content:space-between;font-size:14px;line-height:20px;margin-bottom:6px}
.ch-bar{display:flex;gap:2px;height:24px}
.ch-bar>div{display:flex;align-items:center;justify-content:center;font-size:12px;overflow:hidden;white-space:nowrap}
.ch-det{font-size:12px;line-height:18px;color:var(--muted);margin-top:6px}
.ch-det b{font-weight:400;color:var(--text)}
@media (max-width:860px){
  .duo,.duo.even{grid-template-columns:minmax(0,1fr)}
  [data-testid="stMainBlockContainer"]{padding-left:18px!important;padding-right:18px!important}
}
@media (max-width:640px){
  .panel{padding:16px}
  .kp{grid-template-columns:1fr 1fr;row-gap:12px}
  .kp>div,.kp>div:first-child{padding:0;border-left:0}
  .kp .lead{grid-column:1 / -1}
  .kp.two{grid-template-columns:1fr 1fr}
  .al{grid-template-columns:auto 1fr;gap:4px 12px}
  .al .msg{grid-column:1 / -1;margin-bottom:6px}
}
</style>
"""

CH_ORDER = ["Dine In", "Pickup", "Delivery"]
CH_LABEL = {"Dine In": "堂食", "Pickup": "外帶自取", "Delivery": "外送"}
# (底色, 字色)：深、中、淺三階灰
CH_TONE = {"Dine In": ("#2b2b2b", "#fff"), "Pickup": ("#6b6b6b", "#fff"),
           "Delivery": ("#d4d4d4", "#0a0a0a")}


def _delta_pct(cur, prev):
    return (cur - prev) / prev * 100 if prev else None


def _usd(v):
    """HTML 用金額；&#36; 避免 Streamlit 把兩個 $ 之間當成 LaTeX 公式。"""
    return f"&#36;{v:,.2f}"


def _dot(store):
    return f'<span class="dot" style="background:{STORE_COLOR.get(store, "#141414")}"></span>'


def _chg_span(dp):
    """漲綠跌紅；四捨五入為 0 用灰色「±0%」，無基準用灰色「—」。"""
    if dp is None:
        return '<span class="na">—</span>'
    r = round(dp)
    if r == 0:
        return "±0%"
    cls, arr = ("up", "▲") if r > 0 else ("dn", "▼")
    return f'<span class="{cls}">{arr} {abs(r)}%</span>'


def _delta_html(dp, base):
    return f'<div class="d">{_chg_span(dp)} {base}</div>'


def _html(s):
    st.markdown(s, unsafe_allow_html=True)


def _heading(text, meta=""):
    m = f'<span class="meta">{meta}</span>' if meta else ""
    return f'<div class="panel-head"><h2>{text}</h2>{m}</div>'


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


@st.cache_data(show_spinner=False)
def _item_daily_df(_records, sig=""):
    """把 item_daily records 轉 DataFrame（date 轉 date 物件）。
    以 sig（generated_ts）當快取鍵；_records 不參與雜湊，避免每次切期間重解析 ~萬筆。"""
    if not _records:
        return pd.DataFrame(columns=["date", "store", "item", "category", "qty", "amt"])
    df = pd.DataFrame(_records)
    df["date"] = pd.to_datetime(df["date"]).dt.date
    return df


def _top_from_df(sub, stores, n=10):
    """從 df 算熱銷（同 boss_export.top_items_from_df），供自訂區間即時計算。"""
    out = {}
    for store in stores:
        sdf = sub[sub["store"] == store]
        is_drink = sdf["category"].str.lower() == "drinks"
        grp = {}
        for cat_key, cdf in (("drinks", sdf[is_drink]), ("food", sdf[~is_drink])):
            total = int(cdf["qty"].sum()) or 1
            agg = cdf.groupby("item")["qty"].sum().sort_values(ascending=False).head(n)
            grp[cat_key] = [{"item": k, "qty": int(v), "pct": round(v / total * 100, 1)}
                            for k, v in agg.items()]
        out[store] = grp
    return out


def _newshare_from_df(sub, stores, new_list):
    """從 df 算新品佔比（同 boss_export.new_items_share_from_df）。"""
    per = {s: {x.strip().lower() for x in new_list.get(s, [])} for s in stores}
    if not any(per.values()):
        return {}
    out = {}
    tot = {"qty_new": 0, "qty_all": 0, "amt_new": 0.0, "amt_all": 0.0}
    for store in stores:
        sdf = sub[sub["store"] == store]
        qa, aa = int(sdf["qty"].sum()), float(sdf["amt"].sum())
        # 佔比＝佔同類（飲料/食物）同期總數量，與熱銷品項表口徑一致
        is_drink = sdf["category"].str.lower() == "drinks"
        cat_total = {True: int(sdf.loc[is_drink, "qty"].sum()),
                     False: int(sdf.loc[~is_drink, "qty"].sum())}
        ndf = sdf[sdf["item"].str.strip().str.lower().isin(per[store])]
        qn, an = int(ndf["qty"].sum()), float(ndf["amt"].sum())
        agg = ndf.assign(_drink=ndf["category"].str.lower() == "drinks") \
            .groupby("item").agg(qty=("qty", "sum"), amt=("amt", "sum"),
                                 drink=("_drink", "max")) \
            .sort_values("qty", ascending=False)
        detail = []
        for k, r in agg.iterrows():
            ct = cat_total[bool(r.drink)]
            detail.append({"item": k, "qty": int(r.qty),
                           "amt": round(float(r.amt), 2),
                           "pct": round(int(r.qty) / ct * 100, 1) if ct else 0.0})
        out[store] = {"qty_new": qn, "qty_all": qa, "amt_new": round(an, 2),
                      "amt_all": round(aa, 2), "detail": detail}
        tot["qty_new"] += qn; tot["qty_all"] += qa
        tot["amt_new"] += an; tot["amt_all"] += aa
    tot["amt_new"] = round(tot["amt_new"], 2); tot["amt_all"] = round(tot["amt_all"], 2)
    out["total"] = tot
    return out


def _fmt_chg(v):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return "新"
    if round(v) == 0:
        return "±0%"
    return f"{'▲' if v > 0 else '▼'} {abs(v):.0f}%"


def _color_chg(v):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return "color:#92400e;font-weight:500"
    if round(v) == 0:
        return "color:#6b6b6b"
    return "color:#2e7d32;font-weight:500" if v > 0 else "color:#c4242a;font-weight:500"


def _show_table(col, df, show, fmt, chg_vals):
    """品項表：變化欄先轉成文字（st.dataframe 會把空值畫成 None），顏色依原始數值；數字欄靠右。"""
    if chg_vals is not None:
        df = df.assign(變化=[_fmt_chg(v) for v in chg_vals])
    sty = df[show].style.format(fmt)
    if chg_vals is not None:
        sty = sty.apply(lambda _c: [_color_chg(v) for v in chg_vals], subset=["變化"])
    cfg = {c: st.column_config.Column(alignment="right") for c in show[1:]}
    cfg[show[0]] = st.column_config.Column(pinned=True)
    col.dataframe(sty, hide_index=True, width="stretch", column_config=cfg)


def _item_change(df, stores, s, e):
    """每支品項 vs 上一期（同長度、緊接在前）的數量變化%。
    回 ({store: {item: pct or None}}, has_prev)。has_prev=False：前一期超出資料範圍。"""
    L = (e - s).days + 1
    ps, pe = s - timedelta(days=L), s - timedelta(days=1)
    dmin = df["date"].min() if not df.empty else None
    has_prev = dmin is not None and ps >= dmin
    cur = df[(df["date"] >= s) & (df["date"] <= e)]
    prv = df[(df["date"] >= ps) & (df["date"] <= pe)]
    out = {}
    for store in stores:
        c = cur[cur["store"] == store].groupby("item")["qty"].sum()
        p = prv[prv["store"] == store].groupby("item")["qty"].sum()
        out[store] = {it: ((int(cq) - int(p.get(it, 0))) / int(p.get(it, 0)) * 100
                           if int(p.get(it, 0)) else None) for it, cq in c.items()}
    return out, has_prev


def _new_table(col, detail, chg):
    """新品明細表；chg=該店 {item:變化%}，None 則不顯示變化欄。"""
    items = [r["item"] for r in detail]
    ndf = pd.DataFrame(detail).rename(
        columns={"item": "品項", "qty": "數量", "amt": "銷售額", "pct": "佔比"})
    fmt = {"銷售額": lambda v: f"${v:,.2f}", "佔比": lambda v: f"{v:.1f}%"}
    if chg is not None:
        show = ["品項", "數量", "佔比", "變化", "銷售額"]
    else:
        show = ["品項", "數量", "佔比", "銷售額"]
    _show_table(col, ndf, show, fmt, [chg.get(it) for it in items] if chg is not None else None)


def _top_table(col, rows, chg):
    """熱銷表；chg=該店 {item:變化%}，None 則不顯示變化欄。"""
    items = [r["item"] for r in rows]
    tdf = pd.DataFrame(rows).rename(columns={"item": "品項", "qty": "數量", "pct": "佔比"})
    fmt = {"佔比": lambda v: f"{v:.1f}%"}
    if chg is not None:
        show = ["品項", "數量", "佔比", "變化"]
    else:
        show = ["品項", "數量", "佔比"]
    _show_table(col, tdf, show, fmt, [chg.get(it) for it in items] if chg is not None else None)


def _wd(iso):
    return "一二三四五六日"[date.fromisoformat(iso).weekday()]


def _md(iso):
    p = iso.split("-")
    return f"{int(p[1])}/{int(p[2])}" if len(p) == 3 else iso


def _chart_cfg(ch):
    """圖表：無外框、淡格線、無 y 軸線、標籤 12px 灰。"""
    return (ch.configure(font=FONT, background="transparent")
            .configure_view(stroke=None)
            .configure_axis(labelColor="#6b6b6b", labelFontSize=12, gridColor="#ececec",
                            domainColor="#d4d4d4", tickColor="#d4d4d4", labelPadding=6)
            .configure_axisY(domain=False, ticks=False)
            .configure_legend(orient="top", direction="horizontal", title=None, labelFontSize=12,
                              labelColor="#3d3d3d", padding=0, offset=10))


def _store_scale(stores):
    return alt.Scale(domain=list(stores), range=[STORE_COLOR.get(s, "#141414") for s in stores])


def _ledger_row(cur, prev, stores, lead_label, base, sub=False):
    """一列：兩店合計、各店營業額、來客、客單價；delta 對上週同日。"""
    t = cur["total"]
    tp = prev["total"] if prev else None

    def cell(label, value, cv, pv, money, lead=False):
        dp = _delta_pct(cv, pv) if pv else None
        return (f'<div class="{"lead" if lead else ""}"><div class="l">{label}</div>'
                f'<div class="v{" m" if money else ""}">{value}</div>{_delta_html(dp, base)}</div>')

    cells = [cell(lead_label, _usd(t["sales"]), t["sales"], tp["sales"] if tp else None, True, True)]
    for s in stores:
        sv = cur[s]["sales"] if cur.get(s) else 0
        spv = prev[s]["sales"] if prev and prev.get(s) else None
        cells.append(cell(f"{_dot(s)}{html.escape(s)}", _usd(sv), sv, spv, True))
    cells.append(cell("來客 合計", f"{t['tc']:,}", t["tc"], tp["tc"] if tp else None, False))
    at = t["sales"] / t["tc"] if t["tc"] else 0
    atp = tp["sales"] / tp["tc"] if tp and tp["tc"] else None
    cells.append(cell("客單價", _usd(at), at, atp, True))
    return (f'<div class="kp{" sub" if sub else ""}" style="--n:{len(cells) - 1}">'
            + "".join(cells) + "</div>")


def _finding(day, cur, prev, stores):
    """標題下一句：最新一日兩店合計對上週同日，並點出變化最大的店。"""
    t, tp = cur["total"]["sales"], prev["total"]["sales"]
    head = f"{_md(day)}（週{_wd(day)}）兩店營業額 {_usd(t)}"
    if not tp:
        return head + "。"
    r = round(_delta_pct(t, tp))
    if r == 0:
        return head + f"，和上週{_wd(day)}持平。"
    word = "多" if r > 0 else "少"
    moves = [(s, _delta_pct(cur[s]["sales"], prev[s]["sales"])) for s in stores
             if cur.get(s) and prev.get(s) and prev[s]["sales"]]
    moves = [m for m in moves if (m[1] > 0) == (r > 0)]
    tail = ""
    if moves:
        s, dp = max(moves, key=lambda m: abs(m[1]))
        tail = f"，{'主要來自' if r > 0 else '主要是'} {html.escape(s)}（{word} {abs(dp):.0f}%）"
    return head + f"，比上週{_wd(day)}{word} {abs(r)}%{tail}。"


def render():
    try:
        d = load_data()
    except Exception:
        st.error("目前讀不到資料，請稍後再試。")
        return

    gen = d.get("generated_at", "—")
    _html(_CSS)
    stores = d["stores"]
    daily = d.get("daily", {})

    # ── 資料新鮮度警示（夜間同步可能失敗）──
    # 優先用帶時區的時間戳算「絕對小時」，避免雲端(UTC)與 Mac(PDT)日期偏移誤報；
    # 夜跑每 24h 一次 → 超過 36h 未更新才示警。舊資料無 ts 時退回日期比較（放寬到 3 天）。
    stale_hint = None
    stamp = gen
    gts = d.get("generated_ts")
    if gts:
        try:
            gdt = datetime.fromisoformat(gts)
            stamp = gdt.strftime("%Y-%m-%d %H:%M")
            hrs = (datetime.now(timezone.utc) - gdt.astimezone(timezone.utc)).total_seconds() / 3600
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

    latest, _ = _latest_two_dates(daily, stores)
    alerts = find_alerts(daily, stores)

    # ── 標題：品牌、頁名、今天最該知道的一句 ──
    hues = [STORE_COLOR.get(s, "#141414") for s in stores[:2]] + ["#141414"] * 2
    mark = ('<svg width="24" height="14" viewBox="0 0 24 14" aria-hidden="true">'
            f'<circle cx="7" cy="7" r="6" fill="{hues[0]}"/>'
            f'<circle cx="16" cy="7" r="6" fill="{hues[1]}" stroke="#f4f3f1" stroke-width="2"/></svg>')
    _html(f'<div class="brand">{mark}<b>CrunCheese × CoCo</b>'
          f'<span>{" · ".join(html.escape(s) for s in stores)}</span></div>')
    st.title("營運總覽")

    finding = ""
    if latest:
        today_d = latest
        yest_d = (date.fromisoformat(today_d) - timedelta(days=1)).isoformat()
        lw_today = (date.fromisoformat(today_d) - timedelta(days=7)).isoformat()
        lw_yest = (date.fromisoformat(yest_d) - timedelta(days=7)).isoformat()
        cur_today = _day_row(daily, stores, today_d)
        prev_today = _day_row(daily, stores, lw_today)
        finding = _finding(today_d, cur_today, prev_today, stores)
    if alerts:
        finding += f"　近 10 天有 {len(alerts)} 筆異常。"
    notice = (f'<div class="notice">資料可能未更新：最後更新 {gen}（{stale_hint}）。'
              f'夜間同步可能失敗，以下數字請當「舊資料」看。</div>' if stale_hint else "")
    _html(f'<p class="finding">{finding}</p>'
          f'<p class="stamp">資料更新於 {stamp} · 唯讀</p>{notice}')

    # ── 最新一日（完整營業日）+ 前一日：各 vs 上週同日；下方接近 10 天異常 ──
    if alerts:
        rows = "".join(
            f'<span class="meta">{dt}</span><span>{_dot(store)}{html.escape(store)}</span>'
            f'<span class="pill {level}">{"紅燈" if level == "red" else "注意"}</span>'
            f'<span class="msg">{html.escape(msg).replace("$", "&#36;")}</span>'
            for dt, store, level, msg in alerts)
        al = (f'<div class="al-h"><h3>需要注意</h3><span class="meta">近 10 天 · {len(alerts)} 筆</span></div>'
              f'<div class="al">{rows}</div>')
    else:
        al = ('<div class="al-h"><h3>需要注意</h3><span class="meta">近 10 天</span></div>'
              '<div class="empty">近 10 天沒有異常。</div>')
    if latest:
        body = _ledger_row(cur_today, prev_today, stores, "兩店營業額", f"vs 上週{_wd(today_d)}")
        cur_yest = _day_row(daily, stores, yest_d)
        if cur_yest["total"]["sales"] or any(cur_yest.get(s) for s in stores):
            prev_yest = _day_row(daily, stores, lw_yest)
            body += _ledger_row(cur_yest, prev_yest, stores,
                                f"{_md(yest_d)}（週{_wd(yest_d)}）合計",
                                f"vs 上週{_wd(yest_d)}", sub=True)
        head = _heading(f"{today_d}（週{_wd(today_d)}）", "最新一日 · 對上週同日")
        _html(f'<div class="panel blk">{head}{body}{al}</div>')
    else:
        _html(f'<div class="panel blk">{al}</div>')

    # ── 本週（近 7 天，合計＋各店）＋ 通路 ──
    tw, lw = d["week"]["this"], d["week"]["last"]

    def _side(side, key):
        """取某側（this/last）某店或合計的數字；相容舊格式（扁平＝合計）。"""
        if isinstance(side, dict) and "total" in side:
            return side.get(key, {"sales": 0, "cups": 0, "tc": 0})
        return side if key == "total" else {"sales": 0, "cups": 0, "tc": 0}

    cols_def = [("營業額", "sales", True), ("杯數", "cups", False), ("食物", "food", False),
                ("來客", "tc", False), ("客單價", None, True)]
    thead = "<tr><th>店</th>" + "".join(f"<th>{c[0]}</th>" for c in cols_def) + "</tr>"
    tbody = ""
    for key, label, cls in [("total", "兩店合計", "tot")] + \
            [(s, f"{_dot(s)}{html.escape(s)}", "") for s in stores]:
        a, b = _side(tw, key), _side(lw, key)
        tds = ""
        for _lbl, k, money in cols_def:
            cv, pv = (_avg_ticket(a), _avg_ticket(b)) if k is None else (a.get(k, 0), b.get(k, 0))
            tds += f'<td>{_usd(cv) if money else f"{cv:,}"}{_delta_html(_delta_pct(cv, pv), "")}</td>'
        tbody += f'<tr class="{cls}"><td>{label}</td>{tds}</tr>'
    week_html = (f'<div class="panel">{_heading("本週", "近 7 天 · 對上週")}'
                 f'<div class="scroll"><table class="lg">{thead}{tbody}</table></div></div>')

    cm = d.get("channel_mix", {})
    ch_html = ""
    if cm:
        key_html = "".join(f'<span><i style="background:{CH_TONE[c][0]}"></i>{CH_LABEL[c]}</span>'
                           for c in CH_ORDER)
        blocks = ""
        for store in stores:
            twc = cm.get(store, {}).get("this", {})
            lwc = cm.get(store, {}).get("last", {})
            tot = sum(twc.values())
            segs, parts = "", []
            for ch in CH_ORDER:
                n, ln = twc.get(ch, 0), lwc.get(ch, 0)
                parts.append(f'{CH_LABEL[ch]} <b>{n}</b> {_chg_span((n - ln) / ln * 100 if ln else None)}')
                share = n / tot * 100 if tot else 0
                if share <= 0:
                    continue
                bg, fg = CH_TONE[ch]
                segs += (f'<div style="flex:{share:.2f} 1 0;background:{bg};color:{fg}" '
                         f'title="{CH_LABEL[ch]} {n} 單（{share:.0f}%）">'
                         f'{f"{share:.0f}%" if share >= 10 else ""}</div>')
            blocks += (f'<div class="ch-s"><div class="ch-n"><span>{_dot(store)}{html.escape(store)}</span>'
                       f'<span class="meta">{tot:,} 單</span></div><div class="ch-bar">{segs}</div>'
                       f'<div class="ch-det">{" · ".join(parts)}</div></div>')
        ch_html = (f'<div class="panel">{_heading("通路", "本週訂單 · 對上週")}'
                   f'<div class="ch-key">{key_html}</div>{blocks}'
                   f'<div class="ch-det" style="margin-top:14px">外帶自取＝自助機＋人工外帶'
                   f'（兩店 POS 標籤不同已合併）。</div></div>')
    _html(f'<div class="duo blk">{week_html}{ch_html}</div>' if ch_html else f'<div class="blk">{week_html}</div>')

    # ── 每日銷售趨勢 ──
    with st.container(border=True, key="card_daily"):
        _html(_heading("每日銷售", "各店每日營業額"))
        win = st.radio("區間", [30, 60, 90], index=0, horizontal=True,
                       format_func=lambda x: f"近 {x} 天", label_visibility="collapsed")
        rows = []
        for store in d["stores"]:
            for r in d["daily"].get(store, [])[-win:]:
                rows.append({"date": r["date"], "store": store, "sales": r["sales"]})
        if rows:
            df = pd.DataFrame(rows)
            chart = alt.Chart(df).mark_line(strokeWidth=2).encode(
                x=alt.X("date:T", title=None,
                        axis=alt.Axis(format="%m/%d", labelAngle=0, tickCount=6, grid=False)),
                y=alt.Y("sales:Q", title=None, axis=alt.Axis(format="$,.0f", tickCount=5)),
                color=alt.Color("store:N", scale=_store_scale(stores)),
                tooltip=[alt.Tooltip("date:T", title="日期", format="%m/%d"),
                         alt.Tooltip("store:N", title="店"),
                         alt.Tooltip("sales:Q", title="營業額", format="$,.2f")],
            ).properties(height=240)
            st.altair_chart(_chart_cfg(chart), width="stretch", theme=None)
        else:
            st.caption("尚無每日資料。")

    # ── 每月總計 ──
    mrows = []
    for store in d["stores"]:
        for r in d["monthly"].get(store, []):
            mrows.append({"月份": r["month"], "店別": store,
                          "營業額": r["sales"], "杯數": r["cups"], "來客": r["tc"]})
    if mrows:
        mdf = pd.DataFrame(mrows)
        months = sorted(mdf["月份"].unique())
        meta = f"{months[0]} – {months[-1]}"
        if latest and latest[:7] == months[-1]:
            meta += f" · {int(latest[5:7])} 月計至 {int(latest[8:])} 日"
        with st.container(border=True, key="card_monthly"):
            _html(_heading("每月營業額", meta))
            mbar = alt.Chart(mdf).mark_bar().encode(
                x=alt.X("月份:N", title=None, sort=months,
                        axis=alt.Axis(labelAngle=0, labelExpr="toNumber(slice(datum.label, 5)) + '月'")),
                xOffset=alt.XOffset("店別:N", sort=list(stores)),
                y=alt.Y("營業額:Q", title=None, axis=alt.Axis(format="$,.0f", tickCount=5)),
                color=alt.Color("店別:N", scale=_store_scale(stores)),
                tooltip=["月份", "店別", alt.Tooltip("營業額:Q", format="$,.2f"), "杯數", "來客"],
            ).properties(height=240)
            st.altair_chart(_chart_cfg(mbar), width="stretch", theme=None)

    # ── 同比 YoY（今年 vs 去年同月），兩店並排 ──
    # 當月還沒過完時，boss_export 的去年同月只算到同一天（月至今對月至今），月份標出「至 N 日」
    _last = max((r["date"] for s_ in d["stores"] for r in d.get("daily", {}).get(s_, [])), default="")
    _cur_m = _last[:7]
    _month_done = bool(_last) and (date.fromisoformat(_last) + timedelta(days=1)).day == 1

    def _mlabel(m):
        return f"{m}（至 {int(_last[8:10])} 日）" if m == _cur_m and not _month_done else m

    yrows = []
    for store in d["stores"]:
        for r in d["monthly"].get(store, []):
            ly = r.get("sales_ly")
            yoy = (r["sales"] - ly) / ly * 100 if ly else None
            yrows.append({"month": r["month"], "store": store, "sales": r["sales"],
                          "ly": ly, "yoy": yoy})
    if any(row["ly"] for row in yrows):
        panels = ""
        for store in d["stores"]:
            trs = "".join(
                f'<tr><td>{_mlabel(r["month"])}</td><td>{_usd(r["sales"])}</td>'
                f'<td>{_usd(r["ly"]) if r["ly"] else "<span class=na>—</span>"}</td>'
                f'<td>{_chg_span(r["yoy"])}</td></tr>'
                for r in yrows if r["store"] == store)
            panels += (f'<div class="panel">{_heading(f"{_dot(store)}{html.escape(store)} 同比", "今年 vs 去年同月")}'
                       f'<div class="scroll"><table class="lg"><tr><th>月份</th><th>今年</th>'
                       f'<th>去年同月</th><th>YoY</th></tr>{trs}</table></div></div>')
        _html(f'<div class="duo even">{panels}</div>')
        st.caption("YoY＝(今年−去年同月) ÷ 去年同月。當月還沒過完時，去年同月只算到同一天"
                   "（月至今對月至今）。去年同月已套用同比修正（如缺失月份）。")

    # ── 品項期間：新品與熱銷各一組選單（含自訂區間），標題帶出實際日期 ──
    PERIOD_LABELS = {"7d": "近 7 天", "14d": "近 14 天", "30d": "近 30 天",
                     "last_week": "上週", "last_month": "上個月"}
    top_all = d.get("top_items", {})
    new_all = d.get("new_items_share", {})
    pdates = d.get("period_dates", {})
    has_custom = bool(d.get("item_daily"))
    avail = [k for k in PERIOD_LABELS if k in top_all or k in new_all]

    def _plabel(k):
        r = pdates.get(k)
        return (f"{PERIOD_LABELS[k]} {_md(r[0])}-{_md(r[1])}"
                if r and len(r) == 2 else PERIOD_LABELS[k])

    def _pct(n, a):
        return n / a * 100 if a else 0

    idf = _item_daily_df(d.get("item_daily", []), d.get("generated_ts", ""))

    def _resolve(key):
        """畫期間選單（含自訂區間），回 (plabel, ns, ti, s, e)；自訂尚未選完回 None。"""
        opts = avail + (["custom"] if has_custom else [])
        sel = st.radio("期間 Period", opts, horizontal=True, key=key + "_p",
                       label_visibility="collapsed",
                       format_func=lambda k: "自訂" if k == "custom" else PERIOD_LABELS[k])
        if sel != "custom":
            r = pdates.get(sel) or []
            try:
                s, e = date.fromisoformat(r[0]), date.fromisoformat(r[1])
            except (ValueError, IndexError):
                s = e = None
            return _plabel(sel), new_all.get(sel, {}), top_all.get(sel, {}), s, e
        rng = d.get("item_daily_range") or []
        try:
            dmin, dmax = date.fromisoformat(rng[0]), date.fromisoformat(rng[1])
        except (ValueError, IndexError):
            st.caption("自訂區間資料暫無。")
            return None
        picked = st.date_input("自訂日期（起～迄）",
                               value=(max(dmin, dmax - timedelta(days=6)), dmax),
                               min_value=dmin, max_value=dmax, key=key + "_r")
        if not (isinstance(picked, (list, tuple)) and len(picked) == 2):
            st.info("請選擇結束日期。")
            return None
        s, e = picked
        sub = idf[(idf["date"] >= s) & (idf["date"] <= e)]
        return (f"{_md(s.isoformat())}-{_md(e.isoformat())}",
                _newshare_from_df(sub, stores, d.get("new_items_list", {})),
                _top_from_df(sub, stores), s, e)

    def _chg_for(s, e):
        if s and e and not idf.empty:
            return _item_change(idf, stores, s, e)
        return {}, False

    def _store_h(store, extra=""):
        return (f'<div class="ch-n" style="margin:4px 0 2px"><span>{_dot(store)}'
                f'<b style="font-weight:500">{html.escape(store)}</b></span>'
                f'<span class="meta">{extra}</span></div>')

    if avail:
        # 新品佔比（自己的期間選單）
        with st.container(border=True, key="card_new"):
            head = st.empty()
            r = _resolve("new")
            plabel = r[0] if r else ""
            head.markdown(_heading("新品佔比", plabel), unsafe_allow_html=True)
            if r:
                _, ns, _ti, s, e = r
                chg, has_prev = _chg_for(s, e)
                if ns and ns.get("total") and ns["total"].get("qty_all"):
                    t = ns["total"]
                    _html('<div class="kp two">'
                          f'<div><div class="l">兩店數量佔比</div><div class="v">'
                          f'{_pct(t["qty_new"], t["qty_all"]):.1f}%</div></div>'
                          f'<div><div class="l">兩店銷售額佔比</div><div class="v">'
                          f'{_pct(t["amt_new"], t["amt_all"]):.1f}%</div></div></div>')
                    cols = st.columns(len(stores))
                    for col, store in zip(cols, stores):
                        x = ns.get(store) or {}
                        qp, ap = _pct(x.get("qty_new", 0), x.get("qty_all", 0)), \
                            _pct(x.get("amt_new", 0), x.get("amt_all", 0))
                        col.markdown(_store_h(store, f"數量 {qp:.1f}% · 銷售額 {ap:.1f}%"),
                                     unsafe_allow_html=True)
                        detail = x.get("detail", [])
                        if detail:
                            _new_table(col, detail, chg.get(store) if has_prev else None)
                        else:
                            col.caption("無新品銷售")
                    cap = "佔比＝該新品佔同店同類（飲料或食物）同期總數量（與熱銷品項表口徑一致）。"
                    cap += ("變化＝數量 vs 上一期（同長度、緊接在前），「新」＝前期無此品項。"
                            if has_prev else "（前一期資料不足，未顯示變化）")
                    st.caption(cap + "新品清單手動維護（兩店分開，改 new_items.json）。")
                else:
                    st.caption("此期間無新品銷售。")

        # 熱銷品項（自己的期間選單）
        with st.container(border=True, key="card_top"):
            head2 = st.empty()
            r2 = _resolve("top")
            head2.markdown(_heading("熱銷品項", r2[0] if r2 else ""), unsafe_allow_html=True)
            if r2:
                _, _ns2, ti, s2, e2 = r2
                chg2, has_prev2 = _chg_for(s2, e2)
                if not ti:
                    st.caption("品項資料暫無（下次資料更新後顯示）。")
                else:
                    for store in stores:
                        _html(_store_h(store))
                        c1, c2 = st.columns(2)
                        for col, cat_key, label in ((c1, "drinks", "飲料"), (c2, "food", "食物")):
                            col.caption(label)
                            rows = ti.get(store, {}).get(cat_key, [])
                            if rows:
                                _top_table(col, rows, chg2.get(store) if has_prev2 else None)
                            else:
                                col.caption("—")
                    cap = "佔比＝該品項佔同店同類（飲料或食物）同期總數量的百分比。"
                    st.caption(cap + ("　變化＝數量 vs 上一期。" if has_prev2 else ""))

    st.caption(f"CrunCheese × CoCo · 資料更新於 {stamp} · 每日自動更新")


if check_password():
    render()
