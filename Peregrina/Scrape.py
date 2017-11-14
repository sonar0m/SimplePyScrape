import sys
import re
import inspect
import datetime

try:
    import urllib2
except:
    import urllib.request as urllib2
from copy import deepcopy, Error


# deperacated
class Scrape:
    """
		Scrape class, added's value for recived data as recursive

		cfgs = {"type":"string",
			   "name":"scrape name",
			   "cfg":{"Sub":subscrapevar},
			   "flags":[1, "start","end"],
			   "filter":"[a-zA-Z0-9]+" #not implimented
			   }


		scrape=Scrape(str(url))
		scrape.getSource()
		scrape.setConfig(cfgs)
		scrape.doConfig()
		scrape.output  #this is a {} with names from your configurations

	"""
    cashe = {}
    casheDetla = datetime.timedelta(hours=-1)

    def __init__(self, url="", source=""):
        '''
		url is the url to pull from
		can also use source if you have a subscrape or a test/ file
		type
		'''
        self.source = ""
        self.output = {}
        self.url      = ""
        self.name = ""  # should be a string0
        self.scrapeType = ""
        self.commands = {}
        self.flags = []
        self.filter= ""  # should be string
        if Scrape.cashe==None:
            Scrape.cashe={}
        self.output = {}
        self.source = ""
        self.url = url
        if (type(source) == type("")):
            self.source = source;
        else:
            #print(source)
            raise TypeError("source")
        ''' testing
		self.getSource()
		'''

    def getSource(self):
        hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}
        if self.url in Scrape.cashe:
            if Scrape.cashe[self.url][1] > datetime.datetime.now() +Scrape.casheDetla:
                #print("DEBUG(getSource): " + "is true"+"\r\n"+Scrape.cashe[self.url][0][:128])
                self.source=Scrape.cashe[self.url][0]
                return
        if (self.url != None):
            req = urllib2.Request(self.url, headers=hdr)
            self.source = str(urllib2.urlopen(req).read())
        elif (self.source != None and type(self.source) == type("")):
            print("source defined")
        else:
            raise NameError("Source Not Defined and URL not given.")
        if self.source == None:
            raise NameError("Source Not Found")
        Scrape.cashe[self.url]=(self.source, datetime.datetime.now())#todo add time check as well

    def setConfig(self, scrapeCfg={}):
        '''
        flags = [num repeat, start, end]
		"type": "string|regex",  can be blank but would default to str
		"name": "url", 
		"cfg": {}, #nested configurations
		"flags": urlflag
		'''
        if (type(scrapeCfg["name"]) == type("")):
            self.name = scrapeCfg["name"]
        self.commands = scrapeCfg["cfg"]
        self.scrapeType = scrapeCfg["type"].lower().split(".")
        self.flags = scrapeCfg["flags"]
        try:
            self.filter = scrapeCfg["filter"]
        except KeyError:
            self.filter = ""


    def doConfig(self):
        # if -1 while not missing?
        #print(self.source)
        if self.flags[0] == -1:
            i = 0
            while True:
                found = self.findOutput()
                if found != -1:  # while not returning not found
                    self.output[self.name + str(i)] = found
                else:
                    break
                i = i + 1
        else:#count loops
            for i in range(self.flags[0]):
                self.output[self.name + str(i)] = self.findOutput()
            # need to do self.filter()
        if self.commands != None and self.commands != {}: #if comfigurations is empty
            keys = self.commands.keys()
            subScrape = {}
            for c in keys:
                for ou in self.output.keys():
                    if type(self.output[ou]) == type({}):
                        ''' need to fix and compete dealing with sub scrapes'''
                        continue
                    subScrape[ou + "|" + c] = Scrape(source=self.output[ou])
                    subScrape[ou + "|" + c].setConfig(self.commands[c])
                    subScrape[ou + "|" + c].doConfig()

                # self.output[ou+"|"+c]=subScrape.output
            self.output.update((s, subScrape[s].output) for s in subScrape.keys() if s not in self.output.keys())
        # End find source
        # utility start
        # start of Find area

    def findOutput(self):
        f = {"regex": self.findRegex, "string": self.findString}
        type = "string"
        if "regex" in self.scrapeType:
            type = "regex"
        if self.filter == None or self.filter == "":
            self.filter = ""
        ret = ""
        if len(self.flags) > 3:
            ret = f[type](self.flags[1], self.flags[2], self.flags[3])
        else:
            ret = f[type](start=self.flags[1], end=self.flags[2])
        if ret !=-1:
            ret = self.filtering(ret)
        return ret

    def findString(self, start="", startText="", end=""):
        # print "plain"
        if self.source.find(start) == -1:
            return -1  # blank
        st = 0
        if start != "":
            st = self.source.find(start)
        stt = 0
        if startText != "":
            stt = self.source[st + len(start):].find(startText) + st + len(start)
        else:
            stt = st
            startText = start
        if self.source[stt + len(startText):].find(end) == -1:
            return -1
        en = self.source[stt + len(startText):].find(end)
        if en == -1:
            return -1
        if end != "":
            en = self.source[stt + len(startText):].find(end) + stt + len(startText)
        else:
            en = len(self.source)
        s = self.source[stt + len(startText):en]
        sourceTmp = self.source[:]
        sourceTmp = sourceTmp[:st] + sourceTmp[en + len(end):]
        self.source = sourceTmp
        return s

    def findRegex(self, start="", startText="", end=""):
        '''
		find's a reg ex part of the source
		start start part of the text
		start text optional finds the
		'''
        st = 0
        rstart = re.search(start, self.source)
        if rstart != None:
            st = rstart.start()
        if rstart == None:
            return -1
        stt = 0
        rstartText = re.search(startText, self.source[st + len(rstart.group()):])
        if startText != "":
            stt = rstartText.start() + st + len(rstart.group())
        else:
            stt = st
            startText = start
        rend = re.search(end, self.source[stt + len(rstartText.group()):])
        if rend == None:
            return ""
        en = 0
        if rend == None:
            return -1
        if end != "":
            en = rend.start() + stt + len(rstartText.group())
        else:
            en = len(self.source)
        s = self.source[stt + len(rstartText.group()):en]
        sourceTmp = self.source[:]
        sourceTmp = sourceTmp[:st] + sourceTmp[en + len(rend.group()):]
        self.source = sourceTmp
        return s

    def remove(self, rm):
        '''
		not used
		'''
        if self.source.find(rm) >= 0:
            return self.source[:self.source.find(rm)] + self.source[self.source.find(rm) + len(rm):]
        return self.source

    def filtering(self, source):
        '''
		still to do
		'''
        invert = False
        filter = self.filter
        if self.filter[:9].lower() == "(-invert)":
            invert = True
            filter = self.filter[9:]
        if invert:
            ret = re.findall(filter, source)
            if len(ret) > 0: return "".join(ret)
        else:
            ret = re.sub(filter, "", source)
        if len(ret) > 0: return ret


