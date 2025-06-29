#! /usr/bin/env python3
# ptag.py  23/06/2025  D.J.Whale
#   based on python code: 10/04/2014 D.J.Whale
#   based on php code 2012 D.J.Whale

import xml.sax

#-------------------------------------------------------------------------------
class TagParser:
    """Parse a file into a set of tag start/end handler calls"""
    class InboundContentHandler(xml.sax.ContentHandler):
        def __init__(self, outbound_handler):
            xml.sax.ContentHandler.__init__(self)
            self._outbound_handler = outbound_handler
            self._databuffer = None
            self._current_tag = ""
            self._depth = 0

        def flushdata(self):
            if self._databuffer != None:
                #self._trace("flushdata")
                # we have some chars collected, notify our client
                buf = self._databuffer.strip()
                if len(buf) > 0:
                    self._outbound_handler.doData(self._current_tag, buf)
                self._databuffer = None

        def startElement(self, name, attrs):
            #self._trace("startElement:%s" % name)
            self.flushdata()
            self._current_tag = name
            if self._depth == 0:
                self._outbound_handler.doStartDocument()
            self._outbound_handler.doStart(name)
            self._depth += 1
            for attrname in attrs.getNames():
                self._outbound_handler.doAttribute(name, attrname, attrs[attrname])

        def characters(self, text):
            #self._trace("chars:%s" % text)
            if self._databuffer is None:
                self._databuffer = text
            else:
                self._databuffer += text

        def endElement(self, name):
            #self._trace("endElement:%s" % name)
            self.flushdata()
            self._outbound_handler.doEnd(name)
            self._current_tag = ""
            self._depth -= 1
            if self._depth == 0:
                self._outbound_handler.doEndDocument()

    class InboundErrorHandler:
        def warning(self, e):
            print("warning:", str(e))
            # really just informational, keep going

        def error(self, e):
            print("error:", str(e))
            # possibly recoverable, keep going

        def fatalError(self, e):
            print("fatal:", str(e))
            # never recoverable, give in
            raise e

    class DummyOutboundHandler:
        def __init__(self, trace=print):
            self._trace = trace

        def doStartDocument(self) -> None:
            self._trace("startDoc")

        def doStart(self, tag: str) -> None:
            self._trace("start:%s" % str(tag))

        def doAttribute(self, tag: str, name: str, value) -> None:
            self._trace("attr:(%s) %s=%s" % (tag, name, str(value)))

        def doData(self, tag: str, data) -> None:
            self._trace("data:(%s) %s" % (tag, str(data)))

        def doEnd(self, tag: str) -> None:
            self._trace("end:%s" % str(tag))

        def doEndDocument(self) -> None:
            self._trace("endDoc")

    #NOTE: naive approach is: xml.sax.parse(filename, self._content_handler)

    def __init__(self, *, trace=print, outbound_handler=None):
        self._trace = trace
        if outbound_handler is None: outbound_handler = TagParser.DummyOutboundHandler(trace)
        self._outbound_handler = outbound_handler
        self._content_handler = None  # will lazy-start later
        self._xml_parser = None  # will lazy-start later

    def start(self) -> None:
        """Start an incremental parse process for future feed() calls"""
        assert self._xml_parser is None
        # will content_handler will fail in __init__
        # if subclasses __init__ do other dependent work
        self._content_handler = TagParser.InboundContentHandler(self._outbound_handler)
        self._xml_parser = xml.sax.make_parser()
        self._xml_parser.setContentHandler(self._content_handler)
        self._xml_parser.setErrorHandler(TagParser.InboundErrorHandler())

    def feed(self, data) -> None:
        """Feed a single data item to a previously start()ed parser"""
        if data is not None:
            if not isinstance(data, str): data = str(data)
            assert self._xml_parser is not None
            self._xml_parser.feed(data)

    def parse_from(self, iterable) -> None:
        """Parse a whole data set from an iterable"""
        self.start()
        for item in iterable:
            self.feed(item)
        self.finish()

    def parse_file(self, filename:str) -> None:
        """Parse a whole data set from a single local filename"""
        with open(filename) as f:
            self.parse_from(f.readlines())

    def finish(self) -> None:
        """Finish an incremental parse process done with start(), feed()..."""
        assert self._xml_parser is not None
        self._xml_parser.feed("", isFinal=True)
        self._xml_parser = None

    @staticmethod
    def do_parse_file(filename:str) -> None:
        """Parse a file, without the app needing to create a parser object"""
        TagParser().parse_file(filename)

    @staticmethod
    def do_parse_from(iterable) -> None:
        """Parse any iterable, without the app needing to create a parser object"""
        TagParser().parse_from(iterable)

