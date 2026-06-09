import requests

def summarize_text(text):
    print("[Ollama] Processing text...")
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3.2",
                "prompt": f"Create a brief summary in bullet points:\n{text}"
            },
            stream=False
        )
        result = response.json().get("response", "")
        return result.strip()
    except Exception as e:
        print("Error summarizing:", e)
        return "Failed to generate summary."
