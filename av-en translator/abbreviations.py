import re


def clean_text(text):
    abbr = {
        "вводн.": "Introductory word",
        "возвр. мест.": "Reflexive pronoun",
        "вопр.": "Interrogative word",
        "вопр. част.": "Interrogative particle",
        "всп. гл.": "Auxiliary verb",
        "гл.": "Verb",
        "гл. сов.": "Perfective verb",
        "гл. несов.": "Imperfective verb",
        "гл. част.": "Verbal particle",
        "деепр.": "Gerund",
        "клас. в.": "Class variant",
        "комп.": "Сomposite",
        "кратк.": "Short form",
        "личн. мест.": "Personal pronoun",
        "мест. личн.": "Personal pronoun",
        "масд.": "Masdar",
        "межд.": "Interjection",
        "мест.": "Pronoun",
        "мест. нар.": "Pronominal adverb",
        "мн. ч.": "Plural",
        "мод.": "Modal word / Modal phrase",
        "нареч.": "Adverb",
        "ном. част.": "Nominal particle",
        "опред. мест.": "Universal pronoun",
        "посл.": "Postposition",
        "прил.": "Adjective",
        "прич.": "Participle",
        "произв.": "Derivative",
        "род. п.": "Genitive (case)",
        "словосочет.": "Phrase",
        "союз": "Conjunction",
        "стяж.": "Сontraction",
        "сущ.": "Noun",
        "усил. част.": "Intensifier",
        "част.": "Particle",
        "числ.": "Number",
        "эрг.": "Ergative",
    }

    for key, value in abbr.items():
        text = re.sub(key, f"({value})", text)
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"(\d+\))", r"<def>\1</def>", text)
    return text
