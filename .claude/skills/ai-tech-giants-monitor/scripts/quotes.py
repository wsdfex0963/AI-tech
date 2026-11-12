#!/usr/bin/env python3
# 報價抓取＋匯出＋到價檢查（§1-12）。
# 主來源：Yahoo Finance chart API（免 key；環境已放行 query1.finance.yahoo.com）。
# 第二來源：Finnhub /quote（免費 key 存在雲端環境的網路密鑰，代理自動帶上，程式裡不放 key）；有設就自動交叉驗證，沒設就略過。
# 用法：python3 quotes.py [--days 7] [--out closes.csv] [--json]
#   結束碼：0＝沒有到價、2＝至少一條到價（排程可用來決定要不要通知）。
import argparse, csv, json, os, sys, time, urllib.request, datetime as dt
TICKERS=['TSM','MU','NVDA','TSLA','GOOGL','AAPL','SPCX','SOXX']
USE_FINNHUB=False   # 11/12 使用者：第二來源這條路先不要走（key 一直 401）；要恢復改 True
ALERTS=[('MU','>=',770.0,'MU 短期倉碰 $770 → 賣 1 股（賺回 SOXX 虧損）')]   # (代號, 方向, 價位, 要做的事)

def get(url):
    req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
    with urllib.request.urlopen(req,timeout=20) as r: return json.load(r)

def yahoo(sym,days):
    r=get(f'https://query1.finance.yahoo.com/v8/finance/chart/{sym}?range={days}d&interval=1d')['chart']['result'][0]
    m=r['meta']; q=r['indicators']['quote'][0]; reg=m.get('currentTradingPeriod',{}).get('regular',{})
    now=time.time(); live=reg.get('start',0)<=now<reg.get('end',0)          # 盤中：最後一根還不是收盤
    bars=[dict(date=str(dt.datetime.fromtimestamp(t,dt.timezone.utc).date()),high=h,low=l,close=round(c,2))
          for t,h,l,c in zip(r['timestamp'],q['high'],q['low'],q['close']) if c is not None]
    mdate=str(dt.datetime.fromtimestamp(m['regularMarketTime'],dt.timezone.utc).date())
    if not live and (not bars or bars[-1]['date']<mdate):               # 剛收盤時日線最後一根常是空的：用收盤後的報價補上
        r2=lambda v: round(v,2) if v is not None else None
        bars.append(dict(date=mdate,high=r2(m.get('regularMarketDayHigh')),low=r2(m.get('regularMarketDayLow')),close=round(m['regularMarketPrice'],2)))
    return dict(symbol=sym,last=round(m.get('regularMarketPrice'),2),live=live,bars=bars)

def finnhub(sym):
    try: return get(f'https://finnhub.io/api/v1/quote?symbol={sym}')
    except Exception: return None                                            # 沒設 key 或主機沒放行 → 略過

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--days',type=int,default=7); ap.add_argument('--out'); ap.add_argument('--json',action='store_true')
    a=ap.parse_args(); rows=[]; hits=[]
    for s in TICKERS:
        y=yahoo(s,a.days); fin=[b for b in y['bars']][: -1 if y['live'] else None]   # 只有收完的才算收盤
        prev=fin[-1]['close'] if fin else None; f=finnhub(s) if USE_FINNHUB else None; check='—'
        if f and f.get('pc'):                                                  # 交叉驗證：Finnhub 前收 vs Yahoo 最後一根收盤
            ref=fin[-2]['close'] if (not y['live'] and len(fin)>1) else prev
            fv=f['c'] if not y['live'] else f['pc']; yv=prev if not y['live'] else ref
            check='✅' if yv is not None and abs(fv-yv)<=0.02 else f'⚠️ Finnhub {fv}'
        today=y['bars'][-1]; rows.append(dict(symbol=s,last=y['last'],live=y['live'],last_close=prev,last_close_date=fin[-1]['date'] if fin else None,
                     day_high=round(today['high'],2) if today['high'] else None,check=check,closes=fin))
        for tk,op,lv,act in ALERTS:
            if tk==s and ((op=='>=' and (y['last']>=lv or (today['high'] or 0)>=lv)) or (op=='<=' and (y['last']<=lv or (today['low'] or 9e9)<=lv))):
                hits.append(dict(symbol=s,level=lv,last=y['last'],day_high=today['high'],action=act))
    if a.out:                                                                  # 匯出：每檔每天一列，重跑會去重
        old={}
        if os.path.exists(a.out):
            with open(a.out,encoding='utf-8') as fh: old={(r['date'],r['symbol']):r for r in csv.DictReader(fh)}
        for r in rows:
            for b in r['closes']: old[(b['date'],r['symbol'])]=dict(date=b['date'],symbol=r['symbol'],close=b['close'],source='yahoo',verified=r['check'] if b is r['closes'][-1] else '')
        with open(a.out,'w',newline='',encoding='utf-8') as fh:
            w=csv.DictWriter(fh,fieldnames=['date','symbol','close','source','verified']); w.writeheader(); w.writerows(sorted(old.values(),key=lambda r:(r['date'],r['symbol'])))
    if a.json: print(json.dumps(dict(rows=[{k:v for k,v in r.items() if k!='closes'} for r in rows],alerts=hits),ensure_ascii=False))
    else:
        for r in rows: print(f"{r['symbol']:5} 現價 {r['last']:>8}{'（盤中）' if r['live'] else '（收盤）'}  最近收盤 {r['last_close']}（{r['last_close_date']}）  第二來源 {r['check']}")
        for h in hits: print(f"🔔 到價：{h['symbol']} 現價 {h['last']}／今日高 {h['day_high']} ≥ {h['level']} → {h['action']}")
    sys.exit(2 if hits else 0)
main()
