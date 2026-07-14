import os
import threading
from flask import Flask, request, jsonify
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer, ChatterBotCorpusTrainer

app = Flask(__name__)

DB_PATH = os.path.join(os.path.dirname(__file__), "db.sqlite3")

chatbot = ChatBot(
    "Chatpot",
    storage_adapter="chatterbot.storage.SQLStorageAdapter",
    database_uri=f"sqlite:///{DB_PATH}",
    read_only=True,
)

list_trainer = ListTrainer(chatbot)
corpus_trainer = ChatterBotCorpusTrainer(chatbot)

train_lock = threading.Lock()


@app.route("/", methods=["GET"])
def root():
    return jsonify({"status": "ok", "service": "chatbot", "endpoints": ["/chat", "/train"]})

def require_admin_key(req) -> bool:
    admin_key = os.environ.get("CHATBOT_ADMIN_KEY", "")
    provided = req.headers.get("X-Admin-Key", "")
    return bool(admin_key) and provided == admin_key

# Flask 1.x compatible:
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()
    if not text:
        return jsonify({"error": "Missing 'text'"}), 400

    response = chatbot.get_response(text)
    return jsonify({
        "input": text,
        "response": str(response),
        "confidence": getattr(response, "confidence", None),
    })

@app.route("/train", methods=["POST"])
def train():
    if not require_admin_key(request):
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json(silent=True) or {}
    mode = (data.get("mode") or "list").strip().lower()

    # habilitar escritura SOLO durante entrenamiento
    chatbot.read_only = False

    with train_lock:
        try:
            if mode == "list":
                conversations = data.get("conversations") or []
                if not isinstance(conversations, list) or not conversations:
                    return jsonify({"error": "Provide 'conversations' as a non-empty list"}), 400

                trained = 0
                for conv in conversations:
                    if isinstance(conv, list) and len(conv) >= 2:
                        list_trainer.train(conv)
                        trained += 1

                return jsonify({"status": "ok", "trained_conversations": trained})

            elif mode == "file":
                lines = data.get("lines") or []
                if not isinstance(lines, list) or len(lines) < 2:
                    return jsonify({"error": "Provide 'lines' as a list of strings (min 2)"}), 400

                clean = [str(x).strip() for x in lines if str(x).strip()]
                if len(clean) < 2:
                    return jsonify({"error": "Not enough valid lines"}), 400

                list_trainer.train(clean)
                return jsonify({"status": "ok", "trained_lines": len(clean)})

            elif mode == "corpus":
                corpus = (data.get("corpus") or "").strip()
                if not corpus:
                    return jsonify({"error": "Provide 'corpus' string"}), 400

                corpus_trainer.train(corpus)
                return jsonify({"status": "ok", "trained_corpus": corpus})

            else:
                return jsonify({"error": f"Unknown mode '{mode}'"}), 400

        finally:
            chatbot.read_only = True

if __name__ == "__main__":
    # solo para desarrollo local; gunicorn usara `app` directamente
    print("Starting Flask dev server on http://127.0.0.1:5000 (not for production)")
    app.run(host="127.0.0.1", port=5000, debug=False)
