import math
# 儀表板產生器（§1-9／§1-10／§1-11）。用法：在工作資料夾先跑 ../scenario_model.py 產生 out.json，再跑本檔；
# 每期改 H（股數、均價、現價、成本、顏色、持股說明）、COST、assert 的總市值，以及 body 裡的文字。
import os
HERE=os.path.dirname(os.path.abspath(__file__))
head_art=open(os.path.join(HERE,'head_art.html'),encoding='utf-8').read()   # Artifact 版：可用 Google Fonts、亮暗主題
head_nb=open(os.path.join(HERE,'head_nb.html'),encoding='utf-8').read()     # Notion 內嵌版：不得有外部連結
H=[('TSM',22,383.11,418.51,8428.47,'#2c6f92','長抱 20＋戰術 2；<b>戰術倉 10/24 裁示續抱；新地板 $400（待確認）</b>'),
   ('MU',4,950.78,877.55,3803.12,'#b5711f','4 股上限；離 $810 地板 7.7%；台中工會已簽約'),
   ('NVDA',11,181.43,210.96,1995.75,'#22857f','長抱倉；地板 $180（10/21 定案不收緊）'),
   ('TSLA',6,344.90,372.22,2069.38,'#c23c2d','Q3 EPS 小勝、營業利益 −56%；跟 SPCX 同一個 Musk 因子'),
   ('GOOGL',4,311.15,320.21,1244.60,'#54529c','<b>10/28 財報</b>；本週 −6.0%，離 $290 地板 9.4%'),
   ('AAPL',3,269.57,347.7267,808.70,'#707a86','<b>10/29 財報</b>；<b>離 $360 停利 3.5%（減 1 股）</b>'),
   ('SPCX',5,152.57,147.49,762.85,'#8a6bb0','Q3 首次獲利；10/26 第六批解禁；地板 $110'),
   ('SOXX',1,511.44,478.20,511.44,'#5e7d2a','<b>離 $460 地板 3.8%</b>；11/5 起 3 拆 1（地板→$153.33）')]
COST=19624.31
mvs={t:round(n*p,2) for t,n,a,p,c,col,_ in H}
TOT=round(sum(mvs.values()),2); NSH=sum(h[1] for h in H)
assert abs(TOT-20810.97)<0.01 and NSH==56 and abs(sum(h[4] for h in H)-COST)<0.01
R=103; C=2*math.pi*R
arcs=[];labels=[];cum=0;pcts={}
for t,n,a,p,c,col,_ in H:
    pct=mvs[t]/TOT; L=pct*C; pcts[t]=round(pct*100,1)
    arcs.append(f'<circle r="103" stroke="{col}" stroke-dasharray="{L:.2f} {C-L:.2f}" stroke-dashoffset="{-cum:.2f}"/>')
    mid=(cum+L/2)/C*2*math.pi-math.pi/2; p1=pcts[t]
    fs=10.5 if p1>=5 else 8.5 if p1>=4 else 7.5 if p1>=3 else 6.5 if p1>=2.5 else 6
    labels.append(f'<text x="{R*math.cos(mid):.2f}" y="{R*math.sin(mid)+fs*0.34:.2f}" text-anchor="middle" fill="#fff" font-size="{fs}px" font-family="IBM Plex Mono,monospace">{p1}%</text>')
    cum+=L
print(pcts, round(sum(pcts.values()),1))
rows=''.join(f'<tr><td class="ticker">{t}</td><td class="tabular">{pcts[t]}%</td><td class="tabular">${mvs[t]:,.0f}</td><td>{note}</td><td class="dim tabular">{n}</td><td class="dim tabular">{n/NSH*100:.1f}%</td></tr>' for t,n,a,p,c,col,note in H)

