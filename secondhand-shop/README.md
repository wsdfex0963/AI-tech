# 文湖線衣櫥：二手衣拍賣網站

Live 版本：https://claude.ai/artifact/Lvz7zeep5TGeoodQnDnHiv

這個資料夾裡的 `index.html` 是網站的**初始模板**。賣家在後台按「發布到網站」時，頁面會把
資料重新寫進自己的 HTML，產生一個新版本。所以之後上架的商品只存在 live 版本裡，不會回寫到這個 repo。

## 資料流

```
賣家上傳照片 ─► 瀏覽器端處理（不上傳任何伺服器）
                 ├─ 縮圖到最長邊 1000px
                 ├─ 去背：把照片四邊分群出幾種背景色（床單、地板…），從邊緣做 flood fill，
                 │        再修掉細碎毛邊、只保留最大的衣服主體、羽化邊緣
                 ├─ 美化：溫和自動調光（避免改變衣服原色） + 亮度/對比/飽和/色溫
                 └─ 合成 900×900 方圖（背景色 + 陰影）→ WebP（不支援就用 JPEG）
             ─► 草稿 (draft，只有賣家這個分頁看得到)
             ─► 發布：整頁 HTML（CSS + JS + JSON 資料）重新產生 ─► 新版本上線
買家瀏覽 ─► 加入詢問清單 (存在買家自己的瀏覽器) ─► 產生 LINE 訊息 ─► 私訊 wsdfex
```

## 資料模型（`<script id="shop-data">` 裡的 JSON）

| 欄位 | 型別 | 說明 |
|---|---|---|
| `schema` | int | 資料結構版本，目前是 1 |
| `shop.name / tagline / lineId` | string | 店名、介紹、LINE ID |
| `shop.shipNote / payNote / meetNote` | string | 寄貨、付款、面交說明 |
| `seq` | int | 下一個商品流水號（`A` + 3 碼） |
| `publishedAt` | ISO datetime | 最後發布時間 |
| `items[].id` | string | 商品編號，例：`A012`，發出後不重複使用 |
| `items[].title / cat / size / cond` | string | 名稱、分類、尺寸、狀況 |
| `items[].brand / material / note` | string | 品牌、材質、說明與瑕疵 |
| `items[].price / orig` | int | 售價、原價（0 = 不顯示） |
| `items[].measures` | object | 平放實量，key 依分類而定，例：`{"肩寬":"44"}` |
| `items[].status` | enum | `available` 可購買 / `reserved` 保留中 / `sold` 已售出 |
| `items[].photos` | string[] | 處理後的 data URI，第一張是封面；`svg:*` 是範例插圖 |
| `items[].sample` | bool | 範例商品，可在後台一鍵清除 |
| `items[].createdAt / updatedAt / soldAt` | ISO datetime | 上架、更新、售出時間 |
| `log[]` | `{at, action, id, detail}` | 異動紀錄（上架／修改／狀態／刪除），保留最近 300 筆 |

## 限制

- 照片直接存在網頁裡，整頁上限 16 MB，大約可放 100 件以上（每張約 60–120 KB）。後台有容量條。
- 去背用的是顏色規則，不是 AI 模型：淺色、單色背景拍的效果最好。背景很雜的照片可以關掉去背，只做美化。
- iPhone 的 HEIC 照片在部分瀏覽器讀不進來，先轉成 JPG。
