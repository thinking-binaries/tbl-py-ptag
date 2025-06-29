#! /usr/bin/env python3
# muppets.py  23/06/2025  D.J.Whale

import ptag

#-------------------------------------------------------------------------------
#class MuppetsParser(ptag.PathClassifier):
#class MuppetsParser(ptag.VariableParser):
#class MuppetsParser(ptag.RuleParser):
class MuppetsParser(ptag.RecBuilder):
    HEADINGS = ("type", "id",   "entity",   "description")
    QUOTED   = (False,  False,  True,       True)

    def start_rec(self, rules, value) -> None:
        self._rec = {"type":self._type}

    def setType(self, rules, value) -> None:
        _ = rules  # argused
        self._type = value

    #NOTE, there are multiple resultsets in this xml file, we need to flatten
    RULES = {
       #"/":
       #"/IMDbResults":
       #"/IMDbResults/ResultSet":
       "/IMDbResults/ResultSet/type":                       (setType,),
       "/IMDbResults/ResultSet/ImdbEntity":                 (start_rec,),
       "/IMDbResults/ResultSet/ImdbEntity/id":              (ptag.RecBuilder.store, "id"),
       "/IMDbResults/ResultSet/ImdbEntity/":                (ptag.RecBuilder.store, "entity"),
       #"/IMDbResults/ResultSet/ImdbEntity/Description":
       "/IMDbResults/ResultSet/ImdbEntity/Description/":    (ptag.RecBuilder.store, "description"),
       #"/IMDbResults/ResultSet/ImdbEntity/Description~":
       "/IMDbResults/ResultSet/ImdbEntity~":                (ptag.RecBuilder.end_rec,)
       #"/IMDbResults/ResultSet~":
       #"/IMDbResults~":
       #"/~":
    }

    @staticmethod
    def do_parse_file(filename:str):
        """Parse a file, without the app needing to create a parser object"""
        m = MuppetsParser()
        m.parse_file(filename)
        return m

    @staticmethod
    def do_parse_from(iterable):
        """Parse any iterable, without the app needing to create a parser object"""
        m = MuppetsParser()
        m.parse_from(iterable)
        return m

#-------------------------------------------------------------------------------
class MuppetsSQLParser(ptag.SQLGenerator):
    def setType(self, rules, value):
        _ = rules  # argused
        self._type = value

    def start_rec(self, rules=None, value=None):
        if hasattr(self, "_type"):
            self._rec = {"muppets": {"type": self._type}}
        else:
            self._rec = {"muppets": {}}

    RULES = {
       "/IMDbResults/ResultSet/type":                       (setType,),
       "/IMDbResults/ResultSet/ImdbEntity":                 (start_rec,),
       "/IMDbResults/ResultSet/ImdbEntity/id":              (ptag.SQLGenerator.store, "muppets", "id"),
       "/IMDbResults/ResultSet/ImdbEntity/":                (ptag.SQLGenerator.store, "muppets", "entity"),
       "/IMDbResults/ResultSet/ImdbEntity/Description/":    (ptag.SQLGenerator.store, "muppets", "description"),
       "/IMDbResults/ResultSet/ImdbEntity~":                (ptag.SQLGenerator.end_rec,)
    }

    @staticmethod
    def do_parse_file(filename:str):
        """Parse a file, without the app needing to create a parser object"""
        m = MuppetsSQLParser()
        m.parse_file(filename)
        return m

    @staticmethod
    def do_parse_from(iterable):
        """Parse any iterable, without the app needing to create a parser object"""
        m = MuppetsSQLParser()
        m.parse_from(iterable)
        return m

#-------------------------------------------------------------------------------
if __name__ == "__main__":
    # wget -O muppets.xml xxxx IMDB?
    FILENAME = "muppets.xml"
    MuppetsParser.do_parse_file(FILENAME)

    # inefficient string processing approach (good for small data sets)
    print(MuppetsSQLParser.do_parse_file(FILENAME).get_sql())

    # more efficient iteration approach (good for large data sets)
    #inserts = MuppetsSQLParser.do_parse_file(FILENAME).get_inserts()
    #for i in inserts:
    #    print(i)

# END