import json
F=json.load(open('out.json',encoding='utf-8'))
DT=sorted({r['date'] for r in F['rows']}); B0='2026-10-28'; NAME={'2026-11-06':'選舉後','2026-12-31':'年底聖誕行情','2027-03-31':'3 月底','2027-06-30':'6 月底'}; SC=[('樂觀','green'),('中性','accent'),('悲觀','red')]
DAYS={B0:0,**{r['date']:r['t']*365 for r in F['rows']}}; DMAX=max(DAYS.values()); MV0=F['mv0']
X=lambda d:44+DAYS[d]/DMAX*272; Y=lambda v:180-(v-15000)/20000*164
svg=['<svg viewBox="0 0 400 206" width="100%" role="img" aria-label="三情境組合市值走勢" style="display:block;max-width:640px;margin:0 auto">']
for g in (15000,20000,25000,30000,35000):
    svg.append(f'<line x1="44" x2="316" y1="{Y(g):.1f}" y2="{Y(g):.1f}" style="stroke:var(--border)" stroke-width="0.6"/><text x="40" y="{Y(g)+3:.1f}" text-anchor="end" font-size="10" style="fill:var(--text-faint)">{g//1000}k</text>')
for i,d in enumerate([B0]+DT):
    an,dx=(('end',4) if i==0 else ('start',1) if i==1 else ('middle',0))
    svg.append(f'<text x="{X(d)+dx:.1f}" y="198" text-anchor="{an}" font-size="10" style="fill:var(--text-dim)">{int(d[5:7])}/{int(d[8:])}</text>')
