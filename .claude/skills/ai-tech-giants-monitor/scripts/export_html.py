#!/usr/bin/env python3
"""把 Data 型儀表板匯出成「單一 HTML 檔」：頁面（dashboard/index.html）＋六個資料檔＋d3＋亮／暗主題色全部內嵌，
離線、手機、Notion 內嵌都能直接打開。資料檔本來就不含成本與均價，這裡也不會加。

用法：python3 scripts/export_html.py --d3 <d3@7 的 d3.min.js> [--out 輸出路徑]
"""
import argparse, datetime as dt, json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IDS = ['summary', 'holdings', 'scenarios', 'goal_plan', 'compound', 'notes', 'combined']
LIVE = 'https://claude.ai/artifact/FxqXJG1BiFKtkvYwUFeCWw'

LIGHT = '''--color-bg:#fbfaf7;--color-fg:#1f1e1c;--color-fg-muted:#6b6a66;--color-panel:#f3f1ec;--color-border-line:#e2dfd8;
--color-ok:#1a7f4b;--color-warn:#a3620a;--color-bad:#c0392b;--pf-c0:#2f6f95;--pf-c1:#1a7f4b;--pf-c2:#c0392b;
--cds-chart-grid:#ebe8e2;--cds-chart-axis:#b9b5ad;--cds-chart-reference:#8a867e;--cds-text-secondary:#6b6a66;
--cds-surface-popover:#ffffff;--cds-border:#dcd8d0;--cds-shadow-popover:0 4px 16px rgba(0,0,0,.12);'''
DARK = '''--color-bg:#1a1a18;--color-fg:#ecebe7;--color-fg-muted:#a3a19b;--color-panel:#252522;--color-border-line:#3a3935;
--color-ok:#4cc38a;--color-warn:#e0a64a;--color-bad:#ef7b6b;--pf-c0:#6fb3dd;--pf-c1:#4cc38a;--pf-c2:#ef7b6b;
--cds-chart-grid:#33322f;--cds-chart-axis:#5c5a55;--cds-chart-reference:#8f8c85;--cds-text-secondary:#a3a19b;
--cds-surface-popover:#2a2a27;--cds-border:#45433f;--cds-shadow-popover:0 4px 16px rgba(0,0,0,.5);'''
THEME = ''':root{%s
--font-anthropic-sans:"Noto Sans TC","PingFang TC","Microsoft JhengHei",-apple-system,system-ui,sans-serif;
--font-anthropic-serif:"Noto Serif TC","Songti TC",Georgia,serif;
--cds-font-size-caption:12px;--cds-font-size-body:14px;--cds-font-size-heading:17px;--cds-font-size-title:28px;--cds-font-weight-medium:600;
--cds-gap-xs:4px;--cds-gap-sm:8px;--cds-gap-md:12px;--cds-gap-lg:16px;--cds-gap-xl:28px;
--cds-pad-xs:4px;--cds-pad-sm:8px;--cds-pad-md:12px;--cds-pad-lg:16px;--cds-pad-xl:24px;--cds-radius:10px;color-scheme:light dark}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){%s}}
:root[data-theme="dark"]{%s}
html,body{margin:0;background:var(--color-bg);color:var(--color-fg)}
#dash-root{padding:16px 16px 32px}
.pf-export{max-width:60rem;margin:0 auto;padding:0 16px 24px;color:var(--color-fg-muted);font:12px/1.5 var(--font-anthropic-sans)}
.pf-export a{color:inherit}''' % (LIGHT, DARK, DARK)

# 模擬儀表板執行環境：dash.data／onData／draw／colors；先跑 onData（切換隱藏的句子）再畫圖，視窗變寬窄時重畫
SHIM = '''window.dash=(function(){var D=window.__DASH_DATA__,draws={},ons=[];
var api={colors:['var(--pf-c0)','var(--pf-c1)','var(--pf-c2)'],
data:function(id){var d=D[id];return d?{status:'ok',data:d,columns:d[0]?Object.keys(d[0]):[]}:{status:'missing',data:[]};},
onData:function(f){ons.push(f);},draw:function(n,f){if(f)draws[n]=f;},calc:function(){},loader:function(){},refresh:function(){},
params:function(){return {};},setParams:function(){},resetParams:function(){},setLink:function(){}};
function run(){ons.forEach(function(f){f();});Object.keys(draws).forEach(function(n){
document.querySelectorAll('[data-draw="'+n+'"]').forEach(function(el){if(!el.closest('[hidden]'))draws[n](el);});});}
api.__start=function(){run();var t;window.addEventListener('resize',function(){clearTimeout(t);t=setTimeout(run,150);});};
return api;})();'''


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--d3', required=True); ap.add_argument('--out')
    a = ap.parse_args()
    data = {k: json.load(open(f'{ROOT}/dashboard/data/{k}.json', encoding='utf-8')) for k in IDS}
    page = open(f'{ROOT}/dashboard/index.html', encoding='utf-8').read().replace('<meta name="dash-one-writer">\n', '')
    d3 = open(a.d3, encoding='utf-8').read()
    asof = data['summary'][0]['as_of']; now = dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
    blob = json.dumps(data, ensure_ascii=False).replace('</', '<\\/')
    assert '</script' not in d3.lower()
    html = (f'<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1"><title>AI 科技核心股儀表板（{asof}）</title>'
            f'<style>{THEME}</style><script>{d3}</script><script>window.__DASH_DATA__={blob};{SHIM}</script></head>'
            f'<body><div id="dash-root">{page}</div>'
            f'<p class="pf-export">離線版：{asof} 收盤資料，{now} 匯出。線上版（每週更新）：<a href="{LIVE}">{LIVE}</a></p>'
            f'<script>dash.__start();</script></body></html>')
    out = a.out or f'{ROOT}/dashboard/ai-tech-dashboard-{asof}.html'
    open(out, 'w', encoding='utf-8').write(html)
    print(out, f'{len(html.encode()) / 1024:.0f} KB')


if __name__ == '__main__':
    main()
