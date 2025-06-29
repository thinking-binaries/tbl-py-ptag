#! /usr/bin/env python3
# news.py  23/06/2025  D.J.Whale

import ptag

#class NewsParser(ptag.PathClassifier):
#class NewsParser(ptag.VariableParser):
class NewsParser(ptag.RuleParser):
    RULES = {
        #----- CHANNEL
        ##"/rss/channel":
        "/rss/channel/title/":                      lambda v:print("title:", v),
        "/rss/channel/link/":                       lambda v:print("link:", v),
        "/rss/channel/description/":                lambda v:print("description:", v),
        "/rss/channel/language/":                   lambda v:print("language:", v),
        "/rss/channel/lastBuildDate/":              lambda v:print("lastBuildDate:", v),
        "/rss/channel/copyright/":                  lambda v:print("copyright:", v),
        "/rss/channel/image/url/":                  lambda v:print("url:", v),
        "/rss/channel/image/title/":                lambda v:print("title:", v),
        "/rss/channel/image/link/":                 lambda v:print("link:", v),
        "/rss/channel/image/width/":                lambda v:print("width:",v),
        "/rss/channel/image/height/":               lambda v:print("height:", v),
        "/rss/channel/ttl/":                        lambda v:print("ttl:", v),
        #----- ATOM
        ##"/rss/channel/atom:link":
        "/rss/channel/atom:link/href":              lambda v:print("atom href:", v),
        "/rss/channel/atom:link/rel":               lambda v:print("atom rel:", v),
        "/rss/channel/atom:link/type":              lambda v:print("atom type:", v),
        ##"/rss/channel/atom:link~":
        #---- ITEM
        ##"/rss/channel/item":
        "/rss/channel/item/title/":                 lambda v:print("item title:", v),
        "/rss/channel/item/description/":           lambda v:print("item desc:", v),
        "/rss/channel/item/link/":                  lambda v:print("item link:", v),
        "/rss/channel/item/guid/isPermaLink":       lambda v:print("item guid perma:", v),
        "/rss/channel/item/guid/":                  lambda v:print("item guid:", v),
        "/rss/channel/item/pubDate/":               lambda v:print("item pubdate:", v),
        "/rss/channel/item/media:thumbnail/width":  lambda v:print("item tnwidth:", v),
        "/rss/channel/item/media:thumbnail/height": lambda v:print("item thheight:", v),
        "/rss/channel/item/media:thumbnail/url":    lambda v:print("item tnurl:", v),
        "/rss/channel/item~":                       lambda v:print(),
        ##"/rss/channel~":
        }

    @staticmethod
    def do_parse_file(filename:str) -> None:
        """Parse a file, without the app needing to create a parser object"""
        NewsParser().parse_file(filename)

    @staticmethod
    def do_parse_from(iterable) -> None:
        """Parse any iterable, without the app needing to create a parser object"""
        NewsParser().parse_from(iterable)

if __name__ == "__main__":
    # wget -O news.xml http://feeds.bbci.co.uk/news/technology/rss.xml
    FILENAME = "news.xml"
    NewsParser.do_parse_file(FILENAME)

# END