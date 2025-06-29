#! /usr/bin/env python3
# html.py  25/06/2025  D.J.Whale

import ptag

#----- HTML TEST PARSER --------------------------------------------------------
class HTMLTestParser(ptag.RuleParser):
    """A demonstration of extracting data from a specific HTML file format"""
    RULES = {
        "/html/head/title/":    lambda v: print("title:%s" % v),
        "/html/body/h1/":       lambda v: print("heading:%s" % v),
        "/html/body/a/href":    lambda v: print("href:%s" % v)
    }
    def __init__(self):
        ptag.RuleParser.__init__(self)

    @staticmethod
    def do_parse_file(filename:str) -> None:
        """Parse a file, without the app needing to create a parser object"""
        HTMLTestParser().parse_file(filename)

    @staticmethod
    def do_parse_from(iterable) -> None:
        """Parse any iterable, without the app needing to create a parser object"""
        HTMLTestParser().parse_from(iterable)

#----- HTML TABLE PARSER --------------------------------------------------------
class HTMLTableParser(ptag.RuleParser):
    def SetTableName(self, rules, value):
        _ = rules  # argused
        print("# table:", value)
        self._table_name = value

    def AddHeading(self, rules, value):
        _ = rules  # argused
        self._headings.append(value)

    def EndHeadings(self, rules, value):
        _,_ = rules, value  # argsused
        print("# headings:", self._headings)

    def StartRow(self, rules, value):
        _,_ = rules, value  # argsused
        self._row = []

    def AddData(self, rules, value):
        _ = rules  # argused
        self._row.append(value)

    def EndRow(self, rules, value):
        _,_ = rules, value  #argsused
        print(self._row)

    RULES = {
        "/html/body/h1/":                   (SetTableName,),
        "/html/body/table/thead/tr/th/":    (AddHeading,),
        "/html/body/table/thead~":          (EndHeadings,),
        "/html/body/table/tr":              (StartRow,),
        "/html/body/table/tr~":             (EndRow,),
        "/html/body/table/tr/td/":          (AddData,)
    }

    def __init__(self, **kwargs):
        ptag.RuleParser.__init__(self, **kwargs)
        self._table_name = None
        self._headings = []
        self._rows = {}

    @staticmethod
    def do_parse_file(filename:str) -> None:
        """Parse a file, without the app needing to create a parser object"""
        HTMLTableParser().parse_file(filename)

    @staticmethod
    def do_parse_from(iterable) -> None:
        """Parse any iterable, without the app needing to create a parser object"""
        HTMLTableParser().parse_from(iterable)

if __name__ == "__main__":
    FILENAME = "test.html"
    ptag.HTMLHREFExtractor.do_parse_file(FILENAME)

    FILENAME = "test.html"
    HTMLTestParser.do_parse_file(FILENAME)

    FILENAME = "test_table.html"
    HTMLTableParser.do_parse_file(FILENAME)