class Item(list):
    def __init__(self, sep, name, rowinfo):
        self.seperator = sep
        list.__init__([])
        self.itemDetails = {}
        self.itemInfo = name
        self.rowinfo = rowinfo

    def append(self, *args, **arg):
        input = [value for value in args if type({}) == type(value) and len(value) == 3]
        if len(args) > 0 and type(args[0]) == type(self):
            for a in args[0]:
                self.append(**a)
        if len(input) > 0:
            list.append(self, input)
        if len(arg) == len(self.rowinfo.split(self.seperator)):
            list.append(self, arg.copy())

    def __repr__(self):
        '''Display's the it's accourding to the seprator and CSV format.'''
        ret = ""
        join = lambda f, d: ("{" + ("}" + self.seperator + "{").join(f.split(str(self.seperator))) + "}").format(**d)
        if len(self.itemInfo.split(str(self.seperator))) > 0 and len(self.itemDetails) > 0:
            ret += join(self.itemInfo, self.itemDetails) + "\r"
        ret += self.rowinfo
        ret += "\r"
        for r in self:
            if len(self.rowinfo.split(str(self.seperator))) > 0 and len(r):
                ret = ret + join(self.rowinfo, r) + "\r"
        return ret

    def __str__(self):
        return self.__repr__()
		
def eprint(input):
	print("debug("+str(inspect.getouterframes( inspect.currentframe() )[1][3])+"): "+ str(input))
# end utility
