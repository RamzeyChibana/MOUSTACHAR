import json 
import os 
import numpy as np
import pandas as pd

files = os.listdir("laws_json")

laws = []
for file in files:
 
    with open(f"laws_json\\{file}","r",encoding="utf-8") as file :
        law = json.load(file)
        laws+=law

print(f"there is {len(laws)}")

with open("laws_json/All_laws.json", "w", encoding="utf-8") as f:
    json.dump(laws, f, ensure_ascii=False, indent=4)



