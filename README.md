# hw2_WordCloud
# 程式設計作業 2：自製 Hash Table 文字雲產生器

## 1. 程式說明與設計理念
本程式完全依照要求，**無使用任何內建的 dict 或 collections.Counter 函式庫**。
資料結構部分，我自建了 `CustomHashTable` 類別，使用陣列與子陣列 (Chaining) 來處理 Hash Collision，並手寫了 Selection Sort 進行排序以防違反規定。

## 2. 加分項實作
* **存成圖檔**：介面上設計了 `[SAVE EPS]` 按鈕，透過 Tkinter 的 Canvas 匯出 `.eps` 向量圖檔。
* **Stop Words 排除**：自訂了無意義字詞清單 (如 is, a, the 等)，在讀取時自動略過。
* **中文處理**：利用中文字的 Unicode 範圍 (\u4e00-\u9fff)，搭配 **2-gram (雙字詞) 滑動視窗演算法**，成功擷取出中文的常用兩字詞彙。

## 3. 圖形化介面
使用 `tkinter` 打造，並採用深色底搭配螢光色的「復古像素風格 (Pixel Art)」，字體統一使用 Courier 呈現點陣科技感。