from greekdict import WikiWordGraph
import srt
import string
import glob
import json
import sqlite3
from googletrans import Translator


css = """
    <!DOCTYPE html>
    <html>
    <head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
    .dropbtn {
      background-color: #04AA6D;
      color: white;
      padding: 16px;
      font-size: 16px;
      border: none;
    }

    .dropdown {
      position: relative;
      display: inline-block;
    }

    .dropdown-content {
      display: none;
      position: absolute;
      background-color: #f1f1f1;
      min-width: 160px;
      box-shadow: 0px 8px 16px 0px rgba(0,0,0,0.2);
      z-index: 1;
    }

    .dropdown-content a {
      color: black;
      padding: 12px 16px;
      text-decoration: none;
      display: block;
    }

    .dropdown-content a:hover {background-color: #ddd;}

    .dropdown:hover .dropdown-content {display: block;}

    .dropdown:hover .dropbtn {background-color: #3e8e41;}
    </style>
    </head>
    <body>
"""

print("importing graph...")
word_graph = WikiWordGraph('word_graph.json')
print("imported")

print("importing wikdict...")
con = sqlite3.connect("el-en.sqlite3")
cur = con.cursor()
print("imported")

print("connecting to google translate...")
translator = Translator()

path = r'/Users/merlinn/Downloads/avatar/Book 1_ Νερό/*.srt'
files = glob.glob(path)

def get_norm(item):
    if item['norm'] == "[]" and item['pos'] != "[]":
        norm = item['search']
    if item['norm'] != "[]":
        norm = json.loads(item['norm'].replace("\'","\""))[0]
    if item['norm'] == "[]" and item['pos'] == "[]":
        norm = item['search']

    #hacky bullshit
    if norm in ["ο","η","το","τον","τη","την","οι","τους","τις","τα","των","τος"]:
        return ""
    if norm in ["αυτός", "αυτή", "αυτό", "αυτοί", "αυτές", "αυτά", "αυτού", "αυτής", "αυτών", "αυτούς", "να","απο", "δεν", "δε", "και"]:
        return ""
    return norm

#iterate through srt files in directory
for file in files:
    #print(file)
    original_sub_file = open(file)
    new_sub_file = open(file + ".html", "w")
    print("Starting " + (str(file)))
    new_sub_file.write(css)
    parser = srt.parse(original_sub_file)
    for subline in parser:
        for word in (subline.content).split():

            print(word)
            #normalize word for searching

            #lowercase
            modified_word = word.lower()

            #strip punctuation
            modified_word = modified_word.translate(str.maketrans('', '', string.punctuation))

            #create debug object
            item = {'search': modified_word, 'norm': str(word_graph[modified_word]), 'pos': str(word_graph.get_pos(modified_word))}
            norm = get_norm(item)

            html = f"<div class='dropdown'><pre><h3><button class='dropbtn'>{str(word)}</h3></button><div class='dropdown-content'>"
            if norm != "":
               #google translate
               googleres = translator.translate(norm).text

               #sql lite lookup, limit to 5
               query = f"SELECT written_rep,trans_list FROM translation WHERE written_rep LIKE '%{norm}%' LIMIT 3"
               cur.execute(query)
               sql_result = str(cur.fetchall())
               html += f"SEARCH: {str(item)}\n"
               html += f"WIKDICT: {str(sql_result)}\n"
               html += f"GOOGLE: {str(googleres)}\n"
               html += f"<a href = 'https://www.wordreference.com/gren/{norm}' target='_blank'>WordReference</a> \t <a href = 'https://en.wiktionary.org/wiki/{norm}' target='_blank'>Wiki</a> \t <a href = 'https://translate.google.com/?sl=el&tl=en&text={norm}&op=translate' target='_blank'>Google Translate</a>\n"
               html += f"<a href = 'https://www.google.com/search?q={norm}' target='_blank'>Google Search</a>\n"
               html += f"<a href = 'https://forvo.com/search/{norm}/' target='_blank'>Forvo</a>"
            html += f"</pre></div></div>"
            new_sub_file.write(html)
        new_sub_file.write("<br>")
    original_sub_file.close()
    new_sub_file.close()
    print("Finished with " + (str(original_sub_file)))
