# 儀表板產生器 v2（2026-10-30 起）：持倉改用表格（股數＋市值佔比），Artifact 與 Notion 內嵌版都不顯示成本、均價、成交價（使用者 10/30 要求）。
# 用法：在工作資料夾先跑 ../scenario_model.py 產生 out.json，再跑本檔。每期只改「本期資料」區塊（§1-6、§1-9、§1-10、§1-11）。
import os, json, math
HERE=os.path.dirname(os.path.abspath(__file__))
head_art=open(os.path.join(HERE,'head_art.html'),encoding='utf-8').read()   # Artifact 版：可用 Google Fonts、亮暗主題
head_nb=open(os.path.join(HERE,'head_nb.html'),encoding='utf-8').read()     # Notion 內嵌版：不得有外部連結
F=json.load(open('out.json',encoding='utf-8'))

# ================= 本期資料（每期改這裡） =================
META=dict(
  report='2026-11-06', ver='v7.6', basis='11/5 盤中', base='2026-11-05',
  out_nb='holdings_dashboard_2026-11-05_v17.html',
  h1='11/5 盤中｜AI 晶片崩盤，組合轉虧；NVDA 離 $180 地板 1.6%',
  conclusion='今天費半盤中約 −11%，組合由賺轉虧 −8.4%。<b>最急：NVDA 今天收盤若 &lt;$180 → 11 股全出</b>；SOXX 剩 1 股、TSM 戰術倉、MU 的地板都已經破了還沒賣。短期目標：MU 新買那 1 股賣在 $770，賺回 SOXX 兩股虧的約 $72。',
  mv_sub='起點 10/28 以來：行情 −$4,083、新投入 $997',
  ret_sub='10/30 收盤 +3.88%',
  pending=('3 筆','SOXX 1 股、TSM 戰術 2 股、MU 減 1 股（待裁示）；NVDA 看今天收盤'),
  disc=('5 / 22','22 筆：5 執行・6 反向・7 裁示不執行・4 未執行'),
  hold_note='半導體 71.3%；MU 5 股超過 4 股上限（新那 1 股另記短期倉）。',
  fc_note='<b>起點已經在 MU、SOXX、TSM 戰術倉的地板下面，NVDA 也只差 1.6%，所以悲觀路一開始就碰一排地板。</b>',
)
# ticker, 股數, 現價, 成本（只用來算總報酬與賺賠檔數，不顯示）, 顏色
H=[('TSM',22,357.035,8428.47,'#2c6f92'),('MU',5,683.18,4499.42,'#b5711f'),('TSLA',6,341.48,2069.38,'#c23c2d'),
   ('NVDA',11,182.93,1995.75,'#22857f'),('GOOGL',6,284.4717,1814.04,'#54529c'),('AAPL',3,344.27,808.70,'#707a86'),
   ('SPCX',5,123.056,762.85,'#8a6bb0'),('SOXX',1,134.02,170.48,'#5e7d2a')]
EXPECT_MV=18820.72   # 截圖市值加總，驗算用
SEMI=('TSM','MU','NVDA','SOXX'); MUSK=('TSLA','SPCX')
ALERTS=[('alertbar','🔴 <b>NVDA $182.93，離 $180 地板只剩 1.6%</b>——今天收盤若 &lt;$180 → 照 10/21 定案 11 股全出（明天美股盤中）。今天 AI 晶片股崩盤（費半盤中約 −11%、NVDA 約 −8%）：民主黨大勝後的 AI 監管疑慮，加上記憶體股被中國 CXMT 消息打到最多 −20%。'),
        ('alertbar','🔴 <b>三條地板已經破了還沒賣</b>：SOXX 剩 1 股（拆股後 $153.33 已破；今天賣了 2 股）；TSM 戰術倉 2 股（11/2 收 $398.63 破 $400，現 $357）；MU（$810 已破，規則減 1 股）。另外 MU 今天加 1 股 → 5 股，超過 4 股上限、也買在地板下 → 記<b>反向執行</b>，那 1 股另記成短期倉（見下方）。')]
