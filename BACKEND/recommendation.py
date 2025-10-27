# routes/recommendation.py
import os
import requests
import traceback
from flask import Blueprint, request, jsonify
from dotenv import load_dotenv

bp = Blueprint("recommendation", __name__)

# --- Load environment ---
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
load_dotenv(env_path)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # add to your .env

# Helper: safe extraction of text from Gemini response
def extract_text_from_gemini(result_json):
    try:
        if isinstance(result_json, dict):
            cand = result_json.get("candidates")
            if cand and isinstance(cand, list):
                first = cand[0]
                cont = first.get("content") or first.get("output")
                if isinstance(cont, dict):
                    parts = cont.get("parts") or cont.get("structured") or []
                    if parts and isinstance(parts, list):
                        part0 = parts[0]
                        if isinstance(part0, dict) and "text" in part0:
                            return part0["text"]
                        elif isinstance(part0, str):
                            return part0
                if "text" in first:
                    return first["text"]

            if "output" in result_json:
                out = result_json["output"]
                if isinstance(out, dict):
                    if "text" in out:
                        return out["text"]
                    if "contents" in out and isinstance(out["contents"], list):
                        texts = []
                        for c in out["contents"]:
                            if isinstance(c, dict) and "text" in c:
                                texts.append(c["text"])
                            elif isinstance(c, str):
                                texts.append(c)
                        if texts:
                            return "\n".join(texts)

            def find_first_string(d):
                if isinstance(d, str):
                    return d
                if isinstance(d, dict):
                    for v in d.values():
                        s = find_first_string(v)
                        if s:
                            return s
                if isinstance(d, list):
                    for item in d:
                        s = find_first_string(item)
                        if s:
                            return s
                return None

            maybe = find_first_string(result_json)
            if maybe:
                return maybe
    except Exception:
        pass
    return None

# --- GET handler for browser / health check ---
@bp.route("", methods=["GET"])
def recommend_get():
    return jsonify({"message": "Recommendation API is up. Use POST to get recommendations."}), 200

# --- POST handler for actual recommendations ---
@bp.route("", methods=["POST"])
def recommend():
    try:
        payload = request.get_json(force=True, silent=True)
        if not payload:
            return jsonify({"error": "Invalid JSON body"}), 400

        query = payload.get("query", "").strip()
        if not query:
            return jsonify({"error": "No query provided"}), 400

        # Mock fallback if GEMINI_API_KEY not set
        if not GEMINI_API_KEY:
            mock_recs = [
                f"Mock suggestion 1 for '{query}'",
                f"Mock suggestion 2 for '{query}'",
                f"Mock suggestion 3 for '{query}'",
                f"Mock suggestion 4 for '{query}'",
                f"Mock suggestion 5 for '{query}'"
            ]
            print("WARNING: GEMINI_API_KEY not set, returning mock recommendations")
            return jsonify({"warning": "GEMINI_API_KEY not configured. Returning mock data.", "recommendations": mock_recs}), 200

        # Call Gemini API
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite-preview-09-2025:generateContent?key={GEMINI_API_KEY}"

        body = {
            "contents": [
                {"parts": [{"text": f"Provide 5 concise, actionable recommendations for: {query}"}]}
            ]
        }
        headers = {"Content-Type": "application/json"}
        resp = requests.post(url, json=body, headers=headers, timeout=15)

        if resp.status_code != 200:
            print(f"Gemini HTTP error {resp.status_code}: {resp.text}")
            return jsonify({"error": f"Gemini API returned status {resp.status_code}", "details": resp.text}), 502

        result = resp.json()
        text = extract_text_from_gemini(result)

        if not text:
            print("Gemini response missing expected text. Full payload:")
            print(result)
            mock_recs = [
                f"Fallback suggestion A for '{query}'",
                f"Fallback suggestion B for '{query}'",
                f"Fallback suggestion C for '{query}'",
            ]
            return jsonify({"error": "Unexpected Gemini response format", "recommendations": mock_recs}), 200

        # Split lines into recommendations
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        recommendations = [line.lstrip(" -•0123456789.).\t").strip() for line in lines if line.strip()]
        if not recommendations:
            recommendations = [text.strip()]

        return jsonify({"recommendations": recommendations}), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": "Server exception", "details": str(e)}), 500
