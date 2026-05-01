import tkinter as tk
from tkinter import messagebox, filedialog
import random
import math
import os
import io
from collections import Counter

# 引入外部專業套件
try:
    import jieba
    from PIL import Image, ImageGrab
    HAS_LIBS = True
except ImportError:
    HAS_LIBS = False

# ---------------- 1. 文字處理與頻率計算 (Jieba 專業版) ----------------
def get_top_words(text, top_n):
    # 英文停用詞庫
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
    
    # 中文停用詞庫 (過濾虛詞與常見無意義組合)
    chi_stop_words = {
        "的", "了", "在", "是", "和", "就", "不", "也", "都", "這", "那", "與", "及", "或", "著", 
        "過", "於", "對", "從", "向", "被", "讓", "給", "之", "們", "一個", "一些", "有些", 
        "什麼", "為什麼", "如何", "如果", "雖然", "但是", "因為", "所以", "可以", "非常", "為什"
    }

    # 使用 jieba 斷詞
    seg_list = jieba.lcut(text)
    
    words_to_count = []
    for word in seg_list:
        word = word.strip().lower()
        
        # 過濾長度小於 2 的字、停用詞、以及非文字內容
        if len(word) < 2 or word in eng_stop_words or word in chi_stop_words:
            continue
        if not word.isalnum():
            continue
            
        words_to_count.append(word)
                    
    counter = Counter(words_to_count)
    return counter.most_common(top_n)

# ---------------- 2. GUI 功能與文字雲產生 (螺旋演算法) ----------------
def generate_wordcloud():
    text = text_input.get("1.0", tk.END)
    if not text.strip():
        messagebox.showwarning("WARNING", "INSERT COIN (TEXT) TO PLAY!")
        return

    try:
        word_count = int(count_entry.get())
        if word_count <= 0: raise ValueError
    except ValueError:
        messagebox.showwarning("ERROR", "請輸入正整數！")
        return

    top_words = get_top_words(text, word_count)
    
    canvas.delete("all")
    draw_crt_grid() 
    
    if not top_words:
        messagebox.showinfo("INFO", "沒有足夠的關鍵字。")
        return
        
    max_freq = top_words[0][1]
    placed_boxes = [] 
    cx, cy = 300, 200 
    
    for word, freq in top_words:
        font_size = max(12, int((freq / max_freq) * 55))
        # 配色參考自 Isometric Pixel Art 調色盤
        colors = ["#D9212A", "#3783C6", "#F3D500", "#FFFFFF", "#B3B3B3"]
        color = random.choice(colors)
        
        theta = 0.0
        step = 0.5 
        placed = False
        
        while not placed:
            r = 4 * theta
            x = cx + r * math.cos(theta)
            y = cy + r * math.sin(theta)
            
            text_id = canvas.create_text(x, y, text=word, font=("Courier", font_size, "bold"), fill=color)
            bbox = canvas.bbox(text_id) 
            
            overlap = False
            for pb in placed_boxes:
                if bbox[2] > pb[0] and bbox[0] < pb[2] and bbox[3] > pb[1] and bbox[1] < pb[3]:
                    overlap = True
                    break
            
            if overlap:
                canvas.delete(text_id)
                theta += step
                if theta > 150: break
            else:
                placed_boxes.append(bbox)
                placed = True

def draw_crt_grid():
    for i in range(0, 600, 10):
        canvas.create_line(i, 0, i, 400, fill="#1a1a1a")
    for i in range(0, 400, 10):
        canvas.create_line(0, i, 600, i, fill="#1a1a1a")

def paste_text():
    try:
        clipboard_content = root.clipboard_get()
        text_input.insert(tk.INSERT, clipboard_content)
    except tk.TclError:
        messagebox.showwarning("ERROR", "剪貼簿為空！")

def clear_text():
    text_input.delete("1.0", tk.END)

def save_image():
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

        # 優先方案：使用 PostScript 轉換，避開系統 UI 殘影 (解決 pet.png 右上角方塊問題)
        try:
            ps_data = canvas.postscript(colormode='color')
            img = Image.open(io.BytesIO(ps_data.encode('utf-8')))
            img.save(file_path, 'png')
        except:
            # 備用方案：螢幕截圖並增加延遲
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
root.configure(bg="#8C8661") # 橄欖綠地板色

title_label = tk.Label(root, text="► PIXEL CITY WORD CLOUD ◄", font=("Courier", 22, "bold"), bg="#8C8661", fg="#FFFFFF")
title_label.pack(pady=15)

# 輸入框區域
screen_frame = tk.Frame(root, bg="#D9212A", bd=4, relief=tk.RAISED)
screen_frame.pack(pady=5)

text_input = tk.Text(screen_frame, height=7, width=58, font=("Courier", 12, "bold"), bg="#FFFFFF", fg="#000000", insertbackground="#000000", borderwidth=0)
text_input.pack(padx=5, pady=5)

# 數量設定區域
config_frame = tk.Frame(root, bg="#8C8661")
config_frame.pack(pady=5)

count_label = tk.Label(config_frame, text="WORDS TO SHOW:", font=("Courier", 12, "bold"), bg="#8C8661", fg="#000000")
count_label.pack(side=tk.LEFT, padx=5)

count_entry = tk.Entry(config_frame, font=("Courier", 12, "bold"), bg="#FFFFFF", fg="#000000", width=5, bd=3, relief=tk.SUNKEN)
count_entry.insert(0, "25") 
count_entry.pack(side=tk.LEFT, padx=5)

# 按鈕區域 (Label 偽裝按鈕以相容 Mac 顏色)
btn_frame = tk.Frame(root, bg="#8C8661")
btn_frame.pack(pady=10)

def create_pixel_button(parent, text, color, fg, command):
    btn = tk.Label(parent, text=text, font=("Courier", 14, "bold"), bg=color, fg=fg, bd=5, relief=tk.RAISED, cursor="hand2")
    btn.pack(side=tk.LEFT, padx=8)
    btn.bind("<Button-1>", lambda e: command())
    return btn

create_pixel_button(btn_frame, "[ PASTE ]", "#3783C6", "#FFFFFF", paste_text)
create_pixel_button(btn_frame, "[ CLEAR ]", "#B3B3B3", "#000000", clear_text)
create_pixel_button(btn_frame, "★ START ★", "#D9212A", "#FFFFFF", generate_wordcloud)
create_pixel_button(btn_frame, "[ SAVE ]", "#F3D500", "#000000", save_image)

# 文字雲展示區域
canvas_frame = tk.Frame(root, bd=6, relief=tk.SUNKEN, bg="#B3B3B3")
canvas_frame.pack(pady=5)

canvas = tk.Canvas(canvas_frame, width=600, height=400, bg="#050505", highlightthickness=0)
canvas.pack()
draw_crt_grid() 

root.mainloop()