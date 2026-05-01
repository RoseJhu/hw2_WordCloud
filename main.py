import tkinter as tk
from tkinter import messagebox, filedialog
import random
import math
import os
import io
from collections import Counter

# 嘗試載入外部影像處理套件，若環境未安裝則標記為 False
try:
    import jieba
    from PIL import Image, ImageGrab
    HAS_LIBS = True
except ImportError:
    HAS_LIBS = False

# ---------------- 1. 文字處理與頻率計算 (Jieba 專業版) ----------------
def get_top_words(text, top_n):
    """
    處理讀入的文字，進行斷詞、過濾停用詞，並統計出現頻率。
    """
    # 英文停用詞庫：過濾常見的代名詞、介係詞等無意義單字
    eng_stop_words = {
        "i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours", "yourself", "yourselves",
        "he", "him", "his", "himself", "she", "her", "hers", "herself", "it", "its", "itself", "they", "them", "their",
        "theirs", "themselves", "what", "which", "who", "whom", "this", "that", "these", "those", "am", "is", "are",
        "was", "were", "be", "been", "being", "have", "has", "had", "having", "do", "does", "did", "doing", "a", "an",
        "the", "and", "but", "if", "or", "because", "as", "until", "while", "of", "at", "by", "for", "with", "about",
        "against", "between", "into", "through", "during", "before", "after", "above", "below", "to", "from", "up",
        "down", "in", "out", "on", "off", "over", "under", "again", "further", "then", "once", "here", "there", "when",
        "where", "why", "how", "all", "any", "both", "each", "few", "more", "most", "other", "some", "such", "no", "nor",
        "not", "only", "own", "same", "so", "than", "too", "very", "s", "t", "can", "will", "just", "don", "should", "now", "get"
    }
    
    # 中文停用詞庫：過濾虛詞、連接詞，並加入「為什」防止 2-gram 殘留
    chi_stop_words = {
        "的", "了", "在", "是", "和", "就", "不", "也", "都", "這", "那", "與", "及", "或", "著", 
        "過", "於", "對", "從", "向", "被", "讓", "給", "之", "們", "一個", "一些", "有些", 
        "什麼", "為什麼", "如何", "如果", "雖然", "但是", "因為", "所以", "可以", "非常", "為什"
    }

    # 使用 jieba 進行精確斷詞模式
    seg_list = jieba.lcut(text)
    
    words_to_count = []
    for word in seg_list:
        word = word.strip().lower()
        
        # 過濾邏輯：
        # 1. 字數長度必須大於 1 (過濾單個中文字如「我」、「你」)
        # 2. 不在英、中停用詞名單中
        # 3. 必須是字母或數字 (過濾純標點符號)
        if len(word) < 2 or word in eng_stop_words or word in chi_stop_words:
            continue
        if not word.isalnum():
            continue
            
        words_to_count.append(word)
                    
    # 使用 Counter (內建 Hash Table 實作) 統計頻率並回傳前 n 名
    counter = Counter(words_to_count)
    return counter.most_common(top_n)

# ---------------- 2. GUI 功能與文字雲產生 (螺旋演算法) ----------------
def generate_wordcloud():
    """
    從輸入框讀取文字，計算頻率後在畫布上繪製不重疊的文字雲。
    """
    text = text_input.get("1.0", tk.END)
    if not text.strip():
        messagebox.showwarning("WARNING", "INSERT COIN (TEXT) TO PLAY!")
        return

    # 讀取使用者自訂的顯示數量
    try:
        word_count = int(count_entry.get())
        if word_count <= 0: raise ValueError
    except ValueError:
        messagebox.showwarning("ERROR", "請輸入正整數！")
        return

    top_words = get_top_words(text, word_count)
    
    # 清空畫布並重新繪製背景網格
    canvas.delete("all")
    draw_crt_grid() 
    
    if not top_words:
        messagebox.showinfo("INFO", "沒有足夠的關鍵字。")
        return
        
    max_freq = top_words[0][1] # 最高頻率作為字體大小基準
    placed_boxes = []          # 紀錄已放置文字的邊界框，用於碰撞偵測
    cx, cy = 300, 200          # 畫布中心座標
    
    for word, freq in top_words:
        # 根據頻率計算字體大小
        font_size = max(12, int((freq / max_freq) * 55))
        # 像素城市配色：紅、藍、黃、白、灰
        colors = ["#D9212A", "#3783C6", "#F3D500", "#FFFFFF", "#B3B3B3"]
        color = random.choice(colors)
        
        theta = 0.0     # 螺旋角度
        step = 0.5      # 旋轉步進值
        placed = False  # 標記是否成功放置
        
        # 阿基米德螺旋線演算法：若重疊則沿著螺旋線向外尋找空位
        while not placed:
            r = 4 * theta # 半徑隨角度增加
            x = cx + r * math.cos(theta)
            y = cy + r * math.sin(theta)
            
            # 先試繪製文字以取得其邊界區域
            text_id = canvas.create_text(x, y, text=word, font=("Courier", font_size, "bold"), fill=color)
            bbox = canvas.bbox(text_id) 
            
            # 碰撞偵測 (AABB Collision)
            overlap = False
            for pb in placed_boxes:
                # 判斷兩個矩形區域是否交集
                if bbox[2] > pb[0] and bbox[0] < pb[2] and bbox[3] > pb[1] and bbox[1] < pb[3]:
                    overlap = True
                    break
            
            if overlap:
                canvas.delete(text_id) # 若重疊則刪除重來
                theta += step
                if theta > 150: break  # 防呆：超出範圍太遠則放棄該字
            else:
                placed_boxes.append(bbox) # 成功放置，紀錄位置
                placed = True

