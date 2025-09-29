import tkinter as tk
from threading import Thread
import requests
import json
from bs4 import BeautifulSoup
import random
from dataclasses import dataclass
from datetime import date
import os
import ctypes
import asyncio

# Get the directory where this script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

LOOKUP_FILE = os.path.join(BASE_DIR, "jehle_verb_lookup.json")
HISTORY_FILE = os.path.join(BASE_DIR, "history.json")

@dataclass
class NounData:
    spanish: str
    english: str

@dataclass
class VerbData:
    spanish: str
    english: str

# --- History utilities ---
def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def get_last_update_date():
    history = load_history()
    if history:
        return max(history.keys())
    return None


def get_today_data():
    history = load_history()
    return history.get(str(date.today()))


def save_daily_data(noun, verb, conjug):
    today = str(date.today())
    history = load_history()
    history[today] = {
        "noun": {"spanish": noun.spanish, "english": noun.english},
        "verb": {"spanish": verb.spanish, "english": verb.english},
        "conjugation": conjug
    }
    save_history(history)


# --- Data fetching functions ---
def get_random_noun() -> NounData:
    try:
        data = requests.get('https://random-words-api.vercel.app/word/spanish', timeout=5).json()
        return NounData(spanish=data[0]['word'], english=data[0]['definition'])
    except:
        return NounData(spanish="error", english="error")

def get_random_verb_data(lookup_file) -> VerbData:
    try:
        with open(lookup_file, "r", encoding="utf-8") as f:
            verbs = json.load(f)
        verb = random.choice(list(verbs.keys()))
        entry = random.choice(verbs[verb])
        return VerbData(spanish=verb, english=entry['translation'])
    except:
        return VerbData(spanish="error", english="error")


def get_conjugation(verb):
    try:
        url = f'https://www.spanishdict.com/conjugate/{verb}'
        soup = BeautifulSoup(requests.get(url, timeout=5).text, 'html.parser')
        table = soup.find('table', {'class': 'sTe03NLF'})
        if not table:
            return [["Conjugation not found"]]
        conjugations = []
        for row in table.find_all('tr'):
            conjugations.append([cell.get_text(strip=True) for cell in row.find_all(['th','td'])])
        return conjugations
    except:
        return [["Error fetching conjugation"]]


# --- GUI update function ---
def display_data(data):
    for widget in main_frame.winfo_children():
        widget.destroy()

    noun = data["noun"]
    verb = data["verb"]
    conjug = data["conjugation"]

    # --- Dark theme colors ---
    bg_color = "#2e2e2e"      # Dark gray background
    frame_bg = "#2e2e2e"      # Slightly lighter for frames
    text_color = "#f9f9f9"    # White text
    separators_color = "black"

    # --- Noun Frame ---
    noun_frame = tk.Frame(main_frame, bg=frame_bg, bd=2, relief="ridge", padx=10, pady=5)
    tk.Label(noun_frame, text="Random noun", font=("Arial", 13, "bold"), bg=frame_bg, fg=text_color).pack(anchor="w")
    tk.Frame(noun_frame, height=1, bg=separators_color).pack(fill="x", pady=4)  # line separator
    tk.Label(noun_frame, text=f"{noun['spanish'].upper()}", font=("Arial", 12), bg=frame_bg, fg=text_color).pack(anchor="w")
    tk.Frame(noun_frame, height=1, bg=separators_color).pack(fill="x", pady=4)  # line separator
    tk.Label(noun_frame, text=f"{noun['english']}", font=("Arial", 11), bg=frame_bg, fg=text_color).pack(anchor="w")
    noun_frame.pack(fill="x", padx=10, pady=5)

    # --- Verb Frame ---
    verb_frame = tk.Frame(main_frame, bg=frame_bg, bd=2, relief="ridge", padx=10, pady=5)
    tk.Label(verb_frame, text="Random verb", font=("Arial", 13, "bold"), bg=frame_bg, fg=text_color).pack(anchor="w")
    tk.Frame(verb_frame, height=1, bg=separators_color).pack(fill="x", pady=4)  # separator
    tk.Label(verb_frame, text=f"{verb['spanish'].upper()}", font=("Arial", 12), bg=frame_bg, fg=text_color).pack(anchor="w")
    tk.Frame(verb_frame, height=1, bg=separators_color).pack(fill="x", pady=4)  # separator
    tk.Label(verb_frame, text=f"{verb['english']}", font=("Arial", 11), bg=frame_bg, fg=text_color).pack(anchor="w")
    verb_frame.pack(fill="x", padx=10, pady=5)

    # --- Conjugation Frame ---
    conj_frame = tk.Frame(main_frame, bg=bg_color, bd=2, relief="ridge", padx=5, pady=5)
    tk.Label(conj_frame, text="Conjugation", font=("Arial", 13, "bold"), bg=bg_color, fg=text_color).grid(row=0, column=0, columnspan=len(conjug[0]), pady=(0,5))
    max_rows = 10
    for i, row in enumerate(conjug[:max_rows]):
        for j, cell in enumerate(row):
            tk.Label(conj_frame, text=cell, font=("Courier", 10), bg=bg_color, fg=text_color,
                     borderwidth=1, relief="solid", padx=5, pady=2).grid(row=i+1, column=j, sticky="nsew")
            conj_frame.grid_columnconfigure(j, weight=1)
    conj_frame.pack(fill="x", padx=10, pady=5)



# --- Async daily update ---
async def update_daily_widget():
    while True:
        today = str(date.today())
        last_date = get_last_update_date()

        if today != last_date:
            noun = get_random_noun()
            verb = get_random_verb_data(LOOKUP_FILE)
            conjug = get_conjugation(verb.spanish)
            data = {
                "noun": {"spanish": noun.spanish, "english": noun.english},
                "verb": {"spanish": verb.spanish, "english": verb.english},
                "conjugation": conjug
            }
            display_data(data)
            save_daily_data(noun, verb, conjug)

        await asyncio.sleep(3600)  # check every hour


def main():
    global root, main_frame
    # --- Tkinter Setup ---
    root = tk.Tk()
    root.title("Spanish Widget")
    root.overrideredirect(True)
    root.config(bg="white")

    # Top-right corner
    window_width = 650
    window_height = 500
    screen_width = root.winfo_screenwidth()
    x = screen_width - window_width - 10
    y = 10
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    main_frame = tk.Frame(root, bg="white")
    main_frame.pack(padx=5, pady=5)

    # --- Windows click-through ---
    hwnd = ctypes.windll.user32.FindWindowW(None, root.title())
    
    ctypes.windll.user32.SetWindowLongW(hwnd, -20, 0x80000 | 0x20)
    root.attributes("-transparentcolor", "white")
    root.attributes("-topmost", False)

    # --- Show today’s data if it exists ---
    today_data = get_today_data()
    if today_data:
        display_data(today_data)

    # --- Run asyncio loop in a thread ---
    def run_asyncio_loop(loop):
        asyncio.set_event_loop(loop)
        loop.run_until_complete(update_daily_widget())

    loop = asyncio.new_event_loop()
    t = Thread(target=run_asyncio_loop, args=(loop,), daemon=True)
    t.start()

    root.mainloop()


if __name__ == "__main__":
    main()