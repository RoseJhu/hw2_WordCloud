**一、開發說明**
：本專案實作之文字雲系統，核心演算法結合了自然語言處理與幾何分佈邏輯。針對**中文語境**採用 `jieba` 斷詞庫進行精確分詞，英文部分則實作字頻統計過濾演算法。文字配置核心採用**阿基米德螺旋演算法（Archimedean spiral）**，搭配 **AABB 碰撞偵測技術**，確保高頻詞彙能由中心向外擴散且視覺上互不重疊。

**二、功能特色**
*   **介面設計**：參考 **Isometric Pixel Art（等距視角像素畫）** 風格調色盤，以橄欖綠、機器人紅與晴空藍等高對比色系，打造具備 90 年代街機感的懷舊視覺體驗。
*   **中英支援**：支援中英文輸入，具備自動過濾「停用詞（Stop words）」功能，剔除無意義之虛詞（如：的、在、is、the），更有效擷取核心關鍵字。
*   **彈性控制**：提供使用者自訂「顯示詞數」功能，並具備一鍵清空（Clear）與剪貼簿貼上（Paste）等按鈕。
*   **圖檔儲存**：支援PNG格式圖檔匯出，另加上可在存取圖片前自行命名等功能，以防多次存取舊圖片被覆蓋。

**三、執行結果過程與圖檔**

執行過程影片：https://drive.google.com/file/d/1iOmb_4P8hdfWzZp_Hftx29ZLKAE8T43m/view?usp=sharing

<img width="600" height="400" alt="travel" src="https://github.com/user-attachments/assets/47b70bef-6bd1-44a6-b993-56a4c08fabdf" />


<img width="600" height="400" alt="pet" src="https://github.com/user-attachments/assets/29e89e44-1120-4bb8-b83d-f9a335e08374" />
