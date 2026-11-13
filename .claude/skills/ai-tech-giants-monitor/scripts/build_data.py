#!/usr/bin/env python3
# 儀表板資料產生器：data/portfolio.json＋data/closes.csv＋data/notes.json → dashboard/data/*.json（6 個資料檔）。
# 頁面 dashboard/index.html 固定不動，每期只重跑這支、把 6 個檔上傳到儀表板換掉舊的。
# 成本與均價只留在 portfolio.json，不進任何輸出（輸出只有總報酬率與總損益）。
# 用法：python3 scripts/build_data.py [--asof YYYY-MM-DD] [--out 目錄]
import argparse, csv, json, math, os, datetime as dt
from statistics import NormalDist
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
Phi = NormalDist().cdf

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--asof'); ap.add_argument('--out', default=f'{ROOT}/dashboard/data'); a = ap.parse_args()
    P = json.load(open(f'{ROOT}/data/portfolio.json', encoding='utf-8'))
    NT = json.load(open(f'{ROOT}/data/notes.json', encoding='utf-8'))
    px = {}
    for r in csv.DictReader(open(f'{ROOT}/data/closes.csv', encoding='utf-8')):
        px.setdefault(r['date'], {})[r['symbol']] = float(r['close'])
    pos = P['positions']; syms = [p['symbol'] for p in pos]
    days = sorted(d for d in px if all(s in px[d] for s in syms))
    D = a.asof or days[-1]; prev = days[days.index(D) - 1]; base = dt.date.fromisoformat(D)
    c, c0 = px[D], px[prev]
    mv = {p['symbol']: p['shares'] * c[p['symbol']] for p in pos}
    MV = sum(mv.values()); COST = sum(p['cost'] for p in pos)
    M = P['model']; mu = math.log(1 + M['neutral_annual'])      # 中性：每年約 10%
    SIG = sum(mv[p['symbol']] * p['vol'] for p in pos) / MV      # 組合波動（市值加權，假設一起漲跌）
    yrs = lambda d: (dt.date.fromisoformat(d) - base).days / 365
    md = lambda d: f"{int(d[5:7])}/{int(d[8:])}"
    ymd = lambda d: f"{d[:4]}/{int(d[5:7])}/{int(d[8:])}"
    ret = lambda v: round((v / COST - 1) * 100, 1)

    # 三情境（§1-10）：每檔 P·exp(μt ± σ√t)，全部抱著
    def total(d, z):
        t = yrs(d); return sum(p['shares'] * c[p['symbol']] * math.exp(mu * t + z * p['vol'] * math.sqrt(t)) for p in pos)
    scen = [dict(date=D, label=f'現在（{md(D)}）', is_base=1, optimistic=round(MV), neutral=round(MV), pessimistic=round(MV),
                 opt_ret=ret(MV), neu_ret=ret(MV), pes_ret=ret(MV))]
    for d in M['dates']:
        o, n, w = total(d, 1), total(d, 0), total(d, -1)
        scen.append(dict(date=d, label=ymd(d), is_base=0, optimistic=round(o), neutral=round(n), pessimistic=round(w),
                         opt_ret=ret(o), neu_ret=ret(n), pes_ret=ret(w)))

    # 目標進度（§1-11）：行情與新投入分開記
    G = P['goal']; T = G['target']; trades = P['trades_since_goal_start']
    new_money = sum(t['amount'] for t in trades if t['date'] <= D)
    r = (1 + M['neutral_annual']) ** (1 / 12) - 1
    plan = []
    for d in M['goal_dates']:
        t = yrs(d); gr = math.exp(mu * t); n = max(1, round(t * 12)); fv = sum((1 + r) ** (n - k) for k in range(1, n + 1))
        prob = 1 - Phi((math.log(T / MV) - mu * t) / (SIG * math.sqrt(t)))
        plan.append(dict(target_date=d, label=ymd(d), lump_sum=round(T / gr - MV), monthly=round((T - MV * gr) / fv), months=n,
                         prob_pct=round(prob * 100), is_default=int(d == G['default_date'])))
    pf = lambda t, z: math.exp(mu * t + z * SIG * math.sqrt(t))
    def months_to(cash, z):                                       # 複利模式：每月投入一起滾，幾個月到目標
        for m in range(1, 121):
            if MV * pf(m / 12, z) + sum(cash * pf(m / 12, z) / pf(k / 12, z) for k in range(1, m + 1)) >= T: return m
        return None
    comp = [dict(monthly=cash, optimistic_months=months_to(cash, 1), neutral_months=months_to(cash, 0), pessimistic_months=months_to(cash, -1))
            for cash in M['monthlies']]

    # 短期倉：收盤或盤中最高碰到目標價就算到價
    S = P['short_term']; sc = c[S['symbol']]; alert = NT.get('intraday', {}).get(S['symbol']) or {}
    status = 'done' if S.get('status') == 'sold' else 'hit' if sc >= S['target'] else 'touched' if alert.get('high', 0) >= S['target'] else 'watch'
    prog = 100 if status != 'watch' else max(0, min(100, (sc - S['cost']) / (S['target'] - S['cost']) * 100))

    marks = P.get('week_marks') or [P['last_week']]                    # 上一期週報的日期與市值；取 D 之前最近的一筆
    LW = max((m for m in marks if m['date'] < D), key=lambda m: m['date']); wk = MV - LW['market_value'] - sum(t['amount'] for t in trades if LW['date'] < t['date'] <= D)
    grp = lambda g: sum(mv[p['symbol']] for p in pos if p['group'] == g) / MV * 100
    day = sum(p['shares'] * (c[p['symbol']] - c0[p['symbol']]) for p in pos)
    default_row = next(x for x in plan if x['is_default'])
    summary = [dict(
        as_of=D, as_of_label=md(D), n_holdings=len(pos), n_shares=sum(p['shares'] for p in pos),
        market_value=round(MV), day_change_pct=round(day / (MV - day) * 100, 1),
        pnl=round(MV - COST), return_pct=round((MV / COST - 1) * 100, 1),
        week_change_pct=round(wk / LW['market_value'] * 100, 1), week_base_label=md(LW['date']),
        semi_pct=round(grp('semi'), 1), musk_pct=round(grp('musk'), 1), tsm_shock_pct=round(mv['TSM'] * 0.3 / MV * 100, 1),
        goal_target=T, goal_pct=round(MV / T * 100, 1), goal_gap=round(T - MV),
        goal_start_label=md(G['start_date']), goal_start_mv=round(G['start_mv']),
        goal_market=round(MV - G['start_mv'] - new_money), goal_new_money=round(new_money),
        goal_default_label=default_row['label'], goal_default_monthly=default_row['monthly'],
        mu_status=status, mu_target=S['target'], mu_close=round(sc, 2), mu_gap_pct=round((S['target'] / sc - 1) * 100, 1),
        mu_progress_pct=round(prog), mu_last=alert.get('last'), mu_high=alert.get('high'), mu_time=alert.get('time', ''))]

    LABEL = {'green': '綠燈', 'amber': '黃燈', 'red': '紅燈'}; wk0 = px[LW['date']]
    holdings = []
    for p in sorted(pos, key=lambda p: -mv[p['symbol']]):
        s = p['symbol']; h = NT['holdings'].get(s, {}); light = h.get('light', 'green'); note = h.get('note', ''); cap = p.get('cap_pct')
        if cap:                                                            # 佔比上限只擋加碼：算出離上限還能加幾股（加碼的錢也算進市值）
            room = max(0, int((cap / (100 - cap) * (MV - mv[s]) - mv[s]) // c[s]))
            note = (note + '。' if note else '') + f'上限 {cap}%：目前 {mv[s] / MV * 100:.1f}%，還能加約 {room} 股'
        holdings.append(dict(symbol=s, shares=p['shares'], weight_pct=round(mv[s] / MV * 100, 1), close=round(c[s], 2),
                             day_pct=round((c[s] / c0[s] - 1) * 100, 1), week_pct=round((c[s] / wk0[s] - 1) * 100, 1),
                             light=light, light_label=LABEL[light], note=note))
    KIND = {'todos': 'todo', 'calendar': 'calendar', 'news': 'news'}
    notes = [dict(kind=KIND[k], key=x['key'], date_label=x.get('date_label', ''), title=x['title'], detail=x.get('detail', ''),
                  tone=x.get('tone', ''), url=x.get('url', '')) for k in ('todos', 'calendar', 'news') for x in NT.get(k, [])]

    os.makedirs(a.out, exist_ok=True)
    for name, rows in dict(summary=summary, holdings=holdings, scenarios=scen, goal_plan=plan, compound=comp, notes=notes).items():
        json.dump(rows, open(f'{a.out}/{name}.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    s0 = summary[0]
    print(f"asof {D} MV {MV:.2f} cost {COST:.2f} ret {s0['return_pct']}% day {s0['day_change_pct']}% week {s0['week_change_pct']}% | goal {s0['goal_pct']}% gap {s0['goal_gap']} market {s0['goal_market']} new {s0['goal_new_money']} | MU {status} prog {s0['mu_progress_pct']}% gap {s0['mu_gap_pct']}%")
    print('scen', [(x['label'], x['optimistic'], x['neutral'], x['pessimistic']) for x in scen[1:]], '| monthly', [x['monthly'] for x in plan], '| comp', [(x['monthly'], x['optimistic_months'], x['neutral_months'], x['pessimistic_months']) for x in comp])
main()
