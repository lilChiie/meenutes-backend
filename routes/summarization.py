from flask import Blueprint, request, jsonify
from google import genai
import os

summarization_bp = Blueprint("summarization_v2", __name__)

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


@summarization_bp.route("/api/summarize", methods=["POST"])
def summarize_transcript():
    try:
        # Validasi request
        if not request.is_json:
            return jsonify({
                "success": False,
                "error": "Content-Type must be application/json"
            }), 400

        data = request.get_json()

        # Validasi transcript
        if "transcript" not in data or not data["transcript"].strip():
            return jsonify({
                "success": False,
                "error": "Field 'transcript' is required and cannot be empty"
            }), 400

        transcript = data["transcript"].strip()

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
10. DO NOT remove technical terms.
11. DO NOT add conclusions unless explicitly stated.
12. Bullets MUST represent different topics.

Transcript:
{transcript}
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        summary = response.text.strip()

        return jsonify({
            "success": True,
            "summary": summary,
            "original_length": len(transcript),
            "summary_length": len(summary)
        }), 200

    except Exception as e:
      import traceback
    traceback.print_exc()

    return jsonify({
        "success": False,
        "type": type(e).__name__,
        "error": str(e)
    }), 500


@summarization_bp.route("/api/health", methods=["GET"])
def health_check():
    try:
        return jsonify({
            "status": "running",
            "model": "gemini-2.5-flash",
            "api_key_loaded": bool(os.getenv("GEMINI_API_KEY")),
            "api_key_preview": str(os.getenv("GEMINI_API_KEY"))[:10]
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500