LIGHTS=[('red','NVDA','$182.93（今天約 −8%）；<b>離 $180 地板 1.6%</b>','跌破 $180 收盤 → 全出（11 股）'),
        ('red','MU','$683.18；帳上 −24%；<b>已在 $810 地板下</b>；5 股超過上限','減1股（待裁示）'),
        ('red','TSM','$357.04；戰術倉已破 $400（−19.9%）；長抱倉離 $320 地板 10.4%','減2股（戰術倉）'),
        ('red','SOXX','$134.02（拆股後）；<b>已破 $153.33</b>；今天賣 2 股、剩 1 股','全出（剩 1 股）'),
        ('amber','SPCX','$123.06；帳上 −19.3%；離 $110 地板 10.6%','不動'),
        ('amber','GOOGL','$284.47；觀察案：離 ① $306.18 7.6%、離 ② $260 8.6%','觀察案・禁加碼'),
        ('amber','TSLA','$341.48；帳上 −1.0%；離 $280 地板 18.0%','不動'),
        ('green','AAPL','$344.27；帳上 +27.7%；離 $360 停利 4.6%','續抱')]
NW=' style="white-space:nowrap"'
THESIS=f"""  <div class="card">
    <h2>短期目標：用 MU 賺回 SOXX 兩股的虧損（約 $72）</h2>
    <div class="small" style="margin-top:0">做法：11/5 新買的那 1 股 MU 當「短期倉」，跟原本 4 股分開記（MU 上限 4 股不調高）。三條線先到先做：</div>
    <div class="tblwrap"><table>
      <tr><th>線</th><th>價位</th><th>做什麼</th></tr>
      <tr><td class="ticker"{NW}>🎯 目標</td><td class="tabular"{NW}>$770</td><td>賣這 1 股 → 約 +$73，<b>SOXX 虧損補回</b></td></tr>
      <tr><td class="ticker"{NW}>🛑 停損</td><td class="tabular"{NW}>$625</td><td>賣這 1 股 → 約 −$71</td></tr>
      <tr><td class="ticker"{NW}>⏰ 死線</td><td class="tabular"{NW}>12/4 收盤</td><td>都沒碰 → 12/7 賣掉、回到 4 股（避開 12/9 FOMC 和 12 月中財報）</td></tr>
    </table></div>
    <div class="small">現在 $683.18：離目標 +12.7%、離停損 −8.5%。<b>照 MU 波動粗估：先碰目標約 3 成半、先碰停損約 5 成、到期都沒碰約 2 成</b>——已經比買價低，賠的機率比賺的大。5 股一起看的話 MU 回到約 $698 帳面就有 $72，但 5 股整體還虧約 $1,084。三條線是我訂的預設，可改。</div>
  </div>"""
TODOS=[('🔴 今天收盤看 NVDA $180','收盤 &lt;$180 → 明天（台北 11/6 晚上 10:30 開盤後）11 股全出；先在券商設到價提醒'),
       ('🔴 三筆已破還沒賣：SOXX 1 股、TSM 戰術 2 股、MU 減 1 股','照規則賣；不賣就跟我說，記裁示不執行（TSM 戰術倉是第二次，不能再開觀察案）'),
       ('🎯 MU 短期倉三條線','$770 賣（賺回 SOXX 虧損）／$625 停損／12/4 死線；要改告訴我')]
CAL=[('11/6','<b>收盤＝週報</b>','用收盤價正式重算'),
     ('11/20','<b>GOOGL 觀察案死線</b>','① $306.18／② $260 都沒碰 → 11/23 減 1 股')]
