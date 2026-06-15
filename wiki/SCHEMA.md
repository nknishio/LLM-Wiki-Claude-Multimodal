# Wiki Schema

## Domain
企業營運與治理知識庫 (Enterprise Operations & Governance Knowledge Base)。

涵蓋公司內部營運、制度與合規主題，包括但不限於：
- **資料治理 / Data CoE**：資料卓越中心 (Center of Excellence) 的策略、重點項目、組織與里程碑
- **採購管理**：採購制度、辦法、流程、權責與審核層級
- **會議與協作場景**：會議流程、場景統整、協作工具與最佳實務
- **財稅合規**：電子發票、條碼規格、稅務與法規遵循

頁面語言：**繁體中文** (Traditional Chinese)。原始術語保留原文；必要時於括號附英文對照。

## Conventions
- 檔名：小寫、連字號、無空格、無中文字 (e.g. `data-coe-2025.md`, `procurement-policy.md`)。
  中文主題以語意化英文 slug 命名，頁面標題 (`title`) 用中文。
- 每個 wiki 頁面以 YAML frontmatter 開頭 (見下)
- 使用 `[[wikilinks]]` 互相連結 (每頁至少 2 個對外連結)
- 更新頁面時，務必更新 `updated` 日期
- 每個新頁面都要加入 `index.md` 的對應區塊
- 每個動作都要附加到 `log.md`
- **出處標記 (Provenance)**：在綜合 3 個以上來源的頁面，於段落結尾附上
  `^[raw/papers/source-file.md]`，讓讀者可追溯每項論述。單一來源頁面可省略
  (frontmatter 的 `sources:` 已足夠)。

## Frontmatter
```yaml
---
title: 頁面標題 (中文)
created: YYYY-MM-DD
updated: YYYY-MM-DD
type: entity | concept | comparison | query | summary
tags: [取自下方分類法]
sources: [raw/papers/source-name.md]
# 選用的品質訊號:
confidence: high | medium | low        # 論述支持度
contested: true                        # 有未解決的矛盾時設定
contradictions: [other-page-slug]      # 與本頁衝突的頁面
---
```

`confidence` 與 `contested` 為選用但建議。Lint 會列出 `contested: true` 與
`confidence: low` 的頁面供審查，避免薄弱論述悄悄固化為 wiki 既定事實。

### raw/ Frontmatter
原始來源也需要小型 frontmatter，讓再次匯入時可偵測變動：

```yaml
---
source_url: https://example.com/article   # 原始 URL (若有)
source_file: raw/papers/slug.pdf           # 原始二進位檔 (轉換文件用)
converted_from: pdf | pptx | docx | xlsx   # 機器轉換為 MD 時設定
media_dir: raw/assets/slug                 # 擷取圖片子目錄 (若有)
ingested: YYYY-MM-DD
sha256: <轉換後 Markdown 內文的十六進位雜湊>
---
```

對轉換文件，`sha256` 以*轉換後的 Markdown* 內文計算 (frontmatter 之後的全部)，
因為那是 wiki 實際讀取的產物。

## Tag Taxonomy
每頁的每個 tag 都必須出現在此分類法。若需新 tag，先在此新增，再使用。

**資料治理 / Data**: `data-coe`, `data-governance`, `data-strategy`, `analytics`, `data-platform`
**採購 / Procurement**: `procurement`, `policy`, `approval-flow`, `vendor`, `compliance`
**會議與協作 / Collaboration**: `meeting`, `workflow`, `collaboration`, `process`, `tooling`
**財稅 / Finance & Tax**: `e-invoice`, `barcode-spec`, `tax`, `finance`, `regulation`
**組織 / Org**: `org`, `role`, `team`, `person`, `milestone`, `timeline`
**Meta**: `comparison`, `summary`, `controversy`, `open-question`

## Page Thresholds
- **建立頁面**：實體/概念出現在 2+ 來源，或為單一來源的核心主題
- **加入既有頁面**：來源提及已涵蓋的內容
- **不建立頁面**：一筆帶過、次要細節、或領域外主題
- **拆分頁面**：超過 ~200 行時，拆成子主題並交叉連結
- **封存頁面**：內容完全被取代時，移至 `_archive/`，自 index 移除

## Entity Pages
每個重要實體一頁 (人、組織、產品、系統、制度)。包含：
- 概述 / 是什麼
- 關鍵事實與日期
- 與其他實體的關係 ([[wikilinks]])
- 來源參照

## Concept Pages
每個概念或主題一頁。包含：
- 定義 / 說明
- 目前的知識狀態
- 未解問題或爭議
- 相關概念 ([[wikilinks]])

## Comparison Pages
並列分析 (表格優先)。包含：比較對象與原因、比較維度、結論/綜合、來源。

## Update Policy
新資訊與既有內容衝突時：
1. 檢查日期 — 較新來源通常取代較舊者
2. 若確實矛盾，記錄雙方立場、日期與來源
3. 在 frontmatter 標記：`contradictions: [page-name]`
4. 於 lint 報告中標記供使用者審查
