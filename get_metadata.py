import json 

with open("new_laws/All_laws.json","r",encoding="utf-8") as file :
    laws = json.load(file)

chapters = set()
fields = set()

for law in laws:
    chapter =law["metadata"]["chapter"]
    field =law["metadata"]["file"]
    chapters.add(chapter)
    fields.add(field)

with open("new_laws/chapters.txt","w",encoding="utf-8") as file :
    for chapter in list(chapters):
        file.write(chapter+"\n")
with open("new_laws/fields.txt","w",encoding="utf-8") as file :
    for field in list(fields):
        file.write(field+"\n")