DISC=[('7/23','MU $950 減碼窗口','fail','未執行','隔日跌回，吃虧'),
      ('8/5','SPCX 破 $110 地板','fail','未執行','後反彈，幸運'),
      ('8/8','PLTR $180 停利','ok','✅ 已執行','8/27 結案'),
      ('8/15','NFLX $75–80 減碼區','ok','✅ 已執行','8/24 全出，結案'),
      ('8/18','SPOT 觸及 $520','ok','✅ 已執行結案','剩下 1 股 10/15 主動出清'),
      ('8/24','TSM 40% 佔比上限','rev','反向執行','規則禁止加碼，實際買了 1 股'),
      ('8/31','SPCX 無條件減 1 股','fail','裁示不執行','10/14 結案'),
      ('9/3','TSLA 觸及 $375','fail','裁示不執行','已結案'),
      ('9/4','SPCX 觸及 $150','fail','裁示不執行','10/14 結案'),
      ('9/25','TSM 觸及 $450 停利','fail','裁示不執行','改掛長抱倉，結案'),
      ('10/6','NVDA 盤中觸及 $240','fail','裁示不執行','10/09 改掛長抱倉，結案'),
      ('10/7','TSM 買 1 股（戰術倉第 1 股）','rev','反向執行','10/09 改規則後轉進戰術倉'),
      ('10/13','MU 買 1 股','ok','✅ 照規則執行','3→4 到上限'),
      ('10/15','TSM 買 1 股（戰術倉第 2 股）','rev','反向執行','成交價已在 $425 地板下方'),
      ('10/15','TSM 戰術倉 $425 收盤破 → 觀察案 → 10/20 ① 成立','fail','裁示不執行','10/24 看多、長期持有；改訂 $400'),
      ('10/29','GOOGL 買 1 股（財報後、地板下）','rev','反向執行','規則：距地板 &lt;5% 不加碼'),
      ('10/29','GOOGL 再買 1 股（第 2 次往下攤平）','rev','反向執行','再往下買＝第 3 次，紀律已破'),
      ('10/29','GOOGL 收 $283.82 破 $290 地板','fail','裁示不執行','觀察案：$306.18／$260／11/20'),
      ('11/2','SOXX $460 收盤破 → 全出','ok','✅ 部分執行','11/5 才賣、只賣 2／3 股，剩 1 股'),
      ('11/2','TSM 戰術倉 $400 收盤破','fail','未執行','待裁示；已是第二次跳過'),
      ('11/4–5','MU $810 地板破 → 減 1 股','fail','未執行','待裁示'),
      ('11/5','MU 加 1 股（超過 4 股上限、地板下）','rev','反向執行','另記短期倉：$770／$625／12/4')]
DISC_NOTE='10/19 新買 SOXX 不進紀律統計；SOXX 11/5 起 3 拆 1（地板 $460 → $153.33）。本頁不顯示成交價。'
FOOT=('<b>資料血緣：</b>股數、市值來自 <b>11/5 盤中券商庫存截圖</b>（美東約 12:0x，8 檔 59 股；個股損益加總＝市值−成本 ✅）；成交：MU 買 1 股、SOXX 賣 2 股（11/5 成交紀錄截圖，書號 00000945、00000955）。SOXX 11/5 起 3 拆 1，股數與地板都用拆股後數字。盤中價只有券商一個來源，收盤後覆蓋。'
      '<b>依你的要求本頁不顯示成本、均價、成交價</b>（完整數字在 Notion）。<br><br>'
      '今天的崩盤：Yahoo、IBTimes、Invezz（費半盤中約 −11%、記憶體股最多 −20%）；原因是民主黨大勝後的 AI 監管疑慮與 CXMT。短期倉機率是用 MU 年化波動 55% 粗估、只看收盤。<br><br>'
      '<span class="warn">本頁為決策框架與資料整理，不構成投資建議。</span>所有停損、停利價都是你自己事先訂的規則，要不要執行由你自己決定。')
NAME={'2026-11-06':'選舉後','2026-12-31':'年底聖誕行情','2027-03-31':'3 月底','2027-06-30':'6 月底'}

