import fitz  # PyMuPDF
import pandas as pd
import tabula
import json
import re
# Open PDF

doc = fitz.open("D:\df\\ai\RAG\laws\FPenal.pdf")
field = "Code De Penalite"
start = 9
stop = 380

target_fontsize =  6.960000038146973
title_color = 255  # Black
target_bbox = 100
art_font = "TimesNewRoman,Bold"
text_font = "TimesNewRoman"


x = []
laws = []
current_law = ""
current_chapter = ""
article_text = ""
law_title = ""
law_text = []
art_pattern = r"Art\.?\s?.*(−|-|—)"  
i=0
def store(article,content,chapter):
    laws.append({article:content,"metadata":{"chapter":chapter,"file":field}})
    
for page_idx,page in enumerate(doc):
       
    
    if start-1<=page_idx<stop:
       
        for block in page.get_text("dict")["blocks"]:
            if "lines" in block:
                for line in block["lines"]:
            
                    for span in line["spans"]:
                        fontsize = span["size"]
                        color_int = span["color"]
                        font = span["font"]
                        bbox = span["bbox"][0]
                        x.append(span["font"])
                        
             
                        text = span["text"].strip()

                        if color_int == title_color and text!="":
                            current_chapter = text
                            
                            
                    
                        #font == art_font and color_int != title_color and bbox < target_bbox and text != "" and ("Art." in text or "Article" in text) 
                        if font == art_font and color_int==0 and text!= "" and ("Art." in text or "Article" in text) :
                            if law_title != "":
                                store(law_title,"".join(law_text),current_chapter)
                      
                            law_title = span["text"].strip()
                            law_text = []
                            continue
                            
                        if font in [text_font,art_font] and color_int == 0 and text != "" :
                            law_text.append(span['text'].strip())
store(law_title,"".join(law_text),current_chapter)


with open("laws_json/laws_FPenal.json", "w", encoding="utf-8") as f:
    json.dump(laws, f, ensure_ascii=False, indent=4)
       
print(pd.unique(x))