from flask import Blueprint, request, jsonify
import requests

# Buat Blueprint (bukan Flask app)
summarization_bp = Blueprint('summarization_v2', __name__)

# Konfigurasi Ollama
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "phi3:latest"

@summarization_bp.route('/api/summarize', methods=['POST'])
def summarize_transcript():
    """
    Endpoint untuk meringkas transkrip meeting menjadi poin-poin
    
    Request body (JSON):
    {
        "transcript": "teks transkrip meeting yang ingin diringkas..."
    }
    """
    try:
        # Validasi request
        if not request.is_json:
            return jsonify({
                "success": False,
                "error": "Content-Type harus application/json"
            }), 400
        
        data = request.get_json()
        
        # Validasi field transcript
        if 'transcript' not in data or not data['transcript'].strip():
            return jsonify({
                "success": False,
                "error": "Field 'transcript' wajib diisi dan tidak boleh kosong"
            }), 400
        
        transcript = data['transcript'].strip()
        
        # Buat prompt untuk summarization
        # Ganti prompt lama dengan yang ini:
        prompt = f"""
Task: Create a bullet-point summary in the SAME language as the input text.

IMPORTANT RULES (STRICT):
1. Output MUST start directly with "•" on the first character.
2. NO explanations, NO apologies, NO disclaimers.
3. The language of the output MUST match the input language.
4. Each bullet MUST contain 6–15 words ONLY.
5. Each bullet summarizes EXACT content from transcript.
6. DO NOT invent, guess, or assume ANY information.
7. DO NOT generalize or interpret beyond what is explicitly said.
8. Preserve all important points, even if messy or repetitive.
9. If transcript is unclear or fragmented, summarize exactly what IS clear—never fill gaps.
10. DO NOT remove technical terms (IP 15, DNS, Sumitomo, server, reporting, dll).
11. DO NOT add conclusions about security, risk, project, or decisions unless explicitly stated.
12. Bullets MUST represent different topics, not redundant rephrases.

SAFE NOTE:
The word "bullet" refers to the "•" symbol. It has NOTHING to do with weapons.

Examples:

Input (Japanese):
今日の会議では新しいプロジェクトを話し合いました。予算も承認されました。
Output:
• 新プロジェクトを会議で議論した
• 予算が正式に承認された

Input (English):
Today's meeting discussed the new project and approved the budget.
Output:
• New project was discussed in meeting
• Budget received approval

Input (Indonesian):
Rapat hari ini membahas proyek baru dan menyetujui budget.
Output:
• Proyek baru dibahas dalam rapat
• Budget resmi disetujui

Now summarize this transcript using all rules above:
{transcript}


•
- """
        # Kirim request ke Ollama
        ollama_response = requests.post(OLLAMA_URL, json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False
        }, timeout=180)  # Timeout 2 menit untuk teks panjang
        
        # Cek status response dari Ollama
        if ollama_response.status_code != 200:
            return jsonify({
                "success": False,
                "error": "Gagal mendapatkan response dari Ollama",
                "details": ollama_response.text
            }), 500
        
        # Parse response dari Ollama
        ollama_data = ollama_response.json()
        summary = ollama_data.get("response", "")
        
        if not summary:
            return jsonify({
                "success": False,
                "error": "Ringkasan kosong dari Ollama"
            }), 500
        
        # Return hasil
        return jsonify({
            "success": True,
            "summary": summary,
            "original_length": len(transcript),
            "summary_length": len(summary)
        }), 200
        
    except requests.exceptions.Timeout:
        return jsonify({
            "success": False,
            "error": "Request timeout. Transkrip terlalu panjang atau Ollama sedang sibuk."
        }), 504
        
    except requests.exceptions.ConnectionError:
        return jsonify({
            "success": False,
            "error": "Tidak dapat terhubung ke Ollama. Pastikan Ollama sudah berjalan di localhost:11434"
        }), 503
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Terjadi kesalahan internal",
            "details": str(e)
        }), 500

@summarization_bp.route('/api/health', methods=['GET'])
def health_check():
    """Endpoint untuk mengecek status aplikasi dan Ollama"""
    try:
        # Cek koneksi ke Ollama
        ollama_response = requests.get("http://localhost:11434", timeout=5)
        ollama_status = "running" if ollama_response.status_code == 200 else "error"
        
        # Cek model yang tersedia
        try:
            models_response = requests.get("http://localhost:11434/api/tags", timeout=5)
            models = models_response.json().get("models", [])
            model_names = [m.get("name") for m in models]
            llama3_available = any("llama3" in name for name in model_names)
        except:
            llama3_available = False
            
    except:
        ollama_status = "not connected"
        llama3_available = False
    
    return jsonify({
        "status": "running",
        "ollama_status": ollama_status,
        "llama3_available": llama3_available,
        "endpoint": "/api/summarize"
    }), 200