#!/usr/bin/env python3
"""員工現增認股：結算日情境試算（P/E × 前瞻 EPS + 已領股利）。

用法：python3 scenario.py [config.json]
不帶參數時使用下方 DEFAULT（2026-10-09 版 2890 永豐金）。
所有假設都放在 config，換股票／換年度只改 JSON，不改程式。
"""
import json
import sys

DEFAULT = {
    "ticker": "2890 永豐金",
    "shares": 3000,
    "cost_per_share": 35.15,
    "spot_price": 44.05,          # 查證日收盤（除權後）
    "spot_date": "2026-10-08",
    # 稀釋後 EPS 路徑（年度）。Base 參考凱基 2.74／統一 2.62 再乘現增稀釋 ~0.958
    "eps": {
        "bear": {"2027": 2.20, "2028": 2.10, "2029": 2.20},
        "base": {"2027": 2.55, "2028": 2.65, "2029": 2.75},
        "bull": {"2027": 2.85, "2028": 3.00, "2029": 3.15},
    },
    "pe": {"bear": 12, "base": 15, "bull": 17},
    # 每股現金股利（除息年 → 金額）；2027 年發的是 2026 年盈餘
    "dividends": {
        "bear": {"2027": 1.65, "2028": 1.45},
        "base": {"2027": 1.75, "2028": 1.70},
        "bull": {"2027": 1.85, "2028": 2.00},
    },
    # 結算點：前瞻 EPS 權重（年度: 權重）＋ 截至該日已除息的年度
    "settlements": {
        "2027-12": {"fwd": {"2028": 1.0}, "divs": ["2027"]},
        "2028-07": {"fwd": {"2028": 0.5, "2029": 0.5}, "divs": ["2027", "2028"]},
        "2028-12": {"fwd": {"2029": 1.0}, "divs": ["2027", "2028"]},
    },
}


def run(cfg):
    sh, cost = cfg["shares"], cfg["cost_per_share"]
    print(f"{cfg['ticker']}｜{sh} 股 @ {cost}｜成本 {sh * cost:,.0f}")
    print(f"現價 {cfg['spot_price']}（{cfg['spot_date']}）→ 帳面 "
          f"{(cfg['spot_price'] - cost) * sh:+,.0f}\n")
    print(f"{'結算點':<8}{'情境':<6}{'前瞻EPS':>8}{'P/E':>5}{'股價':>8}"
          f"{'價差':>10}{'累計股利':>10}{'總報酬':>10}{'報酬率':>8}")
    for when, s in cfg["settlements"].items():
        for sc in ("bear", "base", "bull"):
            eps = sum(cfg["eps"][sc][y] * w for y, w in s["fwd"].items())
            px = eps * cfg["pe"][sc]
            gain = (px - cost) * sh
            div = sum(cfg["dividends"][sc][y] for y in s["divs"]) * sh
            tot = gain + div
            print(f"{when:<10}{sc:<7}{eps:>8.2f}{cfg['pe'][sc]:>5}{px:>8.2f}"
                  f"{gain:>+10,.0f}{div:>10,.0f}{tot:>+10,.0f}{tot / (sh * cost):>+8.1%}")
        print()
    # 損益兩平：只靠股利時，股價最低可跌到多少
    for when, s in cfg["settlements"].items():
        d = sum(cfg["dividends"]["base"][y] for y in s["divs"])
        print(f"{when} 損益兩平股價（Base 股利 {d:.2f}）：{cost - d:.2f}")


if __name__ == "__main__":
    cfg = DEFAULT
    if len(sys.argv) > 1:
        with open(sys.argv[1], encoding="utf-8") as f:
            cfg = json.load(f)
    run(cfg)
