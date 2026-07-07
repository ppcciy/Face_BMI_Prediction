import os
import sys
import bs4
import csv
from operator import methodcaller
from collections import OrderedDict
import lxml.html
import lxml.html.html5parser
import re
import sys
import warnings
warnings.filterwarnings('error')

def escstr(s):
    return s.strip().replace("\n", "\\n")\
            .replace("\r", "\\r")\
            .replace('"', '\\"')\
            .replace(";", "\;").encode("utf-8") #takes a string and makes it suitable for CSV - NB! this function is very poorly implemented TODO

def arr2csvR(arr):
    rc = ""
    for i in arr:
        rc += escstr(i) + ";"
    return rc + '\n' #no need for unterminated rows this time around

def tohdr(s):
    return re.sub(r' +', '_', re.sub(r'[^a-zA-Z0-9]', ' ', s.lower()).strip()).encode("utf-8")
#"Some header: " -> "some_header"

physicalcols = {'next': 0}
admissioncols = {'next': 0}
statuscols = {'next': 0}
sentencingcols = {'next' :0}

for fn in sorted(os.listdir("inmates"))[:30000]: #for debug: add [:30000] or some such to make it go faster, note that this might could cause errors in below if it's too low
    first_sentencing = True #only for sentencing table, all are identical so we only need column headers once
    if fn.endswith(".html"):
        r = lxml.html.parse(os.path.join("inmates/", fn)).getroot()
        main = r[1][0][4][0][0][0] #all the fun stuff happens here
        if len(main) == 1:
            continue #this inmate doesn't exist
        indices = {'physical': None, 'admission': None, 'status': None, 'sentencing': None} #their indices in the table
        for i, item in enumerate(main):
            text = item.text_content()
            if len(item) == 1:
                if text == "PHYSICAL PROFILE": #it's a header
                    indices["physical"] = i+1
                elif text == "ADMISSION / RELEASE / DISCHARGE INFO": #headers always are immediately followed by their subject
                    indices["admission"] = i+1
                elif text == "SENTENCING INFORMATION":
                    indices["sentencing"] = i+1
            if text.startswith("Parent Institution: ") or text.startswith("Alias: "): #all have parent inst, but some have alias, but this covers 100% of cases
                indices['status'] = i
        if None in indices.values(): #it failed to find one of the always-present elements
            print "Failed at " + fn
            print indices
            quit(1)
        for i in main[indices["physical"]]: #find the left-hand side, mark them in order of appearance - do this so that they may be used as column headers
            if i[0].text_content() not in physicalcols:
                physicalcols[i[0].text_content()] = physicalcols['next']
                physicalcols['next'] += 1
        for i in main[indices["admission"]]:
            if i[0].text_content() not in admissioncols:
                admissioncols[i[0].text_content()] = admissioncols['next']
                admissioncols['next'] += 1
        for i in main[indices["status"]]:
            if i[0].text_content() not in statuscols and len(i[0].text_content().strip()): #status has an empty spacer for some reason
                statuscols[i[0].text_content()] = statuscols['next']
                statuscols['next'] += 1
        for i in main[indices['sentencing']]:
            if len(i[0].text_content().strip()):
                if first_sentencing:
                    if i[0].text_content() not in sentencingcols:
                        sentencingcols[i[0].text_content()] = sentencingcols['next'] #the special handling (see above)
                        sentencingcols['next'] += 1
                else:
                    assert i[0].text_content() in sentencingcols
        first_sentencing = False

print physicalcols
print admissioncols
print statuscols 
print sentencingcols 

files = {
'person': open("csv/person.csv", 'w'),
##'physical': open("csv/physical.csv", 'w'),
##'admission': open("csv/admission.csv", 'w'),
'sentencing': open("csv/sentencing.csv", 'w'),
#'warrant': open("csv/warrant.csv", 'w'),
#'warning': open("csv/warning.csv", 'w'),
#'captured': open("csv/captured.csv", 'w'),
'marks': open("csv/marks.csv", 'w'),
##'status': open("csv/status.csv", 'w'),
} #file table

files['marks'].write(arr2csvR(['id', 'mark']))
##files['status'].write(arr2csvR(['id'] + map(tohdr, map(lambda i: statuscols.keys()[statuscols.values().index(i)], range(statuscols['next'])))))
##files['physical'].write(arr2csvR(['id'] + map(tohdr, map(lambda i: physicalcols.keys()[physicalcols.values().index(i)], range(physicalcols['next'])))))
##files['admission'].write(arr2csvR(['id'] + map(tohdr, map(lambda i: admissioncols.keys()[admissioncols.values().index(i)], range(admissioncols['next'])))))
files['person'].write(arr2csvR(['id'] + map(tohdr, map(lambda i: physicalcols.keys()[physicalcols.values().index(i)], range(physicalcols['next']))) +
                                        map(tohdr, map(lambda i: admissioncols.keys()[admissioncols.values().index(i)], range(admissioncols['next']))) +
                                        map(tohdr, map(lambda i: statuscols.keys()[statuscols.values().index(i)], range(statuscols['next'])))
))
    
files['sentencing'].write(arr2csvR(['id'] + map(tohdr, map(lambda i: sentencingcols.keys()[sentencingcols.values().index(i)], range(sentencingcols['next'])))))
#write out all the headers

for fn in sorted(os.listdir("inmates")): #second pass, we now know all our headers
    if fn.endswith(".html"):
