__author__ = 'marcus'
# automated testing
import Scrape


def test():
    s = Scrape.Scrape(source="test 1,test 2,test 3,")
    c = [-1, "test", ","]
    cs = {"type": "string",
          "name": "search",
          "cfg": {},
          "flags": c,
          "filter": " "}
    s.setConfig(cs)
    s.doConfig()
    print(s.output)


if __name__ == "__main__":
    test()
