import fitz  # PyMuPDF
import pandas as pd
import tabula
# Open PDF
import json 




with open("laws_json\\Code_Timbre.json","r",encoding="utf-8") as file :
    laws = json.load(file)
print(len(laws))