# ================= 以下不用改 =================
MV={t:round(n*p,2) for t,n,p,c,col in H}; TOT=round(sum(MV.values()),2); COST=round(sum(h[3] for h in H),2); NSH=sum(h[1] for h in H)
assert abs(TOT-EXPECT_MV)<0.05,(TOT,EXPECT_MV)
PL=TOT-COST; RET=PL/COST*100; pct={t:MV[t]/TOT*100 for t in MV}
win=sum(1 for t,n,p,c,col in H if n*p>=c); lose=len(H)-win
semi=sum(pct[t] for t in SEMI); musk=sum(pct[t] for t in MUSK); tsm30=MV['TSM']*0.3/TOT*100
money=lambda v:('+' if v>=0 else '−')+f'${abs(v):,.0f}'

hold_rows=''
for t,n,p,c,col in sorted(H,key=lambda h:-MV[h[0]]):
    hold_rows+=(f'<tr><td class="ticker"><span style="display:inline-block;width:9px;height:9px;border-radius:50%;background:{col};margin-right:7px"></span>{t}</td>'
                f'<td class="tabular">{n}</td><td><div style="display:flex;align-items:center;gap:8px"><div style="flex:1;min-width:64px;height:10px;background:var(--surface-2);border:1px solid var(--border);border-radius:99px;overflow:hidden"><div style="width:{pct[t]:.1f}%;height:100%;background:{col}"></div></div>'
                f'<span class="tabular" style="min-width:48px;text-align:right">{pct[t]:.1f}%</span></div></td></tr>')
hold_rows+=f'<tr><td class="ticker">合計</td><td class="tabular"><b>{NSH}</b></td><td class="tabular" style="text-align:right"><b>100%</b></td></tr>'

LN={'red':'紅燈','amber':'黃燈','green':'綠燈'}; light_rows=''
for l,t,s,a in LIGHTS:
    cls=' class="neg"' if l=='red' else ''
    light_rows+=f'<tr><td><span class="pill {l}"><span class="dot"></span>{LN[l]}</span></td><td class="ticker">{t}</td><td>{s}</td><td{cls}>{a}</td></tr>'
todo_li=''.join(f'<li><div class="box"></div><div><div><b>{a}</b></div><div class="meta">{b}</div></div></li>' for a,b in TODOS)
cal_li=''.join(f'<li><span class="d">{d}</span><span>{a} <span class="note">{b}</span></span></li>' for d,a,b in CAL)
SN={'ok':'status-ok','fail':'status-fail','rev':'status-rev'}
disc_rows=''.join(f'<tr><td class="tabular">{d}</td><td>{e}</td><td class="{SN[k]}">{r}</td><td class="dim">{n}</td></tr>' for d,e,k,r,n in DISC)
alerts=''.join(f'\n  <div class="{c}">\n    {h}\n  </div>\n' for c,h in ALERTS)

# ---- 三情境推估（§1-10）----
DT=sorted({r['date'] for r in F['rows']}); B0=META['base']; MV0=F['mv0']
SC=[('樂觀','green'),('中性','accent'),('悲觀','red')]
DAYS={B0:0}
for r in F['rows']: DAYS[r['date']]=r['t']*365
DMAX=max(DAYS.values()); X=lambda d:44+DAYS[d]/DMAX*272
vals=[F['tot'][d+'|'+sc]['mv'] for d in DT for sc,_ in SC]+[MV0]
LO=int(math.floor(min(vals)/5000)*5000); HI=int(math.ceil(max(vals)/5000)*5000)
Y=lambda v:180-(v-LO)/(HI-LO)*164
svg=['<svg viewBox="0 0 400 206" width="100%" role="img" aria-label="三情境組合市值走勢" style="display:block;max-width:640px;margin:0 auto">']
for g in range(LO,HI+1,5000):
    svg.append(f'<line x1="44" x2="316" y1="{Y(g):.1f}" y2="{Y(g):.1f}" style="stroke:var(--border)" stroke-width="0.6"/><text x="40" y="{Y(g)+3:.1f}" text-anchor="end" font-size="10" style="fill:var(--text-faint)">{g//1000}k</text>')
