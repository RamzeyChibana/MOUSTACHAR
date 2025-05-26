import os
import json
from ollama import generate
import tqdm

# ——— CONFIGURATION ———
IMAGE_DIR   = "images"   # ← Update to your images folder
OUTPUT_JSON = "descriptions.json"
MODEL       = "gemma3:4b"
PROMPT      = "Describe this image and what they are and in what place in one sentence or two"

def describe_image(image_path: str) -> str:
    """
    Uses the ollama.generate binding to get a description from gemma.
    """
    # generate() takes model, prompt, and you can pass one or more image files.
    result = generate(
        model=MODEL,
        prompt=PROMPT,
        images=[image_path]
    )
    # The binding returns a list of choice objects; we grab the first choice's text.
  
    return result["response"]

def main():
    output = []
    pbar = tqdm.tqdm(total=len(os.listdir(IMAGE_DIR)))
    for fname in os.listdir(IMAGE_DIR):
        if not fname.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif")):
            continue

        full_path = os.path.join(IMAGE_DIR, fname)
        try:
            desc = describe_image(full_path)
        except Exception as e:
            print(f"Error describing {fname}: {e}")
            desc =f"{e}"
        output.append({
            "file": fname,
            "context": desc
        })
        pbar.update(1)
    pbar.close()
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"✅ Wrote {len(output)} entries to {OUTPUT_JSON}")

if __name__ == "__main__":
    main()
