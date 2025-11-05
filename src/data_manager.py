import os, json
from dataclasses import dataclass
from datetime import date
from paths import HISTORY_FILE, NOUNS_FILE, VERBS_FILE, SENTENCES_FILE
from logger import logger
import random
from spanishconjugator import Conjugator


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
            "noun": noun,
            "verb": verb,
            "conjugation": conjug,
        }
        self.save_history()

    # --- Fetchers ---
    def random_noun(self) -> "NounData":
        """Fetch a random noun"""
        with open(NOUNS_FILE, "r", encoding="utf-8") as f:
            json_data = json.load(f)

        noun_entry = random.choice(json_data)
        return NounData(spanish=noun_entry["es_noun"], english=noun_entry["en_noun"])

    def random_verb(self) -> VerbData:
        with open(VERBS_FILE, "r", encoding="utf-8") as f:
            json_data = json.load(f)

        verb_entry = random.choice(json_data)
        return VerbData(spanish=verb_entry["es_verb"], english=verb_entry["en_verb"])

    def conjugation(self, verb: str):
        conj = Conjugator()
        tenses = ["present", "preterite", "imperfect", "conditional", "future"]
        persons = ["yo", "tu", "el/ella/usted", "nosotros", "ellos/ellas/ustedes"]

        table = []
        for person in persons:
            row = [person]
            for tense in tenses:
                try:
                    if tense == "conditional":
                        temp = conj.conjugate(verb, "simple_conditional", "conditional")
                    else:
                        temp = conj.conjugate(verb, tense, "indicative")
                    form = temp[person].encode("latin1").decode("utf-8")
                except Exception:
                    form = "-"
                row.append(form)
            table.append(row)

        headers = [[""] + [t.capitalize() for t in tenses]]

        for row in table:
            if row[0] == "el/ella/usted":
                row[0] = "el/ella/Ud."
            elif row[0] == "ellos/ellas/ustedes":
                row[0] = "ellos/ellas/Uds."

        return headers + table
