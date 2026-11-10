# 儀表板產生器 v2（2026-10-30 起）：持倉改用表格（股數＋市值佔比），Artifact 與 Notion 內嵌版都不顯示成本、均價、成交價（使用者 10/30 要求）。
# 用法：在工作資料夾先跑 ../scenario_model.py 產生 out.json，再跑本檔。每期只改「本期資料」區塊（§1-6、§1-9、§1-10、§1-11）。
import os, json, math
HERE=os.path.dirname(os.path.abspath(__file__))
head_art=open(os.path.join(HERE,'head_art.html'),encoding='utf-8').read()   # Artifact 版：可用 Google Fonts、亮暗主題
head_nb=open(os.path.join(HERE,'head_nb.html'),encoding='utf-8').read()     # Notion 內嵌版：不得有外部連結
F=json.load(open('out.json',encoding='utf-8'))

# ================= 本期資料（每期改這裡） =================
META=dict(
  report='2026-11-10', ver='v8.3', basis='11/9 收盤', base='2026-11-09',
  out_nb='holdings_dashboard_2026-11-09_v19.html',
  h1='11/9 收盤｜MU 反彈 +6%，短期倉進度一半；NVDA 加 1 股',
  conclusion='組合 −$461（−2.2%），比上週五少虧約 $632。<b>MU 短期倉離 $770 只差 5.0%</b>（那 1 股已賺約 $37，SOXX 虧損補回一半）。NVDA 11/9 加 1 股 → 12 股（核心倉原本只能減不能加，等你決定要不要改規則）。NVDA 11/17 財報。',
  mv_sub='起點 10/28 以來：行情 −$2,816、新投入 $1,175',
  ret_sub='11/6 收盤 −5.32%',
  pending=('0 筆','只盯 MU 短期倉 $770'),
  disc=('—','核心倉；11/9 NVDA 加碼記一筆'),
  hold_note='核心倉只能減不能加（11/9 NVDA 加碼待決定要不要改規則）。',
  fc_note='<b>⚑ 只剩 MU 短期倉 $770。</b>',
)
# ticker, 股數, 現價, 成本（只用來算總報酬與賺賠檔數，不顯示）, 顏色
H=[('TSM',22,388.62,8428.47,'#2c6f92'),('MU',5,733.15,4498.94,'#b5711f'),('TSLA',6,378.05,2069.38,'#c23c2d'),
   ('NVDA',12,178.67,2173.46,'#22857f'),('GOOGL',6,288.15,1814.04,'#54529c'),('AAPL',3,350.69,808.70,'#707a86'),
   ('SPCX',5,142.07,762.85,'#8a6bb0'),('SOXX',1,146.76,170.48,'#5e7d2a')]
EXPECT_MV=20265.81   # 11/9 收盤後券商截圖市值加總，驗算用
SEMI=('TSM','MU','NVDA','SOXX'); MUSK=('TSLA','SPCX')
ALERTS=[('okbar','📈 <b>11/9 反彈</b>：MU +6.3%、SOXX +7.5%、TSLA +5.5%、SPCX +5.8%；NVDA −4.3%（收 $178.67）。組合 −2.2%（上週五 −5.3%）。'),
        ('askbar','🟡 <b>NVDA 11/9 加 1 股 → 12 股</b>：核心倉規則是「只能減不能加」，先記一筆「核心倉加碼」。要不要改規則（允許逢低加碼、設上限），等你決定。')]
LIGHTS=[('amber','MU','$733.15（+6.3%）；論點 ⚠️（CXMT、台積電 3D DRAM 傳聞）；<b>短期倉離 $770 只差 5.0%</b>','核心倉＋短期倉 $770 賣'),
        ('amber','NVDA','$178.67（−4.3%）；<b>11/17 盤後財報</b>；11/9 加 1 股 → 12 股','核心倉・財報前不加'),
        ('amber','GOOGL','$288.15（+1.2%）；雲端 ✅、廣告 ⚠️','核心倉'),
        ('green','TSM','$388.62（+3.5%）；3D DRAM 傳聞待證實','核心倉'),
        ('green','TSLA','$378.05（+5.5%）','核心倉'),
        ('green','AAPL','$350.69（+2.4%）','核心倉'),
        ('green','SPCX','$142.07（+5.8%）；12/8 全數解禁','核心倉'),
        ('green','SOXX','$146.76（+7.5%）','核心倉')]
