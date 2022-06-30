from greekdict import WikiWordGraph
import srt
import string
import glob
import json
import sqlite3
from googletrans import Translator

print("importing graph...")
word_graph = WikiWordGraph('word_graph.json')
print("imported")

print("importing wikdict...")
con = sqlite3.connect("el-en.sqlite3")
cur = con.cursor()
print("imported")

print("connecting to google translate...")
translator = Translator()

allwords = []

path = r'/Users/merlinn/Downloads/avatar/Book 1_ Νερό/*.srt'
files = glob.glob(path)

#iterate through srt files in directory
for file in files:
    #print(file)
    input_file = open(file)
    parser = srt.parse(input_file)
    #print(list(parser))
    for subline in parser:
        for word in (subline.content).split():
            word = word.lower()
            word = word.translate(str.maketrans('', '', string.punctuation))
            new = {'search': word, 'norm': str(word_graph[word]), 'pos': str(word_graph.get_pos(word))}
            #print(word + "\t" + str(word_graph[word]) + str(word_graph.get_pos(word)))
            allwords.append(new)
    input_file.close()


print("length of orig list is: " + str(len(allwords)))

####Filter by search key and remove duplicates######
key = "search"
memo = set()
newlist = []
    

for item in allwords:
    if item[key] not in memo:
        newlist.append(item)
        memo.add(item[key])
###################################################


print("length of next list is: " + str(len(newlist)))

####Filter by norm key and remove duplicates######
key = "norm"
#memo = set()
final = []
    
for item in newlist:
    if item[key] == "[]":
        final.append(item)
        continue
    temp = json.loads(item['norm'].replace("\'","\""))[0]
    if temp not in memo:
        final.append(item)
        memo.add(temp)
##################################################

input_file = open("./words.html", 'w')
input_file.write("<html>")

count = 0
for item in final:
    count = count + 1
    if item['norm'] == "[]" and item['pos'] != "[]":
        norm = item['search']
    if item['norm'] != "[]":
        norm = json.loads(item['norm'].replace("\'","\""))[0]
    if item['norm'] == "[]" and item['pos'] == "[]":
        norm = item['search']

    #query sql lite dictionary
    query = f"SELECT written_rep,trans_list FROM translation WHERE written_rep LIKE '%{norm}%'"
    cur.execute(query)
    sqlres = str(cur.fetchall())

    #google translate
    googleres = translator.translate(norm).text
     
    html = f"<br><pre><h3>{count} {str(norm)}</h3>" \
           f"SEARCH: {str(item)}\n" \
           f"WIKDICT: {str(sqlres)}\n" \
           f"GOOGLE: {str(googleres)}\n" \
           f"<a href = 'https://www.wordreference.com/gren/{norm}' target='_blank'>WordReference</a> \t <a href = 'https://en.wiktionary.org/wiki/{norm}' target='_blank'>Wiki</a> \t <a href = 'https://translate.google.com/?sl=el&tl=en&text={norm}&op=translate' target='_blank'>Google Translate</a>\n" \
           f"<a href = 'https://www.google.com/search?q={norm}' target='_blank'>Google Search</a>\n" \
           f"<a href = 'https://forvo.com/search/{norm}/' target='_blank'>Forvo</a>" \
           f"</pre></html>"
    input_file.write(html)
    print(item)
input_file.close()

print("length of final list is " + str(len(final)))
 
