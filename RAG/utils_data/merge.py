import json 
import os 
import numpy as np
import pandas as pd

files = os.listdir("new_laws")

laws = []
for file in files:
 
    with open(f"new_laws\\{file}","r",encoding="utf-8") as file :
        law = json.load(file)
        laws+=law

print(f"there is {len(laws)}")

with open("new_laws/All_laws.json", "w", encoding="utf-8") as f:
    json.dump(laws, f, ensure_ascii=False, indent=4)