NW=' style="white-space:nowrap"'
THESIS=f"""  <div class="card">
    <h2>短期目標：用 MU 賺回 SOXX 兩股的虧損（約 $72）</h2>
    <div style="display:flex;flex-wrap:wrap;align-items:baseline;gap:6px 16px"><span class="tabular" style="font-size:28px;font-weight:700;color:var(--accent)">50%</span><span class="tabular">那 1 股已賺約 $37／目標約 $74；現在 $733.15，還差 <b>$36.85（+5.0%）</b></span></div>
    <div style="height:12px;margin:10px 0 6px;background:var(--surface-2);border:1px solid var(--border);border-radius:99px;overflow:hidden"><div style="width:50%;height:100%;background:var(--accent)"></div></div>
    <div class="tblwrap"><table>
      <tr><th>線</th><th>價位</th><th>做什麼</th></tr>
      <tr><td class="ticker"{NW}>🎯 目標</td><td class="tabular"{NW}>$770</td><td>賣這 1 股 → 約 +$74，<b>SOXX 虧損補回</b></td></tr>
    </table></div>
    <div class="small">照 MU 波動粗估：<b>1 個月內收盤碰到 $770 約 66%、3 個月內約 79%</b>。沒有停損。每個交易日收盤後自動檢查一次，盤中即時通知請用 Yahoo 財經 App 價格提醒。</div>
  </div>"""
TODOS=[('🎯 MU 短期倉：碰 $770 就賣 1 股','只差 5%；Yahoo 財經 App 設價格提醒，盤中碰到就通知'),
       ('📝 NVDA 加碼：要不要改規則？','① 照舊（核心倉只能減不能加，記一筆加碼）／② 改成允許逢低加碼、每檔設股數上限'),
       ('🟡 NVDA 11/17 盤後財報','只看論點：資料中心營收、AI 監管影響')]
CAL=[('11/13','<b>收盤＝週報</b>','用 Yahoo 收盤重算'),
     ('11/17','<b>NVDA Q3 財報</b>（盤後）','公司 10/28 公告')]
DISC=[('10/29','GOOGL 買 1 股（財報後、地板下）','rev','反向執行','規則：距地板 &lt;5% 不加碼'),
      ('10/29','GOOGL 再買 1 股（第 2 次往下攤平）','rev','反向執行','再往下買＝第 3 次'),
      ('10/29','GOOGL 收 $283.82 破 $290 地板','fail','裁示不執行','觀察案 11/6 結案（核心倉）'),
      ('11/2','SOXX $460 收盤破 → 全出','ok','✅ 部分執行','11/5 賣 2／3 股，剩 1 股裁示不賣'),
      ('11/2','TSM 戰術倉 $400 收盤破','fail','裁示不執行','11/5 長期持有；第二次跳過'),
      ('11/4','MU $810 收盤破（$795.23）','fail','裁示不執行','11/5 長期持有'),
      ('11/5','MU 加 1 股（超過 4 股上限、地板下）','rev','反向執行','另記短期倉：$770 賣'),
      ('11/9','NVDA 加 1 股（核心倉）','rev','核心倉加碼','規則只能減不能加；待決定要不要改')]
DISC_NOTE='本季 22 筆：5 執行・6 反向・9 裁示不執行・2 未執行（完整紀錄在 Notion 與 skill）。<b>11/6 起全部核心複利倉</b>，之後只記「核心倉加碼」：目前 1 筆（11/9 NVDA）。'
FOOT=('<b>資料血緣：</b>股數、市值來自 <b>11/9 收盤後券商庫存截圖</b>（8 檔 60 股；個股損益加總＝市值−成本 ✅）；成交：NVDA 11/9 買 1 股（成交紀錄截圖，書號 00000354）。'
      '<b>收盤價：Yahoo chart API（scripts/quotes.py）8 檔跟券商截圖完全一致 ✅</b>。本頁不顯示成本、均價、成交價。<br><br>'
      'NVDA 財報 11/17 盤後（公司 10/28 公告）。短期倉機率用 MU 年化波動 55%、只看收盤粗估。<br><br>'
      '<span class="warn">本頁為決策框架與資料整理，不構成投資建議。</span>要不要買賣由你自己決定。')
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
    <h2>三情境推估（§1-10，從 {META['basis']} ${MV0:,.0f} 出發，全部抱著）</h2>
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
