import enchant
import re
from rich.console import Console


def to_english(original_string, response_string):
    d = enchant.Dict("en_US")
    d.add("avar")
    d.add("avaric")
    d.add("avarus")
    cons = Console()
    # original_string = "магазин, лавка, ларёк; гьитІинаб тукен ларёк; кванил тукен продовольственный магазин; росдал тукен сельский магазин; тІахьазул тукен книжный магазин; эбел тукада хІалтІулей йиго мать работает в магазине; тукаде чакар бачІун буго в магазин поступил сахар; тукадаса хьитал росизе купить в магазине обувь"
    # response_string = "shop, shop, stall; gitlinab tuken stall; kwanil tuken grocery store; birthed tuken village shop; tyahiazul tuken bookstore; ebel tukada хІалтлулей yigo mother works in the shop; tukada chakar бачіун bugo in the shop received sugar; tukada hital rosese buy shoes in the shop."

    # the number of non-english words should correspond one to one with the avar original
    # this is except in the case where one of the avar words is also a russian word, which is translated as more than one english word

    """
     per ; delimited section, find the latest index of non-english words
     then substitute those in
    """

    def slice_section(section, checks):
        # find index, compress sequential Trues to 1 True
        previous_was_true = False
        idx = 0
        for check in checks:
            if not check:
                idx += 1
                previous_was_true = False
            if previous_was_true:
                continue
            if check:
                previous_was_true = True
                idx += 1
        words = section.split(" ")
        return words[0 : idx - 1]

    def last_false(checks):
        last = 0
        for idx, check in enumerate(checks):
            if not check:
                last = idx
        return last

    words = response_string.strip().split(" ")
    is_english = []
    for word in words:
        word = re.sub(r"[\[\],;.?!]", "", word)
        if not word:
            continue
        is_english.append(d.check(word))
    substitute_words = " ".join(slice_section(original_string.strip(), is_english))
    last_idx = last_false(is_english)
    # adjust the index, but only if there is at least one
    # non-English word
    if last_idx != 0:
        last_idx += 1

    remaining_words = words[last_idx:]
    return f"[i]{substitute_words}[/i] {' '.join(remaining_words)}".strip()
