---
title: 電子發票證明聯一維及二維條碼規格 (E-Invoice Barcode Spec)
created: 2026-06-15
updated: 2026-06-15
type: concept
tags: [e-invoice, barcode-spec, tax, regulation]
sources: [raw/papers/einvoice-barcode-spec.md]
confidence: high
---

# 電子發票證明聯一維及二維條碼規格

由 [[mof-fiscal-information-center]] 發布之國家標準，規範電子發票證明聯上
一維與二維條碼之編碼方式。版本 **v1.8 (2018/08/22)**。營業人 (如 [[taiwan-mobile]]) 開立電子發票須遵循本規格。

## 一維條碼規格
- **用途**：兌領獎時輸入使用。
- **格式**：三九碼 (**Code 39**)，共 **19 碼** = 發票年期別 (5) + 發票字軌號碼 (10) + 隨機碼 (4)。
- 發票年期別 = 民國年 3 碼 + 雙數月份期別 2 碼 (例：104 年 3-4 月 → `10404`)。
- 範例：`*10404UZ176908720122*`

![一維條碼發票範例](raw/assets/einvoice-barcode-spec/img-1.png)

## 二維條碼規格 (國內營業人)
- **用途**：行動應用讀取發票資訊與防偽。
- **格式**：**QR Code 兩個**，左右並列、上緣對齊、大小一致；編碼區長寬各 ≥1.5 公分，周圍留白 ≥0.2 公分。左方至少 **QR Code V6 (41x41)**、容錯 **Level L (7%)**。
- **左方 QR (前 77 碼)**：發票字軌號碼(10) + 開立日期(7) + 隨機碼(4) + 銷售額(8,十六進位) + 總計額(8,十六進位) + 買方統編(8) + 賣方統編(8) + **加密驗證資訊(24)**。
- **加密驗證資訊**：將「字軌號碼+隨機碼」以 **AES 加密 + Base64 編碼**，共 24 碼 (詳見下方加密流程)。
- 77 碼後以冒號 `:` 分隔延伸欄位：營業人自行使用區(10) → 完整品目筆數 → 總品目筆數 → **中文編碼參數**(0=Big5 / 1=UTF-8 / 2=Base64) → 品名 → 數量 → 單價 → 補充說明。不敷記載則延伸至右方。
- **右方 QR**：固定以 `**` 起始符號開頭，接續左方未盡資訊。

![二維條碼範例 (Big5)](raw/assets/einvoice-barcode-spec/img-2.png)
![二維條碼範例 (UTF-8)](raw/assets/einvoice-barcode-spec/img-3.png)
![二維條碼範例 (Base64)](raw/assets/einvoice-barcode-spec/img-4.png)

## 境外電商營業人規格
銷售額/總計額固定以 `00000000` 記載；中文編碼參數值為 **3 (UTF-8)**；
新增 10 碼境外電商銷售額/總計額欄位 (8 碼整數 + 2 碼小數，分別轉十六進位)。

## 加密流程與金鑰管理
1. 營業人於 [[mof-fiscal-information-center]] 之**電子發票整合服務平台**設定加密種子密碼 (pwd1)。
2. 於本地端以 **AES 金鑰產生工具**將 pwd1 產出加密金鑰 **Key1 (Hex)**。
3. 以 Key1 搭配公開之 **AES 演算法**產製 24 碼加密驗證資訊。

此設計使金鑰不需於網路傳遞 (平台與業者各自由 pwd1 推得同一金鑰)，兼顧安全與管理彈性。
建議每 6 個月更換種子密碼並重新產製金鑰。

![產生 QRCode 加密金鑰之作業流程](raw/assets/einvoice-barcode-spec/img-5.png)

## 加密元件與驗證
- 提供 VB / .NET / Windows Visual C/C++ / JAVA / Linux 元件，及 C# 參考原始碼 (`QREncrypter`，RijndaelManaged，KeySize 128，固定 IV `Dt8lyToo17X/XkXaQvihuA==`)。
- 函式 `QRCodeINV(...)` 回應 77 碼字串送印表機；QR Code 圖檔由業者自行產生。
- **上線前自我檢查**：可用線上條碼解碼工具上傳掃描檔，分別以 Linear / QRCode 解碼驗證，並至平台「QRCode 解密驗證」確認。

![線上條碼解碼工具檢查頁面](raw/assets/einvoice-barcode-spec/img-6.png)

## 與其他頁面的關係
- 發布機關：[[mof-fiscal-information-center]]
- 合規對象：營業人 [[taiwan-mobile]]
