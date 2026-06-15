---
title: 財政部財政資訊中心 (MOF Fiscal Information Center)
created: 2026-06-15
updated: 2026-06-15
type: entity
tags: [org, regulation, e-invoice]
sources: [raw/papers/einvoice-barcode-spec.md]
confidence: high
---

# 財政部財政資訊中心 (MOF Fiscal Information Center)

## 概述
中華民國財政部下轄之資訊中心，為電子發票相關規格與平台之主管機關，
發布 [[einvoice-barcode-spec]] (電子發票證明聯一維及二維條碼規格說明)。

## 關鍵事實
- 發布《電子發票證明聯一維及二維條碼規格說明》，現行版本 **v1.8 (2018/08/22)**，初版 2011/11/29。^[raw/papers/einvoice-barcode-spec.md]
- 規格配合《統一發票使用辦法》第 9 條修正，並納入境外電商營業人應記載事項。
- 營運**電子發票整合服務平台**：提供「密碼及種子管理 (QRCode)」、「QRCode 解密驗證」等功能，供營業人設定加密種子密碼、產製與驗證 AES 金鑰。
- 提供多語言加密元件 (VB、.NET、Windows Visual C/C++、JAVA、Linux) 及參考用原始碼 (C#)，協助營業人系統建置。

## 與其他實體的關係
- 主管並發布 [[einvoice-barcode-spec]]
- 規範對象為開立電子發票之營業人，包括 [[taiwan-mobile]] 等企業 (合規關係)
