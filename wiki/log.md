# Wiki Log

> 所有 wiki 動作的時序記錄。僅附加 (append-only)。
> 格式: `## [YYYY-MM-DD] action | subject`
> Actions: ingest, update, query, lint, create, archive, delete
> 超過 500 筆時輪替: 改名為 log-YYYY.md，重新開始。

## [2026-06-15] create | Wiki initialized
- Domain: 企業營運與治理 (Enterprise Operations & Governance)
- Page language: 繁體中文 (Traditional Chinese)
- Location: ./wiki (in repo LLM-Wiki-Claude-Multimodal)
- Structure created: SCHEMA.md, index.md, log.md, raw/{articles,papers,transcripts,assets}, entities/, concepts/, comparisons/, queries/, .llm-wiki/image-caption-cache.json
- Pending ingest sources in Folder/: Data CoE 2025 重點項目.pptx, 採購管理辦法.pdf, 聚焦會議場景統整.xlsx, 電子發票證明聯一維及二維條碼規格說明.pdf

## [2026-06-15] ingest | 四份來源批次匯入 (Multimodal)
- Toolchain: PyMuPDF + python-pptx + pandas/openpyxl (markitdown/poppler 因 Python 3.9/brew 權限問題改用此組合)
- Raw 轉換 (raw/):
  - raw/papers/procurement-management-policy.md (採購管理辦法.pdf, 16 頁文字)
  - raw/papers/einvoice-barcode-spec.md (電子發票條碼規格.pdf, 17 頁文字 + 6 張去重圖片)
  - raw/articles/data-coe-2025.md (Data CoE 2025.pptx, 單張 SmartArt 文字)
  - raw/articles/meeting-scenarios.md (聚焦會議場景統整.xlsx, 5 工作表轉表格)
- Multimodal: 電子發票 PDF 102 張嵌入圖去重後得 6 張有意義圖 (1D/2D 條碼範例、AES 金鑰流程圖、線上解碼工具)；全部由 agent 親自看圖產生繁中 caption 並寫入 .llm-wiki/image-caption-cache.json (6 entries)
- 採購 PDF 之 105 張「圖片」為字型字元碎片 (noise)，已略過
- Wiki 頁面建立 (8):
  - entities/: taiwan-mobile, procurement-department, mof-fiscal-information-center, data-coe
  - concepts/: procurement-management-policy, einvoice-barcode-spec, data-coe-2025-priorities, ai-agent-meeting-scenarios
- 交叉連結重點: 請購小幫手 (meeting-scenarios) ↔ procurement-management-policy；AI 面試官 ↔ data-coe-2025-priorities；taiwan-mobile 為樞紐
- index.md 更新: Total pages 0 → 8

## [2026-06-15] lint | 0 issues found
- 8 pages: broken links 0, orphans 0, frontmatter issues 0, pages-missing-from-index 0
- media: 6/6 asset files present and referenced, no empty-alt captions

## [2026-06-15] archive | Folder/ 原始檔歸檔至 raw/
- 4 份原始二進位檔以 byte-identical (sha256 比對通過) 複製至 raw/，與其轉換後 .md 同目錄同 slug:
  - raw/papers/procurement-management-policy.pdf
  - raw/papers/einvoice-barcode-spec.pdf
  - raw/articles/data-coe-2025.pptx
  - raw/articles/meeting-scenarios.xlsx
- 各 .md frontmatter 之 source_file 改指向 raw/ 永久路徑，並新增 original_filename 保留原檔名 (body sha 不變)
- 原 Folder/ 內 4 檔已刪除，空目錄 Folder/ 已移除 (位元組已保存於 raw/)