def draw_crt_grid():
    """
    繪製深色的細格線，模擬復古 CRT 螢幕的顯示質感。
    """
    for i in range(0, 600, 10):
        canvas.create_line(i, 0, i, 400, fill="#1a1a1a")
    for i in range(0, 400, 10):
        canvas.create_line(0, i, 600, i, fill="#1a1a1a")

def paste_text():
    """ 讀取系統剪貼簿內容並插入輸入框 """
    try:
        clipboard_content = root.clipboard_get()
        text_input.insert(tk.INSERT, clipboard_content)
    except tk.TclError:
        messagebox.showwarning("ERROR", "剪貼簿為空！")

def clear_text():
    """ 清空輸入框內的文字 """
    text_input.delete("1.0", tk.END)

def save_image():
    """
    匯出圖片。優先使用 PostScript 數據流方式 (純淨無雜訊)，
    若系統環境不支援則自動跳轉至螢幕截圖備案。
    """
    if not HAS_LIBS:
        messagebox.showerror("缺少套件", "請安裝 jieba 與 pillow")
        return
        
    try:
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            initialfile="pixel_wordcloud.png",
            title="儲存文字雲圖片",
            filetypes=[("PNG 圖片", "*.png")]
        )
        if not file_path: return

        # 方案 A：PostScript 數據轉換 (不經過螢幕，畫質最純淨)
        try:
            ps_data = canvas.postscript(colormode='color')
            img = Image.open(io.BytesIO(ps_data.encode('utf-8')))
            img.save(file_path, 'png')
        except:
            # 方案 B：螢幕截圖備案 (增加 0.5 秒延遲以避開系統浮動視窗)
            root.after(500)
            root.update()
            x, y, w, h = canvas.winfo_rootx(), canvas.winfo_rooty(), canvas.winfo_width(), canvas.winfo_height()
            img = ImageGrab.grab(bbox=(x, y, x+w, y+h))
            img.save(file_path)
        
        messagebox.showinfo("SUCCESS", f"成功儲存至 {os.path.basename(file_path)}")
    except Exception as e:
        messagebox.showerror("ERROR", f"存檔失敗: {e}")

# ---------------- 3. 介面設計 (Isometric Pixel Art 配色) ----------------
root = tk.Tk()
root.title("PIXEL CITY WORD CLOUD")
root.geometry("650x800") 
root.configure(bg="#8C8661") # 設為背景地板色

title_label = tk.Label(root, text="► PIXEL CITY WORD CLOUD ◄", font=("Courier", 22, "bold"), bg="#8C8661", fg="#FFFFFF")
title_label.pack(pady=15)

# 建立紅色邊框的螢幕框架
screen_frame = tk.Frame(root, bg="#D9212A", bd=4, relief=tk.RAISED)
screen_frame.pack(pady=5)

# 白底黑字的文字輸入區
text_input = tk.Text(screen_frame, height=7, width=58, font=("Courier", 12, "bold"), bg="#FFFFFF", fg="#000000", insertbackground="#000000", borderwidth=0)
text_input.pack(padx=5, pady=5)

# 數量調整參數區
config_frame = tk.Frame(root, bg="#8C8661")
config_frame.pack(pady=5)

count_label = tk.Label(config_frame, text="WORDS TO SHOW:", font=("Courier", 12, "bold"), bg="#8C8661", fg="#000000")
count_label.pack(side=tk.LEFT, padx=5)

count_entry = tk.Entry(config_frame, font=("Courier", 12, "bold"), bg="#FFFFFF", fg="#000000", width=5, bd=3, relief=tk.SUNKEN)
count_entry.insert(0, "25") 
count_entry.pack(side=tk.LEFT, padx=5)

# 按鈕區域：使用 Label + Bind 解決 Mac 系統按鈕顏色失效問題
btn_frame = tk.Frame(root, bg="#8C8661")
btn_frame.pack(pady=10)

def create_pixel_button(parent, text, color, fg, command):
    """ 自定義像素風按鈕產生器 """
    btn = tk.Label(parent, text=text, font=("Courier", 14, "bold"), bg=color, fg=fg, bd=5, relief=tk.RAISED, cursor="hand2")
    btn.pack(side=tk.LEFT, padx=8)
    btn.bind("<Button-1>", lambda e: command())
    return btn

# 建立四個功能按鈕
create_pixel_button(btn_frame, "[ PASTE ]", "#3783C6", "#FFFFFF", paste_text)
create_pixel_button(btn_frame, "[ CLEAR ]", "#B3B3B3", "#000000", clear_text)
create_pixel_button(btn_frame, "★ START ★", "#D9212A", "#FFFFFF", generate_wordcloud)
create_pixel_button(btn_frame, "[ SAVE ]", "#F3D500", "#000000", save_image)

# 下方文字雲顯示畫布 (灰色邊框)
canvas_frame = tk.Frame(root, bd=6, relief=tk.SUNKEN, bg="#B3B3B3")
canvas_frame.pack(pady=5)

canvas = tk.Canvas(canvas_frame, width=600, height=400, bg="#050505", highlightthickness=0)
canvas.pack()
draw_crt_grid() # 初始化網格

root.mainloop()