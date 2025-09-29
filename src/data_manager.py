import os, json, requests, random
from bs4 import BeautifulSoup
from dataclasses import dataclass
from datetime import date
from paths import LOOKUP_FILE, HISTORY_FILE
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
    def random_noun(self) -> NounData:
        """Fetch a random noun from the API, retrying until success.
        Handles rate limits with longer backoff on 429 responses.
        """
        while True:
            try:
                resp = requests.get(
                    "https://random-words-api.vercel.app/word/spanish",
                    timeout=5
                )

                if resp.status_code == 429:
                    logger.warning("Rate limited (429). Waiting 60s before retrying...")
                    time.sleep(60)
                    continue

                resp.raise_for_status()
                data = resp.json()

                noun_spanish = data[0]['word']
                noun_english = data[0]['definition']
                logger.info(f"Generated random noun: {noun_spanish}, translation: {noun_english}")
                return NounData(spanish=noun_spanish, english=noun_english)

            except requests.RequestException as e:
                logger.warning(f"Failed to generate a noun (retrying in 15s): {e}")
                time.sleep(15)

    def random_verb(self) -> VerbData:
        try:
            with open(LOOKUP_FILE, "r", encoding="utf-8") as f:
                verbs = json.load(f)
            verb = random.choice(list(verbs.keys()))
            entry = random.choice(verbs[verb])
            logger.info(f"Generated random verb: {verb}, translation: {entry['translation']}")
            return VerbData(spanish=verb, english=entry["translation"])
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