#        r = lxml.html.html5parser.parse(os.path.join("inmates/", fn)).getroot()
        r = lxml.html.document_fromstring(
            lxml.html.tostring(
                lxml.html.html5parser.parse(
                    os.path.join("inmates/", fn),
                    parser=lxml.html.html5parser.html_parser) #note - ignore the warning that comes up
                ))[0][0]
        #this kludge is because lxml's parser poorly handles malformed documents, such as when a < character is used in text without escaping, and the
        #html5lib parser doesn't provide a normal tree with methods like text_content() ... for some reason we need to descend 2 levels as well
        main = r[1][0][0][4][0][0][0] #NB! with lxml parser this is 104000, not 1004000
        if len(main) == 2:
            continue #this inmate doesn't exist
        id = ''
        indices = {'physical': None, 'admission': None, 'sentencing': None, 'status': None}
        classified = {} #"do we know what item X is?"
        for i, itemp in enumerate(main.findall(".//table")): #if it has a warrant, the rest gets put into a font tag, thus a recursive search must be done
            if len(itemp):
                item = itemp[0]
                text = item.text_content()
                if len(item) == 1:
                    if text == "PHYSICAL PROFILE": #it's a header
                        indices['physical'] = i+1
                        classified[i] = True
                        classified[i+1] = True
                    elif text == "ADMISSION / RELEASE / DISCHARGE INFO":
                        indices['admission'] = i+1
                        classified[i] = True
                        classified[i+1] = True
                    elif text == "SENTENCING INFORMATION":
                        indices["sentencing"] = i+1
                        classified[i] = True
                        classified[i+1] = True
                    elif re.match("[A-Za-z][0-9]{5} - ", text): #it's an ID
                        id = text[0:6]
                        classified[i] = True
                    elif text.startswith("Warrant Information"): #we don't parse this but at least we know what it is
#                    indices['warrant'] = i
                        classified[i] = True
                    elif text.startswith("Date of Birth: "): #see above
                        "do nothing, we already have physical profile"
                    elif text.startswith("The information"): #disclaimer at bottom of page
                        classified[i] = True
                    elif text.startswith("IDOC TOLL FREE"): #warning "Armed and dangerous - do not apprehend"
                        classified[i] = True
                    elif text == "Captured":
                        classified[i] = True
                        "do nothing"
                    else:
                        print "unexpected text: " + text.encode('utf-8')
                        print fn
                        quit(2)
                elif text.startswith("Parent Institution: ") or text.startswith("Alias: "):
                    indices['status'] = i
                    classified[i] = True

        if None in indices.values(): #"we've found all their indices"
            print fn
            quit(9)
        assert len(id)
        arrs = {'physical': [], 'admission': [], 'status': []} #we always want ID so might as well put it here
        for i, itemp in enumerate(main.findall(".//table")):
            if len(itemp):
                item = itemp[0]
                if i not in classified:
                    if len(item): #no spacers
                        assert len(item) != 1 #all 1-len items are classified
                        text = item.text_content()
                        if text.startswith(" MARKS, SCARS, & TATTOOS"):
                            for m in item[1:]:
                                files['marks'].write(arr2csvR([id, m.text_content()]))
                        else:
                            print "unexpected text: " + text
                            quit(3)
                elif i in indices.values():
                    type = indices.keys()[indices.values().index(i)]
                    if type == 'sentencing':
                        #9 fields and a spacer, last also has the spacer
                        if len(item) % 9 != 0:
                            print fn
                            for i in item:
                                print i.text_content().encode("utf-8")
                            print "not divisible by 9"
                            quit(6)
                        for i in range(len(item)/9): #for each "block"...
                            files['sentencing'].write(arr2csvR([id] + map(lambda x: x[1].text_content(), item[9*i:9*i+8]))) #for each item in the block, put the right-hand side/value to CSV
                    else:
                        c = {'physical': physicalcols,
                            'admission': admissioncols,
                            'status': statuscols}[type] #c gets {"Header: " n, 'next': n_max}
                        for k in range(c['next']):
                            found = False
                            for m in item:
                                if len(m[0].text_content().strip()) and c[m[0].text_content()] == k: #it it's not a spacer and matches our desired header
                                    found = True
                                    if m[0].text_content() == 'Sex Offender Registry Required':
                                        arrs[type] += ["true"] #there's no m[1], so we might as well handle it special case
                                    else:
                                        if type == 'physical':
                                            if m[0].text_content() == "Weight:  ":
                                                txt = m[1].text_content()
                                                if txt[-5:] == " lbs.":
                                                    arrs[type] += [txt[0:-5]] #"111 lbs." -> 111
                                                elif txt == "Not Available":
                                                    arrs[type] += ["N/A"]
                                                else:
                                                    print "unknown weight " + txt
                                                    quit(4)
                                            elif m[0].text_content() == "Height: ":
                                                txt = m[1].text_content()
                                                if re.match(". ft. .. in.", txt):
                                                    foot = int(txt[0])
                                                    inch = int(txt[6:8])
                                                    arrs[type] += [str(foot*12+inch)]
                                                elif txt == "Not Available":
                                                    arrs[type] += ["N/A"]
                                                else:
                                                    print "unknown weight " + txt
                                                    quit(5)
                                            else:
                                                if not len(m) > 1:
                                                    arrs[type] += ['']
                                                else:
                                                    arrs[type] += [m[1].text_content()]
                                        else:
                                            if not len(m) > 1:
                                                arrs[type] += ['']
                                            else:
                                                arrs[type] += [m[1].text_content()]
                            if not found:
                                arrs[type] += ['']
                else:
                    assert i in classified
        arr = [id]
        for col in 'physical', 'admission', 'status':
            arr += arrs[col]
        files['person'].write(arr2csvR(arr))
