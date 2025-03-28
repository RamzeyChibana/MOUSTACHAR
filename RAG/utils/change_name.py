import json


file_name = "laws_Finfo.json"
name = "code de l'information"
with open(f"laws_json\\{file_name}","r",encoding="utf-8") as file :
    laws = json.load(file)


for law in laws :
    law["metadata"]["file"]=name

with open(f"new_laws\\{file_name}", "w", encoding="utf-8") as f:
    json.dump(laws, f, ensure_ascii=False, indent=4)




