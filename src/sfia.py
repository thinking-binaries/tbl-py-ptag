#! /usr/bin/env python3
# sfia.py  23/06/2025  D.J.Whale

import ptag

#class SFIAParser(ptag.PathClassifier):
#class SFIAParser(ptag.VariableParser):
class SFIAParser(ptag.RuleParser):
    RULES = {
        "/html/body/div/div/main/section/article/header/h1/":                    lambda v:print("title:", v),          # skill title[0]
        "/html/body/div/div/main/section/article/header/h1/span/":               lambda v:print("code:", v),           # skill code[0]
        ##"/html/body/div/div/main/section/article/header/div/span/span/":         lambda v:print("title_summary:", v),  # title[0] summary[1]
        "/html/body/div/div/main/section/article/header/div/div/p/":             lambda v:print("summary:", v),        # summary[0]
        "/html/body/div/div/main/section/article/div/div/div/div/div/p/":        lambda v:print("desc:", v),           # longdesc[0,1]
        "/html/body/div/div/main/section/article/div/div/div/div/div/ul/li/":    lambda v:print("areas:", v),           # skill test[*]
        "/html/body/div/div/main/section/article/div/div/div/table/tr/td/":      lambda v:print("levels:", v),         # applicable levels[*]
        "/html/body/div/div/main/section/article/div/div/div/div/div/div/p/":    lambda v:print("compstmt:", v),       # competency statements[*]
        "/html/body/div/div/main/aside/div/aside/div/span/a/":                   lambda v:print("related:", v),        # related areas[*]
    }

    @staticmethod
    def do_parse_file(filename:str) -> None:
        """Parse a file, without the app needing to create a parser object"""
        SFIAParser().parse_file(filename)

    @staticmethod
    def do_parse_from(iterable) -> None:
        """Parse any iterable, without the app needing to create a parser object"""
        SFIAParser().parse_from(iterable)

if __name__ == "__main__":
    import sys
    # wget -O sfia_RESD.xml https://sfia-online.org/en/skillcode/8/RESD
    # awk it, to strip the google analytics malformed js tags -> RESD_safe.html

    DEFAULT_FILENAME = "../../../sfia8/cache/RESD_safe.html"

    if len(sys.argv) > 1:
        for filename in sys.argv[1:]:
            SFIAParser.do_parse_file(filename)
    else:
        SFIAParser.do_parse_file(DEFAULT_FILENAME)

# END