#-------------------------------------------------------------------------------
class PathParser(TagParser):
    """Parse a file into a set of path=value calls (providing a path instead of tagname)"""
    class InboundHandler:
        def __init__(self, outbound_handler):
            assert outbound_handler is not None #TODO<<<< what would the default be here? printing? i.e. PathClassifier?
            self._outbound_handler = outbound_handler
            self._pathstack = []
            self._path = "" # cached str version

        def _push(self, tag: str) -> None:
            self._pathstack.append(tag)
            self._path = self._calcpath()

        def _pop(self, tag: str) -> None:  # or Exception
            assert len(self._pathstack) != 0, "_pop: pathstack is empty"
            assert self._pathstack[-1] == tag, "_pop: nesting error, want:%s got:%s" % (self._pathstack[-1], tag)
            self._pathstack.pop()
            self._path = self._calcpath()

        def _calcpath(self) -> str:
            return "/" + "/".join(self._pathstack)

        def doStartDocument(self) -> None:
            self._outbound_handler.doStartDocument()

        def doStart(self, tag:str) -> None:
            self._push(tag)
            self._outbound_handler.doStart(self._path)

        def doAttribute(self, tag:str, name:str, value) -> None:
            _ = tag  # argused (already part of self._path)
            self._outbound_handler.doAttribute(self._path, name, value)

        def doData(self, tag:str, data) -> None:
            _ = tag  # argused (already part of self._path)
            self._outbound_handler.doData(self._path, data)

        def doEnd(self, tag:str) -> None:
            self._outbound_handler.doEnd(self._path)
            self._pop(tag)

        def doEndDocument(self) -> None:
            self._outbound_handler.doEndDocument()

    def __init__(self, outbound_handler, **kwargs):
        # inject path processing into the handler for the app
        # this converts tag strings to path strings
        #TODO<<<< if outbound_handler is None, provide some DummyHandler, for basically making PathClassifier here
        TagParser.__init__(self, outbound_handler=PathParser.InboundHandler(outbound_handler), **kwargs)

    #TODO<<<< must pass outbound_handler at the moment
    # @staticmethod
    # def do_parse_file(filename:str) -> None:
    #     """Parse a file, without the app needing to create a parser object"""
    #     # default no outbound_handler, so TagParser will print each callback parameter
    #     PathParser().parse_file(filename)
    #
    # @staticmethod
    # def do_parse_from(iterable) -> None:
    #     """Parse any iterable, without the app needing to create a parser object"""
    #     # default no outbound_handler, so TagParser will print each callback parameter
    #     PathParser().parse_from(iterable)

