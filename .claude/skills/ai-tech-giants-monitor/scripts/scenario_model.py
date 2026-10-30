# 情境推估模型（§1-10）：中性＝年化約 10%，樂觀／悲觀＝中性 ±1 個標準差（年化波動為假設值）。
# 用法：改 base、dates、H（股數、均價、成本、起點價、波動）後執行 python3 scenario_model.py，輸出 out.json 與逐檔表。
# 2026-10-21 第一次使用：起點＝10/21 盤中券商截圖價；SOXX 11/5 起 3 拆 1，輸出另列拆後價。
# 2026-10-24 第二次：起點改 10/23 收盤（券商 10/24 庫存截圖「市值÷股數」，6 檔與公開收盤一致）。
# 2026-10-30 第五次：起點＝10/30 收盤（TSM、MU、SPCX 已驗證；NVDA、TSLA、AAPL、GOOGL、SOXX 推算值）。
# 2026-10-29 第四次：起點＝10/29 盤中截圖（GOOGL 10/29 買 2 股 @285.88、@283.10 後 6 股；美東 13:4x 截圖）；加「複利模式」＝全部抱著＋每月固定投入一起滾。
# 2026-10-28 第三次：起點＝10/28 盤中券商截圖；時間點改成使用者指定的「選舉後／年底／3 月底／6 月底」。
import math, json, datetime as dt
base=dt.date(2026,10,30)
dates=[dt.date(2026,11,6),dt.date(2026,12,31),dt.date(2027,3,31),dt.date(2027,6,30)]  # 期中選舉 11/3 後第一個週五／年底／3 月底／6 月底
MU_DRIFT=math.log(1.10)   # 中性：年化約 10%（長期大盤平均量級），不替任何一檔加戲
# ticker, shares, avg, cost, base price (10/30 收盤), 假設年化波動
H=[('TSM',22,383.11,8428.47,406.13,0.40),('MU',4,950.78,3803.12,884.74,0.55),('NVDA',11,181.43,1995.75,204.71,0.45),
   ('TSLA',6,344.90,2069.38,399.87,0.55),('GOOGL',6,302.41,1814.43,279.84,0.30),('AAPL',3,269.57,808.70,344.63,0.25),
   ('SPCX',5,152.57,762.85,134.72,0.70),('SOXX',1,511.44,511.44,465.82,0.40)]
COST=sum(h[3] for h in H); MV0=sum(h[1]*h[4] for h in H)
# 規則（地板／停利），SOXX 用拆股前價格比較
# GOOGL：10/29 收 $283.82 破 $290、裁示不執行 → 觀察案（② $260 破減 1 股／① $306.18 站回減 1 股）
rules={'TSM':[('floor',320,'長抱倉 $320 破→執行'),('floor',400,'戰術倉 $400 破→減2股')],'MU':[('floor',810,'$810 破→減1股'),('tp',1150,'$1,150→減1股'),('tp',1250,'$1,250→減1股')],
 'NVDA':[('floor',180,'$180 破→全出')],'TSLA':[('floor',280,'$280 破'),('tp',420,'$420 停利')],'GOOGL':[('floor',260,'觀察案 ② $260 破→減1股'),('tp',306.18,'觀察案 ① $306.18→減1股'),('tp',400,'$400 停利')],
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
# 目標進度（§1-11）：起點與「起點後新投入的錢」分開記，進度才追得到是行情賺的還是錢投進來的
TARGET=30000; GOAL_START=(dt.date(2026,10,28),21907.30)   # 10/28 盤中截圖，使用者定目標那天
NEW_MONEY=569.83   # 起點後累計新投入（每期照成交截圖加上買進金額、減掉賣出拿回的錢）；10/29 GOOGL 2 股含費 286.31＋283.52
from statistics import NormalDist
SIG=sum(h[1]*h[4]*h[5] for h in H)/MV0   # 組合波動（市值加權，假設一起漲跌）
g=dict(target=TARGET,start_date=str(GOAL_START[0]),start_mv=GOAL_START[1],mv=round(MV0,2),new_money=NEW_MONEY,
       market=round(MV0-GOAL_START[1]-NEW_MONEY,2),pct=round(MV0/TARGET*100,1),gap=round(TARGET-MV0,2),sig=round(SIG,3),rows=[])
r=1.10**(1/12)-1
for d in (dt.date(2026,12,31),dt.date(2027,3,31),dt.date(2027,6,30),dt.date(2027,12,31)):
    t=(d-base).days/365; gr=math.exp(MU_DRIFT*t); n=max(1,round(t*12)); fv=sum((1+r)**(n-k) for k in range(1,n+1))
    p=1-NormalDist().cdf((math.log(TARGET/MV0)-MU_DRIFT*t)/(SIG*math.sqrt(t)))
    g['rows'].append(dict(date=str(d),lump=round(TARGET/gr-MV0),monthly=round((TARGET-MV0*gr)/fv),months=n,p=round(p*100)))
out['goal']=g
# 複利模式（§1-11）：全部抱著不賣（停利只標 ⚑ 不扣）、每月月底固定投入 MONTHLY、投入的錢跟著同一條情境路徑一起滾
import calendar
MONTHLY=808
def mend(k):
    y,m=base.year+(base.month-1+k)//12,(base.month-1+k)%12+1; return dt.date(y,m,calendar.monthrange(y,m)[1])
pf=lambda t,z: math.exp(MU_DRIFT*t+z*SIG*math.sqrt(max(t,0)))
def cval(T,z,c):
    t=(T-base).days/365; v=MV0*pf(t,z); inv=0; k=1
    while mend(k)<=T:
        s=(mend(k)-base).days/365; v+=c*pf(t,z)/pf(s,z); inv+=c; k+=1
    return v,inv
cp=dict(monthly=MONTHLY,rows=[],months_to={})
for d in dates:
    for sc,z in (('樂觀',1),('中性',0),('悲觀',-1)):
        v,inv=cval(d,z,MONTHLY); cp['rows'].append(dict(date=str(d),sc=sc,mv=round(v),inv=inv,ret=round((v/(COST+inv)-1)*100,1)))
for c in (0,300,500,808,1000):
    res=[]
    for z in (1,0,-1):
        m=next((m for m in range(1,121) if MV0*pf(m/12,z)+sum(c*pf(m/12,z)/pf(k/12,z) for k in range(1,m+1))>=TARGET),None); res.append(m)
    cp['months_to'][c]=res
T=dates[-1]; v,inv=cval(T,0,MONTHLY); bg=MV0*pf((T-base).days/365,0)-MV0
cp['split']=dict(date=str(T),mv=round(v),inv=inv,base_growth=round(bg),contrib_growth=round(v-MV0-bg-inv))
out['compound']=cp
json.dump(out,open('out.json','w'),ensure_ascii=False,indent=1)
print('cost',round(COST,2),'mv0',round(MV0,2),f'{(MV0/COST-1)*100:.2f}%')
for k,v in out['tot'].items(): print(k,v)
for d in dates:
    print('\n',d)
    for tk in [h[0] for h in H]:
        r={x['sc']:x for x in out['rows'] if x['date']==str(d) and x['tk']==tk}
        print(f"{tk:5}", ' | '.join(f"{sc} {r[sc]['px']:>8.2f} ({r[sc]['chg']:+.1f}% / 成本{r[sc]['ret_cost']:+.1f}%) {','.join(r[sc]['hits'])}" for sc in ('樂觀','中性','悲觀')))
