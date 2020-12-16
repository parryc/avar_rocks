from rich.console import Console
from rich.table import Table
from is_english import to_english
from abbreviations import clean_text
import requests
import re
import sys
import enchant

"""
generic dict class that is extended with additional dictionaries, ex. a get function that takes a value
and a limit and returns a Table object.

after translating with deepL, check to see if the letters match the transliteration of the avar text and "convert back"
after ; always begins with avar

ex. магазин, лавка, ларёк; гьитІинаб тукен ларёк; кванил тукен продовольственный магазин; росдал тукен сельский магазин; тІахьазул тукен книжный
will be shop, shop, stall; gitlinab tuken stall; kwanil tuken grocery store; gave birth to tuken village shop; tyahyazul tuken bookstore

; росдал тукен сельский магазин; тІахьазул тукен книжный
; gave birth to tuken village shop; tyahyazul tuken bookstore
>> росдал should stay as росдал, not "gave birth to"

One heuristic to get better results is to replace the headword (in ABS) with ~. Ex. with вас,
which is a Russian word, the translations can get really screwy. 
"""


def deepl_lookup(sentences, key):
    data = [
        ("auth_key", key),
        ("target_lang", "en"),
        ("source_lang", "ru"),
        ("preserve_formatting", "1"),
        ("tag_handling", "xml"),
    ]
    for sentence in sentences:
        # trying to keep deepl from getting clever and removing the transliteration
        # it sometimes works
        data.append(("text", f"щуа| {sentence}"))
    r = requests.post("https://api.deepl.com/v2/translate", data=data)
    # TODO: error handling
    results = r.json()
    return [r["text"].split("|")[1] for r in results["translations"]]


class Definition(object):
    def __init__(self, main, examples, def_num):
        self.main = main.strip()
        self.examples = list(map(str.strip, examples))
        self.def_num = def_num

    def __repr__(self):
        return f"{self.def_num}) {self.main}; {', '.join(self.examples)}"

    def translate(self, api_key, include_examples):
        to_translate = [self.main]
        if self.examples and include_examples:
            to_translate.extend(self.examples)
        to_translate = list(map(clean_text, to_translate))
        deepl_response = deepl_lookup(to_translate, api_key)
        main_translation = deepl_response[0]
        spliced_translations = []
        for idx, translation in enumerate(deepl_response[1:]):
            spliced_translations.append(to_english(self.examples[idx], translation))
        if spliced_translations:
            return f"{main_translation}; {', '.join(spliced_translations)}"
        return main_translation


class AvarMe(object):
    original_text = ""
    definitions = []
    with open("deepl_key") as file:
        api_key = file.read()

    def __init__(self, text):
        def_marker = re.compile("\d+\)")
        self.original_text = text
        if re.match(r"\d+\)", text):
            defs = def_marker.split(text)
            current_definition_number = 0
            for d in defs:
                if not d.strip():
                    continue
                current_definition_number += 1
                parts = d.split(";")
                self.definitions.append(
                    Definition(parts[0], parts[1:], current_definition_number)
                )
        elif ";" in text:
            parts = text.split(";")
            self.definitions.append(Definition(parts[0], parts[1:], None))
        else:
            self.definitions.append(Definition(text, [], None))

    def print_translated_entry(self, include_examples):
        entries = []
        for definition in self.definitions:
            entry = ""
            if definition.def_num:
                entry += str(definition.def_num) + ")"
            entry += re.sub(
                r"\s+", " ", definition.translate(self.api_key, include_examples)
            )
            entries.append(entry)
        return "\n".join(entries)

    def print_original_entry(self):
        return self.original_text


def get(value, limit=3, deepl_key=None, include_examples=False):
    table = Table(show_header=True, header_style="bold magenta", show_lines=True)
    table.add_column("Word", style="bold")
    table.add_column("Forms")  # TODO: what forms are these...
    table.add_column("Definition", width=50)
    table.add_column("English", width=50)
    url = f"http://avar.me/api/?lang=AV-RU&reqw={value}&task=request"
    cons.log("[i]Requesting from Avar.me[/i]")
    r = requests.get(url)
    results = r.json()

    for count, result in enumerate(results["results"]):
        if count > limit - 1:
            continue
        entry = result[1]
        forms = entry[0]
        lemma = forms[0]
        definition = entry[1].strip()
        avar_definition = AvarMe(definition)
        if deepl_key:
            cons.log("[i]Translating from DeepL[/i]")
            if include_examples:
                cons.log("[i]Including examples, may take longer to translate[/i]")
            english = avar_definition.print_translated_entry(include_examples)
            cons.log("[i]Splicing translation[/i]")

        table.add_row(lemma, "\n".join(forms[1:]), definition, english)
    return table


def get2(value, limit=3):
    # TODO: maarulal.ru doesn't support palochka, instead using \u0406, ukranian capital i
    # This should be substituted here, but then normalized to palochka for output.
    # this one also supports wild cards
    # TODO: support for examples like this кІудада
    table = Table(show_header=True, header_style="bold magenta", show_lines=True)
    table.add_column("Word", style="bold")
    table.add_column("Definition", width=50)
    table.add_column("Russian")
    url = f"http://dictionary.maarulal.ru/index.php?d=1&q={value}&search=Поиск&srch[adv]=all&srch[by]=d&srch[in]=-1&a=srch"
    "http://dictionary.maarulal.ru/index.php?d=1&q=цIодорбалагьур&search=Поиск&srch[adv]=all&srch[by]=d&srch[in]=-1&a=srch"
    r = requests.get(url)
    matches = re.findall(r"<dd class=\"defnpreview\">.*?</dd>", r.text)
    if not matches:
        table.add_row("No matches found", "", "")
        return table
    definition = re.sub(";&#32", "", matches[0][26:-7])
    russian, english, arabic, turkish = definition.split(";")
    table.add_row(value, english, russian)
    return table


cons = Console()
d = enchant.Dict("en_US")
args = sys.argv[1:]

api_key = ""
with open("deepl_key") as file:
    api_key = file.read()

# TODO: needs some work on entries with multiple definitions such as хІал or баркала
# perhaps should normalize numbers to numbers in circles, rather than 1. or 1)
# segmenting, or submitting multiple sentences in the case of баркала (delimited with .)
# may improve translation.
lookup = args[0]
include_examples = False
if len(args) > 1:
    include_examples = args[1] == "1"

while True:
    cons.print(
        get(lookup, limit=1, deepl_key=api_key, include_examples=include_examples)
    )
    lookup = re.sub("1", "І", input("next: "))
    if lookup == "stop":
        break
