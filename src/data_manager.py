import os, json, requests, random
from bs4 import BeautifulSoup
from dataclasses import dataclass
from datetime import date
from paths import LOOKUP_FILE, HISTORY_FILE, FALLBACK_NOUNS_FILE
from logger import logger
import time


@dataclass
class NounData:
    spanish: str
    english: str


@dataclass
class VerbData:
    spanish: str
    english: str


# --- Helpers ---
def load_fallback_words():
    with open(FALLBACK_NOUNS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def get_fallback_word():
    words = load_fallback_words()
    entry = random.choice(words)
    return NounData(spanish=entry["word"], english=entry["definition"])


class DailyDataManager:
    def __init__(self):
        self.history = self._load_history()

    # --- History ---
    def _load_history(self):
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def save_history(self):
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)

    def get_today(self):
        return self.history.get(str(date.today()))

    def save_today(self, noun: NounData, verb: VerbData, conjug):
        today = str(date.today())
        logger.info(f"Saving data for today: noun: {noun}, verb: {verb}")
        self.history[today] = {
            "noun": noun.__dict__,
            "verb": verb.__dict__,
            "conjugation": conjug,
        }
        self.save_history()

    # --- Fetchers ---
    def random_noun(self) -> "NounData":
        """Fetch a random noun from the API once; if it fails, use local JSON fallback."""
        try:
            resp = requests.get(
                "https://random-words-api.vercel.app/word/spanish", timeout=5
            )
            if resp.status_code == 200:
                data = resp.json()
                noun_spanish = data[0]["word"]
                noun_english = data[0]["definition"]
                logger.info(
                    f"Generated random noun: {noun_spanish}, translation: {noun_english}"
                )
                return NounData(spanish=noun_spanish, english=noun_english)
            else:
                noun = get_fallback_word()
                logger.warning(
                    f"API returned {resp.status_code}, using a random fallback noun: {noun}"
                )
                return noun
        except requests.RequestException as e:
            noun = get_fallback_word()
            logger.warning(
                f"API request failed: {e}. Using a random fallback noun: {noun}"
            )
            return noun

    def random_verb(self) -> VerbData:
        try:
            with open(LOOKUP_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

            keys = list(data.keys())
            random.shuffle(keys)

            for key in keys:
                for entry in data[key]:
                    if entry.get("tense") == "Present":
                        verb_spanish = entry["infinitive"]
                        verb_english = entry["translation"]
                        logger.info(
                            f"Generated random verb: {verb_spanish}, translation: {verb_english}"
                        )
                        return VerbData(spanish=verb_spanish, english=verb_english)
        except:
            return VerbData("error", "error")

    def conjugation(self, verb: str):
        try:
            url = f"https://www.spanishdict.com/conjugate/{verb}"
            soup = BeautifulSoup(requests.get(url, timeout=5).text, "html.parser")
            table = soup.find("table", {"class": "sTe03NLF"})
            if not table:
                return [["Conjugation not found"]]
            return [
                [cell.get_text(strip=True) for cell in row.find_all(["th", "td"])]
                for row in table.find_all("tr")
            ]
        except:
            return [["Error fetching conjugation"]]