#-------------------------------------------------------------------------------
class VariableParser(PathParser):
    """Parse a file into a set of path=value doVariable() calls"""
    class InboundHandler:
        def __init__(self, outbound_handler):
            self._outbound_handler = outbound_handler

        def doStartDocument(self) -> None:
            self.doVariable("/")

        def doStart(self, path:str) -> None:
            self.doVariable(path, None)

        def doData(self, path:str, data) -> None:
            self.doVariable(path + "/", data)

        def doAttribute(self, path:str, name:str, value) -> None:
            self.doVariable(path + "/%s" % name, value)

        def doEnd(self, path:str) -> None:
            if path is None or path == "": path = ""
            self.doVariable("%s~" % path)

        def doVariable(self, name:str, value=None) -> None:
            if value is None: value = ""
            self._outbound_handler.doVariable(name, value)

        def doEndDocument(self) -> None:
            self.doVariable("/~")

    class DummyOutboundHandler:
        def doVariable(self, name: str, value=None) -> None:
            if value is None or value == "":
                print(name)
            else:
                print("%s=%s" % (name, str(value)))

    def __init__(self, outbound_handler=None, **kwargs):
        # inject path processing into the handler for the app
        # this converts tag strings to path strings
        if outbound_handler is None: outbound_handler = VariableParser.DummyOutboundHandler()
        PathParser.__init__(self, outbound_handler=VariableParser.InboundHandler(outbound_handler), **kwargs)

    @staticmethod
    def do_parse_file(filename:str) -> None:
        """Parse a file, without the app needing to create a parser object"""
        VariableParser().parse_file(filename)

    @staticmethod
    def do_parse_from(iterable) -> None:
        """Parse any iterable, without the app needing to create a parser object"""
        # default has no handler, so by default will print each variable set request
        VariableParser().parse_from(iterable)

#-------------------------------------------------------------------------------
class PathClassifier(VariableParser):
    """Emit a list of paths in this file"""
    def __init__(self, emit=print, **kwargs):
        VariableParser.__init__(self, outbound_handler=self, **kwargs)
        self._emit = emit
        self._paths = {} # path:str -> count(values)

    def doVariable(self, name:str, value=None) -> None:
        _ = value  # argused
        # only print first occurence
        if name not in self._paths:
            self._emit(name)
            self._paths[name] = 1
        else:
            self._paths[name] += 1 # count occurences

    @staticmethod
    def do_parse_file(filename:str) -> None:
        """Parse a file, without the app needing to create a parser object"""
        # will just dump unique paths to stdout
        PathClassifier().parse_file(filename)

    @staticmethod
    def do_parse_from(iterable) -> None:
        """Parse any iterable, without the app needing to create a parser object"""
        # default no handler, so TagParser will print each callback parameter
        # will just dump unique paths to stdout
        PathClassifier().parse_from(iterable)

#----- HTML HREF PARSER ------------------------------------------------------
class HTMLHREFExtractor(VariableParser):
    """Extract all A HREF links from a HTML page"""
    def __init__(self, extract=print, **kwargs):
        VariableParser.__init__(self, outbound_handler=self, **kwargs)
        self._extract = extract

    def doVariable(self, name: str, value=None) -> None:
        if name.endswith("a/href"): self._extract(value)

    @staticmethod
    def do_parse_file(filename:str) -> None:
        """Parse a file, without the app needing to create a parser object"""
        # will print all a href targets to stdout
        HTMLHREFExtractor().parse_file(filename)

    @staticmethod
    def do_parse_from(iterable) -> None:
        """Parse any iterable, without the app needing to create a parser object"""
        # default no handler, so TagParser will print each callback parameter
        # will print all a href targets to stdout
        HTMLHREFExtractor().parse_from(iterable)

#-------------------------------------------------------------------------------
class RuleParser(VariableParser):
    """Parse a file into a set of var=value and dispatch based on a rule table"""
    RULES = None # override in subclass

    def __init__(self, **kwargs):
        VariableParser.__init__(self, outbound_handler=self, **kwargs)
        self._rules = self.RULES

    def doVariable(self, name: str, value=None) -> None:
        if self._rules is None:
            print("no rules:", name, value)
            return
        rule = self._get_rule_for(name)
        if rule is None:
            pass # no matching rule
        elif callable(rule):
            rule(value)
            return # done
        elif isinstance(rule, tuple):
            if len(rule) > 0 and callable(rule[0]):
                rule[0](self, rule, value)
                return # done

        # default action, if not handled above
        ##print(str(rule), str(value) if value is not None else "")

    def _get_rule_for(self, name:str) -> callable or None:
        try:
            return self._rules[name]
        except KeyError:
            return None # no matching rule

    # No class methods, because it makes no sense to handle with no RULES
    # provide RULES in subclass and use class helper methods in that if necc.

