import tkinter as tk
from tkinter import filedialog, messagebox
import random

# ---------------- 1. 自建 Hash Table (絕不使用 dict) ----------------
class CustomHashTable:
    def __init__(self, size=1024):
        self.size = size
        self.table = [[] for _ in range(size)]

    def _hash(self, key):
        hash_val = 0
        for char in key:
            hash_val = (hash_val * 31 + ord(char)) % self.size
        return hash_val

    def add_word(self, word):
        index = self._hash(word)
        bucket = self.table[index]
        for i in range(len(bucket)):
            if bucket[i][0] == word:
                bucket[i][1] += 1
                return
        bucket.append([word, 1])

    def get_top_n(self, n):
        all_words = []
        for bucket in self.table:
            for item in bucket:
                all_words.append(item)
        
        # 使用選擇排序法 (Selection Sort) 避免使用內建 sort()
        for i in range(len(all_words)):
            max_idx = i
            for j in range(i + 1, len(all_words)):
                if all_words[j][1] > all_words[max_idx][1]:
                    max_idx = j
            all_words[i], all_words[max_idx] = all_words[max_idx], all_words[i]
            
        return all_words[:n]

# ---------------- 2. 文字處理 (中英雙語 & Stop Words) ----------------
def process_text(text, hash_table):
    stop_words = ["is", "a", "are", "am", "the", "to", "and", "in", "of", "it", "for", "on", "with", "this", "that"]
    punctuation = ".,!?()[]{}\"':;\n\r\t<>@#$%^&*"
    
    clean_text = ""
    for char in text:
        if char not in punctuation:
            clean_text += char
        else:
            clean_text += " "
            
    # 處理英文
    words = clean_text.lower().split()
    for word in words:
        if all('a' <= c <= 'z' for c in word):
            if word not in stop_words and len(word) > 1:
                hash_table.add_word(word)
                
    # 處理中文 (2-gram 雙字詞擷取法，加分項)
    for i in range(len(clean_text) - 1):
        char1, char2 = clean_text[i], clean_text[i+1]
        if '\u4e00' <= char1 <= '\u9fff' and '\u4e00' <= char2 <= '\u9fff':
            word = char1 + char2
            hash_table.add_word(word)

# ---------------- 3. GUI 與文字雲產生 (像素風格) ----------------
def generate_wordcloud():
    text = text_input.get("1.0", tk.END)
    if not text.strip():
        messagebox.showwarning("警告", "請輸入文字！")
        return

    my_hash = CustomHashTable()
    process_text(text, my_hash)
    top_words = my_hash.get_top_n(20)
    
    canvas.delete("all")
    
    if top_words:
        max_freq = top_words[0][1]
        for word, freq in top_words:
            # 像素風格字體與隨機顏色
            font_size = max(12, int((freq / max_freq) * 60))
            x = random.randint(100, 500)
            y = random.randint(50, 350)
            colors = ["#39ff14", "#ff007f", "#00ffff", "#fdfd96", "#ffb347"]
            color = random.choice(colors)
            canvas.create_text(x, y, text=word, font=("Courier", font_size, "bold"), fill=color)

def save_image():
    try:
        canvas.postscript(file="wordcloud_output.eps")
        messagebox.showinfo("成功", "已儲存為 wordcloud_output.eps (EPS格式)")
    except Exception as e:
        messagebox.showerror("錯誤", f"存檔失敗: {e}")

# 設定 GUI 介面
root = tk.Tk()
root.title("Pixel Word Cloud Generator")
root.geometry("600x700")
root.configure(bg="#2b2b2b")

title_label = tk.Label(root, text="> WORD CLOUD GENERATOR_", font=("Courier", 18, "bold"), bg="#2b2b2b", fg="#39ff14")
title_label.pack(pady=10)

text_input = tk.Text(root, height=10, width=60, font=("Courier", 12), bg="#1e1e1e", fg="white", insertbackground="white")
text_input.pack(pady=10)

btn_frame = tk.Frame(root, bg="#2b2b2b")
btn_frame.pack(pady=5)

gen_btn = tk.Button(btn_frame, text="[GENERATE]", font=("Courier", 14, "bold"), bg="#444444", fg="#39ff14", command=generate_wordcloud)
gen_btn.pack(side=tk.LEFT, padx=10)

save_btn = tk.Button(btn_frame, text="[SAVE EPS]", font=("Courier", 14, "bold"), bg="#444444", fg="#00ffff", command=save_image)
save_btn.pack(side=tk.LEFT, padx=10)

canvas = tk.Canvas(root, width=600, height=400, bg="#111111", highlightthickness=2, highlightbackground="#39ff14")
canvas.pack(pady=10)

root.mainloop()