svg.append(f'<line x1="44" x2="316" y1="{Y(COST):.1f}" y2="{Y(COST):.1f}" stroke-dasharray="4 3" stroke-width="1" style="stroke:var(--text-faint)"/><text x="180" y="{Y(COST)+12:.1f}" font-size="10" style="fill:var(--text-faint)">成本 ${COST:,.0f}</text>')
for sc,col in SC:
    pts=[(X(B0),Y(MV0))]+[(X(d),Y(F['tot'][d+'|'+sc]['mv'])) for d in DT]
    svg.append(f'<polyline points="{" ".join(f"{x:.1f},{y:.1f}" for x,y in pts)}" fill="none" stroke-width="2" style="stroke:var(--{col})"/>')
    svg+= [f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.6" style="fill:var(--{col})"/>' for x,y in pts[1:]]
    e=F['tot'][DT[-1]+'|'+sc]; y=pts[-1][1]
    svg.append(f'<text x="321" y="{y-1:.1f}" font-size="11.5" font-weight="700" style="fill:var(--{col})">${e["mv"]:,.0f}</text><text x="321" y="{y+11:.1f}" font-size="10" style="fill:var(--{col})">{sc} {e["ret"]:+.1f}%</text>')
svg.append(f'<circle cx="44" cy="{Y(MV0):.1f}" r="3" style="fill:var(--text)"/></svg>')
def hits(d,sc):
    h=[f"{r['tk']} {x.split('（')[0].split('→')[0].replace(' 破','').replace(' 停利','')}" for r in F['rows'] if r['date']==d and r['sc']==sc for x in r['hits']]
    return f'<div class="meta">⚑ {"、".join(h)}</div>' if h else '<div class="meta">—</div>'
trs=''.join(f'<tr><td class="ticker">{int(d[5:7])}/{int(d[8:])}<div class="meta">{d[:4]}・{NAME[d]}</div></td>'+''.join(
    f'<td><b class="tabular">${F["tot"][d+"|"+sc]["mv"]:,.0f}</b> <span class="{"pos" if F["tot"][d+"|"+sc]["ret"]>=0 else "neg"} tabular">{F["tot"][d+"|"+sc]["ret"]:+.1f}%</span>{hits(d,sc)}</td>' for sc,_ in SC)+'</tr>' for d in DT)
pc=lambda v:'0%' if abs(v)<0.5 else f'{v:+.0f}%'
def cell(tk,d):
    r={x['sc']:x for x in F['rows'] if x['date']==d and x['tk']==tk}
    return f'<td class="tabular">${r["中性"]["px"]:,.0f} <span class="{"pos" if r["中性"]["ret_cost"]>=0 else "neg"}">{pc(r["中性"]["ret_cost"])}</span><div class="meta">{r["悲觀"]["px"]:,.0f}–{r["樂觀"]["px"]:,.0f}</div></td>'
hdr2='<tr><th>個股</th>'+''.join(f'<th>{int(d[5:7])}/{int(d[8:])}</th>' for d in DT)+'</tr>'
trs2=''.join(f'<tr><td class="ticker">{t}</td>'+''.join(cell(t,d) for d in DT)+'</tr>' for t,*_ in H)
fc=f"""  <div class="card">
    <h2>四個時間點三情境推估（§1-10，從 10/28 盤中 ${MV0:,.0f} 出發，全部抱著）</h2>
    {''.join(svg)}
    <div class="tblwrap"><table>
      <tr><th>日期</th><th>樂觀（+1σ）</th><th>中性（年化 10%）</th><th>悲觀（−1σ）</th></tr>
      {trs}
    </table></div>
    <div class="tblwrap"><table>
      {hdr2}
      {trs2}
    </table></div>
    <div class="small">起點＝10/28 盤中券商截圖（正式收盤數字等 10/30 週報）。組合格：市值＋對成本 ${COST:,.2f} 的報酬率；⚑＝那一路會碰到的規則（地板破→減或全出，停利碰到→減）。個股格：中性價＋對你均價的報酬率，下行是悲觀–樂觀區間（SOXX 用拆股前價格，11/5 後 ÷3）。<b>不是預測</b>：中性一律年化 10%、樂觀／悲觀＝±1 個標準差（假設波動 AAPL 25%、GOOGL 30%、TSM／SOXX 40%、NVDA 45%、MU／TSLA 55%、SPCX 70%），8 檔假設一起好／一起壞。<br><b>季節性只當參考、沒放進模型</b>：期中選舉後 12 個月 S&amp;P 歷史平均約 +15%（1942 年起，Yardeni）、12 月平均 +1.4%（1928 年起）；中性路到年底 +1.7%，跟 11–12 月歷史平均差不多。但這次 Fed 在升息、組合 75% 是半導體，跟歷史平均的環境不一樣。<b>樂觀路 11/6 就碰 TSLA $420、AAPL $360 停利；悲觀路年底碰 TSM 戰術倉 $400、MU $810、SPCX $110、SOXX 地板。</b></div>
  </div>"""

G=F['goal']; grow=''
for x in G['rows']:
    d=x['date']; tag=' <span class="dim">預設</span>' if d=='2027-06-30' else ''
    grow+=f'<tr><td class="ticker">{d[:4]}/{int(d[5:7])}/{int(d[8:])}{tag}</td><td class="tabular">${x["lump"]:,}</td><td class="tabular">${x["monthly"]:,} × {x["months"]} 個月</td><td class="tabular">約 {x["p"]}%</td></tr>'
goal=f"""  <div class="card">
    <h2>目標 $30,000 進度（起點 {G['start_date'][5:7].lstrip('0')}/{G['start_date'][8:]} 盤中 ${G['start_mv']:,.0f}）</h2>
    <div style="display:flex;flex-wrap:wrap;align-items:baseline;gap:6px 16px"><span class="tabular" style="font-size:28px;font-weight:700;color:var(--accent)">{G['pct']}%</span><span class="tabular">目前 ${G['mv']:,.0f}｜還差 <b>${G['gap']:,.0f}</b>（+{G['gap']/G['mv']*100:.1f}%）</span></div>
    <div style="height:12px;margin:10px 0 6px;background:var(--surface-2);border:1px solid var(--border);border-radius:99px;overflow:hidden"><div style="width:{G['pct']}%;height:100%;background:var(--accent)"></div></div>
    <div class="small" style="margin-top:4px">起點以來：行情 <b>{'+' if G['market']>=0 else '−'}${abs(G['market']):,.0f}</b>、新投入 <b>${G['new_money']:,.0f}</b>（分開記，才看得出進度是賺來的還是投進來的）</div>
    <div class="tblwrap"><table>
      <tr><th>想在什麼時候到</th><th>現在一次投入</th><th>或每月投入</th><th>只靠行情的機率</th></tr>
      {grow}
    </table></div>
    <div class="small">用中性情境（年化 10%）算；悲觀路要投更多。機率是模型粗估（8 檔一起漲跌、組合波動約 {G['sig']*100:.0f}%）。目標日沒定前預設看 2027/6/30，可改。新錢放半導體以外才會降低 75% 的集中度；財報前 14 天不加碼。</div>
  </div>"""

I='\n          '
body=f'''<div class="page">

  <div class="header">
    <div>
      <div class="eyebrow">個人化投資儀表板 · AI 科技核心股</div>
      <h1>10/28 盤中 +11.6%｜選舉後・年底・3 月底・6 月底三情境</h1>
    </div>
    <div class="datebadge">報告日 2026-10-28（v6.9）｜10/23 收盤＋10/28 盤中｜56 股</div>
  </div>

  <div class="conclusion">
    🎯 <b>一句話結論：</b>本週沒有要主動下的單，只盯兩條線：<b>TSM 收盤破 $400 → 戰術倉 2 股全出</b>（10/24 裁示不賣，新地板待你確認）；<b>SOXX 收盤破 $460 → 全出</b>（只剩 3.8%）。下週 FOMC＋GOOGL、AAPL 財報，不加碼。
  </div>

  <div class="okbar">
    🕐 <b>10/28 盤中（券商截圖；你確認本週無交易）：市值約 $21,907、+$2,283（+11.63%）</b>，比 10/23 收盤多約 $1,096。TSM $438.50（戰術倉 −1.6%、離 $400 地板 8.8%）、SOXX $516.85（轉賺、離 $460 地板 11.0%）、MU 轉賺；<b>TSLA 離 $420 停利 4.6%、AAPL 離 $360 停利 4.1%</b>。盤中價不改下面的正式市值、圓餅圖和燈號，等 10/30 收盤週報。
  </div>

  <div class="alertbar">
    🔴 <b>TSM 戰術倉 2 股：10/24 裁示不賣（看多、長期持有）→ 觀察案記「裁示不執行」結案。</b>Q3 毛利率 66.4%、Q4 指引上修，論點確實有數字撐；但<b>論點變強不改變已成立的觸發</b>，所以照實記。戰術倉不能轉進長抱倉（轉了雙帳作廢、$450／$490 停利恢復），先補預設地板：<b>收盤破 $400 → 2 股全出</b>（離 4.4%，待你確認）。這是本季第 6 次裁示跳過已成立的觸發、第 2 次發生在虧損部位（這 2 股 −6.1%）。
  </div>

  <div class="alertbar">
    🔴 <b>SOXX 離 $460 地板只剩 3.8%</b>（10/23 收 $478.20；10/22 晶片股大跌那天收 $475.69）。收盤跌破 $460 → 1 股全出。<b>11/5 起 3 拆 1</b>：股數變 3 股、地板同比例變 $153.33。
  </div>

  <div class="stats">
    <div class="stat">
      <div class="label">總市值</div>
      <div class="value tabular">$20,810.97</div>
      <div class="sub tabular">10/16→10/23 市場本身 +$100（+0.5%）；新投入 SOXX $511.44</div>
    </div>
    <div class="stat">
      <div class="label">未實現報酬率</div>
      <div class="value tabular pos">+6.05%</div>
      <div class="sub tabular">+$1,186.66（成本 $19,624.31）；10/16 +5.68%</div>
    </div>
    <div class="stat">
      <div class="label">待執行動作</div>
      <div class="value tabular">0 筆</div>
      <div class="sub">只盯兩條線：TSM 戰術倉 $400、SOXX $460</div>
    </div>
    <div class="stat">
      <div class="label">本季紀律達成率</div>
      <div class="value tabular neg">4 / 15</div>
      <div class="sub">15 筆觸發：4 執行・3 反向・6 裁示不執行・2 未執行</div>
    </div>
  </div>

{goal}

  <div class="grid2">
    <div class="card">
      <h2>持倉佔比（市值加權）</h2>
      <div class="chartwrap">
        <svg width="230" height="230" viewBox="-130 -130 260 260">
          <g transform="rotate(-90)" fill="none" stroke-width="46">
            {I.join(['  '+x for x in arcs]).strip()}
          </g>
          {I.join(labels)}
          <circle r="76" fill="var(--surface)"/>
          <text x="0" y="-10" text-anchor="middle" font-size="21px" font-weight="700" fill="var(--green)">+6.05%</text>
          <text x="0" y="9" text-anchor="middle" font-size="12px" fill="var(--text-dim)">$20,810.97</text>
          <text x="0" y="25" text-anchor="middle" font-size="11px" fill="var(--text-faint)">8檔・市值加權</text>
        </svg>
        <div class="chart-foot"><b>5 檔賺、3 檔虧</b>（MU −7.7%、SOXX −6.5%、SPCX −3.3%）；本週 GOOGL 跌最多（−6.0%）、TSLA 漲最多（+4.9%）<br><span class="dim">半導體（含 SOXX）74.6%｜TSM 跌 30% → 整個組合 −13.3%</span></div>
      </div>
    </div>

    <div class="card">
      <h2>紅綠燈表（10/23 收盤價）</h2>
      <div class="tblwrap">
      <table>
        <tr><th>燈號</th><th>個股</th><th>現況／距離</th><th>動作</th></tr>
        <tr><td><span class="pill red"><span class="dot"></span>紅燈</span></td><td class="ticker">TSM</td><td>$418.51（週 +1.4%）；戰術倉 10/24 裁示續抱，<b>新地板 $400 離 4.4%</b>（待確認）；長抱倉離 $320 地板 23.5%</td><td class="neg">跌破 $400 收盤 → 減2股（戰術倉）</td></tr>
        <tr><td><span class="pill red"><span class="dot"></span>紅燈</span></td><td class="ticker">SOXX</td><td>$478.20；帳上 −6.5%；<b>離 $460 地板 3.8%</b>；11/5 起 3 拆 1</td><td class="neg">跌破 $460 收盤 → 全出</td></tr>
        <tr><td><span class="pill amber"><span class="dot"></span>黃燈</span></td><td class="ticker">MU</td><td>$877.55（週 −0.1%）；帳上 −7.7%；離 $810 地板 7.7%；預估本益比 5.0 倍</td><td>不動</td></tr>
        <tr><td><span class="pill amber"><span class="dot"></span>黃燈</span></td><td class="ticker">GOOGL</td><td>$320.21（週 −6.0%）；離 $290 地板 9.4%；<b>10/28 財報</b></td><td>等財報</td></tr>
        <tr><td><span class="pill amber"><span class="dot"></span>黃燈</span></td><td class="ticker">AAPL</td><td>$347.73（週 +1.2%）；<b>離 $360 停利 3.5%</b>；10/29 財報</td><td>等財報</td></tr>
        <tr><td><span class="pill amber"><span class="dot"></span>黃燈</span></td><td class="ticker">SPCX</td><td>$147.49（週 +1.0%）；離 $110 地板 25.4%；<b>10/26 第六批解禁</b></td><td>不動</td></tr>
        <tr><td><span class="pill green"><span class="dot"></span>綠燈</span></td><td class="ticker">TSLA</td><td>$372.22（週 +4.9%）；離 $280 地板 24.8%；離 $420 停利 12.8%</td><td>續抱</td></tr>
        <tr><td><span class="pill green"><span class="dot"></span>綠燈</span></td><td class="ticker">NVDA</td><td>$210.96（週 −1.5%）；離 $180 地板 14.7%</td><td>長抱・只能減</td></tr>
      </table>
      </div>
    </div>
  </div>

  <div class="card">
    <h2>持倉明細（市值加權，§1-6）</h2>
    <div class="tblwrap">
      <table>
        <tr><th>個股</th><th>佔比</th><th>市值</th><th>持股說明</th><th class="dim">股數</th><th class="dim">股數佔比</th></tr>
        {rows}
      </table>
    </div>
    <div class="small"><b>股數佔比只能拿來對照，不能用在任何規則判斷。</b>TSM 用市值算 {pcts['TSM']}%，用股數算 {22/NSH*100:.1f}%；NVDA 用股數算 {11/NSH*100:.1f}%，市值只佔 {pcts['NVDA']}%。分母（總市值）＝$20,810.97；總股數 56 股（11/5 SOXX 拆股後變 58 股）。</div>
  </div>

  <div class="row2">
    <div class="card">
      <h2>本週待辦</h2>
      <ul class="todolist">
        <li><div class="box"></div><div><div><b>🔴 TSM 戰術倉：確認新地板 $400（收盤破 → 2 股全出）</b></div><div class="meta">10/24 裁示不賣、觀察案結案。想改價位就告訴我，沒回覆就照 $400；建議券商設 $400 到價提醒</div></div></li>
        <li><div class="box"></div><div><div><b>🔴 SOXX：收盤破 $460 → 1 股全出</b></div><div class="meta">只剩 3.8%；建議在券商 App 設 $460 到價提醒。11/5 拆股後地板改看 $153.33</div></div></li>
        <li><div class="box"></div><div><div><b>財報＋FOMC 週：不加碼</b></div><div class="meta">GOOGL 10/28、AAPL 10/29（碰 $360 減 1 股，離 3.5%）；FOMC 10/27–28</div></div></li>
      </ul>
    </div>

    <div class="card">
      <h2>未來 14 天風險日曆</h2>
      <ul class="cal">
        <li><span class="d">10/26</span><span><b>SPCX 第六批解禁</b>（約 3.28 億股）</span></li>
        <li><span class="d">10/27–28</span><span><b>FOMC</b> <span class="note">這次升息機率約 1 成；12 月約 7–8 成</span></span></li>
        <li><span class="d">10/28</span><span><b>GOOGL Q3 財報</b> <span class="note">本週 −6.0%，離 $290 地板 9.4%</span></span></li>
        <li><span class="d">10/29</span><span><b>AAPL Q4 財報</b>（預估）<span class="note">；PCE 物價</span></span></li>
        <li><span class="d">11/3–5</span><span><b>SOXX 3 拆 1</b> <span class="note">11/5 起拆後價；地板 $153.33</span></span></li>
      </ul>
    </div>
  </div>

{fc}

  <div class="card">
    <h2>紀律追蹤（本季累計，10/24 更新）</h2>
    <div class="tblwrap">
    <table class="disc">
      <tr><th>日期</th><th>觸發事件</th><th>結果</th><th>事後備註</th></tr>
      <tr><td class="tabular">7/23</td><td>MU $950 減碼窗口</td><td class="status-fail">未執行</td><td class="dim">隔日跌回，吃虧</td></tr>
      <tr><td class="tabular">8/5</td><td>SPCX 破 $110 地板</td><td class="status-fail">未執行</td><td class="dim">後反彈，幸運</td></tr>
      <tr><td class="tabular">8/8</td><td>PLTR $180 停利</td><td class="status-ok">✅ 已執行</td><td class="dim">8/27 @$185.50 結案</td></tr>
      <tr><td class="tabular">8/15</td><td>NFLX $75–80 減碼區</td><td class="status-ok">✅ 已執行</td><td class="dim">8/24 全出，結案</td></tr>
      <tr><td class="tabular">8/18</td><td>SPOT 觸及 $520</td><td class="status-ok">✅ 已執行結案</td><td class="dim">剩下 1 股 10/15 @$527.10 主動出清</td></tr>
      <tr><td class="tabular">8/24</td><td>TSM 40% 佔比上限</td><td class="status-rev">反向執行</td><td class="dim">規則禁止加碼，實際買了 1 股</td></tr>
      <tr><td class="tabular">8/31</td><td>SPCX 無條件減 1 股</td><td class="status-fail">裁示不執行</td><td class="dim">10/14 結案；10/20 Q3 首次獲利</td></tr>
      <tr><td class="tabular">9/3</td><td>TSLA 觸及 $375</td><td class="status-fail">裁示不執行</td><td class="dim">已結案；10/23 收 $372.22</td></tr>
      <tr><td class="tabular">9/4</td><td>SPCX 觸及 $150</td><td class="status-fail">裁示不執行</td><td class="dim">10/14 結案；10/23 收 $147.49</td></tr>
      <tr><td class="tabular">9/25</td><td>TSM 觸及 $450 停利</td><td class="status-fail">裁示不執行</td><td class="dim">改掛長抱倉，結案</td></tr>
      <tr><td class="tabular">10/6</td><td>NVDA 盤中 $243.37，觸及 $240</td><td class="status-fail">裁示不執行</td><td class="dim">10/09 改掛長抱倉，結案</td></tr>
      <tr><td class="tabular">10/7</td><td>TSM 買 1 股 @$472.65</td><td class="status-rev">反向執行</td><td class="dim">10/09 改規則後轉進戰術倉</td></tr>
      <tr><td class="tabular">10/13</td><td>MU 買 1 股 @$942</td><td class="status-ok">✅ 照規則執行</td><td class="dim">3→4 到上限；10/23 收 $877.55</td></tr>
      <tr><td class="tabular">10/15</td><td>TSM 買 1 股 @$418.15（戰術倉第 2 股）</td><td class="status-rev">反向執行</td><td class="dim">成交價已在 $425 地板下方</td></tr>
      <tr><td class="tabular">10/15</td><td>TSM 戰術倉 $425 收盤破 → 10/17 觀察案 → 10/20 ① 成立</td><td class="status-fail">裁示不執行</td><td class="dim">10/24 看多、長期持有；新地板 $400 待確認</td></tr>
    </table>
    </div>
    <div class="small">10/19 新買 SOXX 不進紀律統計；10/21 三項預設值定案（NVDA 地板不收緊、AAPL $360 減 1 股、SOXX $460／上限 1 股）。</div>
  </div>

  <div class="footnote">
    <b>資料血緣：</b>股數、均價、成本、市值來自<b>10/24 券商庫存截圖</b>（8 檔 56 股；總成本 $19,624.31；個股損益加總 +$1,186.66＝市值−成本 ✅）。<b>你確認本週沒有成交 → TSM 22 股確認；10/24 裁示戰術倉不賣。</b><br><br>
    <b>10/23 收盤價驗證</b>（每檔都用「10/22 收盤＋當天漲跌」串接過）：券商截圖「市值÷股數」有 6 檔跟公開收盤完全一致 → 判定是 10/23 收盤後的截圖：NVDA $210.96、AAPL $347.73、SPCX $147.49（各再加兩個公開來源 ✅）；TSM $418.51、TSLA $372.22、SOXX $478.20（公開來源＋券商 ✅）。<b>MU 券商 $877.55 vs Finviz／TradingKey $883.81 對不上 → 以券商為準、列推算值</b>；GOOGL 券商 $320.21（之前用的 $320.58 是收盤前報價，已更正）。<br><br>
    📐 <b>報酬率 +5.68%（10/16）→ +6.05%</b>：本週新投入 SOXX $511.44（不是賺回來的）；扣掉後<b>市場本身 10/16→10/23 +$100.11（+0.5%）</b>。同期 S&amp;P −0.5%、那斯達克 −0.7%。中間 10/22 晶片股大跌（那指 −2.6%、SOXX 約 −7%），10/23 小幅反彈。佔比四捨五入後加總 {sum(pcts.values()):.1f}%。<br><br>
    <span class="warn">本頁為決策框架與資料整理，不構成投資建議。</span>所有停損、停利價都是你自己事先訂的規則，要不要執行由你自己決定。
  </div>

</div>


</body></html>'''
open('dashboard.html','w',encoding='utf-8').write(head_art+body)
open('holdings_dashboard_2026-10-28_v13.html','w',encoding='utf-8').write(head_nb+body)
print('ok')