#-------------------------------------------------------------------------------
class RecBuilder(RuleParser):
    HEADINGS = () # provide in subclass
    QUOTED   = () # provide in subclass

    @staticmethod
    def quoted(s:str) -> str:
        return "\"%s\"" % s

    def start_rec(self, rules, value) -> None:
        self._rec = {}

    def store(self, rules, value) -> None:
        name = rules[1]
        self._rec[name] = value

    def end_rec(self, rules, value) -> None:
        _,_ = rules, value  # argsused
        for i in range(len(self.HEADINGS)):
            key = self.HEADINGS[i]
            try:
                value = self._rec[key]
            except KeyError:
                value = "(none)"
            if self.QUOTED[i]:
                print(self.quoted(value), end=" ")
            else:
                print(value, end=" ")
        print()

    # No class methods, because it makes no sense to handle with no RULES
    # provide RULES in subclass and use class helper methods in that if necc.

#-------------------------------------------------------------------------------
class SQLGenerator(RuleParser):
    # default rules not helpful here

    def __init__(self, **kwargs):
        RuleParser.__init__(self, **kwargs)
        self._inserts = []
        self.start_rec()

    def _emptyTable(self, tableName: str) -> None:
        self._rec[tableName] = {}

    def _flushTable(self, tableName: str) -> None:
        """Flush any definition against self._rec into self._sql"""
        # This allows one-to-many record embedding
        if (self._rec[tableName] is not None) and (len(self._rec[tableName]) != 0):
            self._inserts.append(self._buildInsert(tableName, self._rec[tableName]))
            self._emptyTable(tableName)

    @staticmethod
    def _buildInsert(table, row) -> str:
        def csv(v: str, comma: bool) -> str:
            return "%s\n%s" % ("," if comma else "", str(v))

        def quoted(s: str) -> str:
            s = s.replace("'", "\\'")
            return "'%s'" % s

        ##print("build_insert from:", table, row)
        insert = ["INSERT INTO ", table, "("]

        first = True
        for name in row:
            insert.append(csv(name, not first))
            first = False
        insert.append("\n)\nVALUES\n(")

        first = True
        for name, value in row.items():
            insert.append(csv(quoted(value), not first))
            first = False
        insert += "\n);\n\n"
        return "".join(insert)

    def start_rec(self, rules=None, value=None) -> None:
        _, _ = rules, value  # argsused
        self._rec = {}

    def store(self, rules, value) -> None:
        tableName = rules[1]
        columnName = rules[2]
        if self._rec[tableName] is None:
            self._emptyTable(tableName)
        if not columnName in self._rec[tableName]:
            self._rec[tableName][columnName] = value
        else:
            self._rec[tableName][columnName].append(value)

    def end_rec(self, rule, value) -> None:
        _,_ = rule, value  # argsused
        for tablename in self._rec:
            self._flushTable(tablename)

    def get_inserts(self) -> list:
        return self._inserts

    def get_sql(self) -> str:
        return "\n".join(self._inserts)

    # No class methods, because it makes no sense to handle with no RULES
    # provide RULES in subclass and use class helper methods in that if necc.

#----- SIMPLE TEST HARNESS -----------------------------------------------------
import sys

def main(self, argv):
    DEFAULT_FILENAME = "test.html"
    DEFAULT_PARSER   = PathClassifier
    parser_class     = DEFAULT_PARSER

    if len(argv) == 0:
        parser_class.do_parse_file(DEFAULT_FILENAME)
    else:
        for arg in argv:
            if arg.startswith("--"):
                parser_name = arg[2:]
                try:
                    parser_class = getattr(self, parser_name)
                except AttributeError:
                    sys.stderr.write("unknown parser:%s\n" % parser_name)
                    exit(1)
            else:
                parser_class.do_parse_file(arg)

if __name__ == "__main__":
    main(sys.modules["__main__"], sys.argv[1:])

# END


