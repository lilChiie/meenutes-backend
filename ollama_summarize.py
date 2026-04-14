import requests

def summarize_text(text):
    print("[Ollama] Memproses teks...")
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3.2",
                "prompt": f"Buat ringkasan singkat dalam bentuk poin:\n{text}"
            },
            stream=False
        )
        result = response.json().get("response", "")
        return result.strip()
    except Exception as e:
        print("Error summarizing:", e)
        return "Gagal membuat ringkasan."