for i,d in enumerate([B0]+DT):
    an,dx=('end',4) if i==0 else (('start',1) if i==1 else ('middle',0))
    svg.append(f'<text x="{X(d)+dx:.1f}" y="198" text-anchor="{an}" font-size="10" style="fill:var(--text-dim)">{int(d[5:7])}/{int(d[8:])}</text>')
for sc,col in SC:
    pts=[(X(B0),Y(MV0))]+[(X(d),Y(F['tot'][d+'|'+sc]['mv'])) for d in DT]
    svg.append(f'<polyline points="{" ".join(f"{x:.1f},{y:.1f}" for x,y in pts)}" fill="none" stroke-width="2" style="stroke:var(--{col})"/>')
    svg+=[f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.6" style="fill:var(--{col})"/>' for x,y in pts[1:]]
    e=F['tot'][DT[-1]+'|'+sc]; y=pts[-1][1]
    svg.append(f'<text x="321" y="{y-1:.1f}" font-size="11.5" font-weight="700" style="fill:var(--{col})">${e["mv"]:,.0f}</text><text x="321" y="{y+11:.1f}" font-size="10" style="fill:var(--{col})">{sc} {e["ret"]:+.1f}%</text>')
svg.append(f'<circle cx="44" cy="{Y(MV0):.1f}" r="3" style="fill:var(--text)"/></svg>')
def hits(d,sc):
    h=[r['tk']+' '+x.split('（')[0].split('→')[0].replace(' 破','').replace(' 停利','') for r in F['rows'] if r['date']==d and r['sc']==sc for x in r['hits']]
    return f'<div class="meta">⚑ {"、".join(h)}</div>' if h else '<div class="meta">—</div>'
trs=''
for d in DT:
    trs+=f'<tr><td class="ticker">{int(d[5:7])}/{int(d[8:])}<div class="meta">{d[:4]}・{NAME.get(d,"")}</div></td>'
    for sc,_ in SC:
        x=F['tot'][d+'|'+sc]
        trs+=f'<td><b class="tabular">${x["mv"]:,.0f}</b> <span class="{"pos" if x["ret"]>=0 else "neg"} tabular">{x["ret"]:+.1f}%</span>{hits(d,sc)}</td>'
    trs+='</tr>'
pc=lambda v:'0%' if abs(v)<0.5 else f'{v:+.0f}%'
hdr2='<tr><th>個股</th>'+''.join(f'<th>{int(d[5:7])}/{int(d[8:])}</th>' for d in DT)+'</tr>'
trs2=''
for t,*_ in H:
    trs2+=f'<tr><td class="ticker">{t}</td>'
    for d in DT:
        r={x['sc']:x for x in F['rows'] if x['date']==d and x['tk']==t}; v=r['中性']['chg']
        trs2+=f'<td class="tabular">${r["中性"]["px"]:,.0f} <span class="{"pos" if v>=0 else "neg"}">{pc(v)}</span><div class="meta">{r["悲觀"]["px"]:,.0f}–{r["樂觀"]["px"]:,.0f}</div></td>'
    trs2+='</tr>'
fc=f"""  <div class="card">
    <h2>四個時間點三情境推估（§1-10，從 {META['basis']} ${MV0:,.0f} 出發，全部抱著）</h2>
    {''.join(svg)}
    <div class="tblwrap"><table>
      <tr><th>日期</th><th>樂觀（+1σ）</th><th>中性（年化 10%）</th><th>悲觀（−1σ）</th></tr>
      {trs}
    </table></div>
    <div class="tblwrap"><table>
      {hdr2}
      {trs2}
    </table></div>
    <div class="small">組合格：市值＋對總成本的報酬率；⚑＝那一路會碰到的規則（地板破→減或全出，停利碰到→減）。個股格：中性價＋相對現價的漲跌，下行是悲觀–樂觀區間。<b>不是預測</b>：中性一律年化 10%、樂觀／悲觀＝±1 個標準差（假設波動 AAPL 25%、GOOGL 30%、TSM／SOXX 40%、NVDA 45%、MU／TSLA 55%、SPCX 70%），8 檔假設一起好／一起壞；季節性（選舉、聖誕行情）只當參考、沒放進模型。{META['fc_note']}</div>
  </div>"""

# ---- 目標進度＋複利模式（§1-11）----
G=F['goal']; CP=F['compound']; SP=CP['split']; sd=SP['date']
grow=''
for x in G['rows']:
    d=x['date']; tag=' <span class="dim">預設</span>' if d=='2027-06-30' else ''
    grow+=f'<tr><td class="ticker">{d[:4]}/{int(d[5:7])}/{int(d[8:])}{tag}</td><td class="tabular">${x["lump"]:,}</td><td class="tabular">${x["monthly"]:,} × {x["months"]} 個月</td><td class="tabular">約 {x["p"]}%</td></tr>'
crow=''
for d in DT:
    cs=[x for x in CP['rows'] if x['date']==d]
    crow+=f'<tr><td class="ticker">{int(d[5:7])}/{int(d[8:])}<div class="meta">已投入 ${cs[0]["inv"]:,}</div></td>'
    crow+=''.join(f'<td class="tabular"><b>${x["mv"]:,}</b> <span class="{"pos" if x["ret"]>=0 else "neg"}">{x["ret"]:+.1f}%</span></td>' for x in cs)+'</tr>'
mrow=''.join(f'<tr><td class="ticker">${int(c):,}</td>'+''.join(f'<td class="tabular">{m} 個月</td>' if m else '<td class="tabular">—</td>' for m in ms)+'</tr>' for c,ms in CP['months_to'].items())
goal=f"""  <div class="card">
    <h2>目標 $30,000 進度（起點 {int(G['start_date'][5:7])}/{int(G['start_date'][8:])} 盤中 ${G['start_mv']:,.0f}）</h2>
    <div style="display:flex;flex-wrap:wrap;align-items:baseline;gap:6px 16px"><span class="tabular" style="font-size:28px;font-weight:700;color:var(--accent)">{G['pct']}%</span><span class="tabular">目前 ${G['mv']:,.0f}｜還差 <b>${G['gap']:,.0f}</b>（+{G['gap']/G['mv']*100:.1f}%）</span></div>
    <div style="height:12px;margin:10px 0 6px;background:var(--surface-2);border:1px solid var(--border);border-radius:99px;overflow:hidden"><div style="width:{G['pct']}%;height:100%;background:var(--accent)"></div></div>
    <div class="small" style="margin-top:4px">起點以來：行情 <b>{money(G['market'])}</b>、新投入 <b>${G['new_money']:,.0f}</b>（分開記，才看得出進度是賺來的還是投進來的）</div>
    <div class="tblwrap"><table>
      <tr><th>想在什麼時候到</th><th>現在一次投入</th><th>或每月投入</th><th>只靠行情的機率</th></tr>
      {grow}
    </table></div>
    <h2 style="margin-top:18px">複利模式：全部抱著＋每月投入 ${CP['monthly']:,} 一起滾</h2>
    <div class="tblwrap"><table>
      <tr><th>時間點</th><th>樂觀</th><th>中性</th><th>悲觀</th></tr>
      {crow}
    </table></div>
    <div class="tblwrap"><table>
      <tr><th>每月投入</th><th>樂觀</th><th>中性</th><th>悲觀</th></tr>
      {mrow}
    </table></div>
    <div class="small">上表：市值（括號是對「總成本＋累計投入」的報酬率）。下表：幾個月後到 $30,000（— 表示 10 年內到不了）。複利要時間：{int(sd[5:7])}/{int(sd[8:])} 中性的 ${SP['mv']:,} 裡，投入的錢 ${SP['inv']:,}、原本部位長出約 ${SP['base_growth']:,}、投入的錢長出約 ${SP['contrib_growth']:,}。</div>
    <div class="small">用中性情境（年化 10%）算；悲觀路要投更多。機率是模型粗估（8 檔一起漲跌、組合波動約 {G['sig']*100:.0f}%）。目標日沒定前預設看 2027/6/30，可改。新錢放半導體以外才會降低集中度；財報前 14 天不加碼。</div>
  </div>"""

EXTRA_CSS='<style>.meta{color:var(--text-dim);font-size:12px;margin-top:2px}</style>'
body=f"""{EXTRA_CSS}
<div class="page">

  <div class="header">
    <div>
      <div class="eyebrow">個人化投資儀表板 · AI 科技核心股</div>
      <h1>{META['h1']}</h1>
    </div>
    <div class="datebadge">報告日 {META['report']}（{META['ver']}）｜股價 {META['basis']}｜{NSH} 股</div>
  </div>

  <div class="conclusion">
    🎯 <b>一句話結論：</b>{META['conclusion']}
  </div>
{alerts}
  <div class="stats">
    <div class="stat"><div class="label">總市值</div><div class="value tabular">${TOT:,.2f}</div><div class="sub tabular">{META['mv_sub']}</div></div>
    <div class="stat"><div class="label">未實現報酬率</div><div class="value tabular {'pos' if RET>=0 else 'neg'}">{RET:+.2f}%</div><div class="sub tabular">{money(PL)}；{META['ret_sub']}</div></div>
    <div class="stat"><div class="label">待執行動作</div><div class="value tabular">{META['pending'][0]}</div><div class="sub">{META['pending'][1]}</div></div>
    <div class="stat"><div class="label">本季紀律達成率</div><div class="value tabular neg">{META['disc'][0]}</div><div class="sub">{META['disc'][1]}</div></div>
  </div>

{goal}

  <div class="grid2">
    <div class="card">
      <h2>持倉佔比（市值加權）</h2>
      <div class="tblwrap"><table>
        <tr><th>個股</th><th>股數</th><th>佔比</th></tr>
        {hold_rows}
      </table></div>
      <div class="small"><b>{win} 檔賺、{lose} 檔虧</b>｜半導體（含 SOXX）{semi:.1f}%｜Musk 因子 {musk:.1f}%｜TSM 跌 30% → 整個組合 −{tsm30:.1f}%<br>{META['hold_note']}<br>佔比用市值算，股數只是對照、不是權重；依你的要求不顯示成本與均價。</div>
    </div>

    <div class="card">
      <h2>紅綠燈表（{META['basis']}）</h2>
      <div class="tblwrap"><table>
        <tr><th>燈號</th><th>個股</th><th>現況／距離</th><th>動作</th></tr>
        {light_rows}
      </table></div>
    </div>
  </div>

{THESIS}

  <div class="row2">
    <div class="card"><h2>本週待辦</h2><ul class="todolist">{todo_li}</ul></div>
    <div class="card"><h2>未來 14 天風險日曆</h2><ul class="cal">{cal_li}</ul></div>
  </div>

{fc}

  <div class="card">
    <h2>紀律追蹤（本季累計）</h2>
    <div class="tblwrap"><table class="disc">
      <tr><th>日期</th><th>觸發事件</th><th>結果</th><th>事後備註</th></tr>
      {disc_rows}
    </table></div>
    <div class="small">{DISC_NOTE}</div>
  </div>

  <div class="footnote">{FOOT}</div>

</div>
</body></html>"""
open('dashboard.html','w',encoding='utf-8').write(head_art+body)
open(META['out_nb'],'w',encoding='utf-8').write(head_nb+body)
print('ok',TOT,f'{RET:.2f}%',{t:round(pct[t],1) for t in pct},'semi',round(semi,1),'musk',round(musk,1),'tsm30',round(tsm30,1),win,lose)
