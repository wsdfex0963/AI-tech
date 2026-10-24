# 情境推估模型（§1-10）：中性＝年化約 10%，樂觀／悲觀＝中性 ±1 個標準差（年化波動為假設值）。
# 用法：改 base、dates、H（股數、均價、成本、起點價、波動）後執行 python3 scenario_model.py，輸出 out.json 與逐檔表。
# 2026-10-21 第一次使用：起點＝10/21 盤中券商截圖價；SOXX 11/5 起 3 拆 1，輸出另列拆後價。
# 2026-10-24 第二次：起點改 10/23 收盤（券商 10/24 庫存截圖「市值÷股數」，6 檔與公開收盤一致）。
import math, json, datetime as dt
base=dt.date(2026,10,23)
dates=[dt.date(2026,12,1),dt.date(2027,3,1),dt.date(2027,7,1)]
MU_DRIFT=math.log(1.10)   # 中性：年化約 10%（長期大盤平均量級），不替任何一檔加戲
# ticker, shares, avg, cost, base price (10/23 收盤，券商截圖), 假設年化波動
H=[('TSM',22,383.11,8428.47,418.51,0.40),('MU',4,950.78,3803.12,877.55,0.55),('NVDA',11,181.43,1995.75,210.96,0.45),
   ('TSLA',6,344.90,2069.38,372.22,0.55),('GOOGL',4,311.15,1244.60,320.21,0.30),('AAPL',3,269.57,808.70,347.7267,0.25),
   ('SPCX',5,152.57,762.85,147.49,0.70),('SOXX',1,511.44,511.44,478.20,0.40)]
COST=sum(h[3] for h in H); MV0=sum(h[1]*h[4] for h in H)
# 規則（地板／停利），SOXX 用拆股前價格比較
rules={'TSM':[('floor',320,'長抱倉 $320 破→執行'),('floor',400,'戰術倉 $400 破→減2股')],'MU':[('floor',810,'$810 破→減1股'),('tp',1150,'$1,150→減1股'),('tp',1250,'$1,250→減1股')],
 'NVDA':[('floor',180,'$180 破→全出')],'TSLA':[('floor',280,'$280 破'),('tp',420,'$420 停利')],'GOOGL':[('floor',290,'$290 破'),('tp',400,'$400 停利')],
 'AAPL':[('floor',220,'$220 破'),('tp',360,'$360→減1股')],'SPCX':[('floor',110,'$110 破→減1股')],'SOXX':[('floor',460,'$460（拆股後 $153.33）破→全出')]}
out={'cost':COST,'mv0':MV0,'rows':[],'tot':{}}
for d in dates:
    t=(d-base).days/365
    for sc,z in (('樂觀',1),('中性',0),('悲觀',-1)):
        tot=0
        for tk,n,a,c,p0,s in H:
            p=p0*math.exp(MU_DRIFT*t+z*s*math.sqrt(t))
            tot+=n*p
            hits=[lab for k,lv,lab in rules[tk] if (k=='floor' and p<lv) or (k=='tp' and p>=lv)]
            out['rows'].append(dict(date=str(d),t=round(t,3),sc=sc,tk=tk,px=round(p,2),px_split=round(p/3,2) if tk=='SOXX' else None,
                                    ret_cost=round((p/a-1)*100,1),chg=round((p/p0-1)*100,1),hits=hits))
        out['tot'][f'{d}|{sc}']=dict(mv=round(tot,2),pl=round(tot-COST,2),ret=round((tot/COST-1)*100,1),chg=round((tot/MV0-1)*100,1))
json.dump(out,open('out.json','w'),ensure_ascii=False,indent=1)
print('cost',round(COST,2),'mv0',round(MV0,2),f'{(MV0/COST-1)*100:.2f}%')
for k,v in out['tot'].items(): print(k,v)
for d in dates:
    print('\n',d)
    for tk in [h[0] for h in H]:
        r={x['sc']:x for x in out['rows'] if x['date']==str(d) and x['tk']==tk}
        print(f"{tk:5}", ' | '.join(f"{sc} {r[sc]['px']:>8.2f} ({r[sc]['chg']:+.1f}% / 成本{r[sc]['ret_cost']:+.1f}%) {','.join(r[sc]['hits'])}" for sc in ('樂觀','中性','悲觀')))
