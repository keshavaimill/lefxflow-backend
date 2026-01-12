import os
import numpy as np
from functools import lru_cache
from sentence_transformers import SentenceTransformer

os.environ["TOKENIZERS_PARALLELISM"] = "false"

MODEL_NAME = "nlpaueb/legal-bert-base-uncased"


@lru_cache(maxsize=1)
def get_model():
    print("⚙️  [EMBED] Loading Legal-BERT model…")
    model = SentenceTransformer(MODEL_NAME, device="cpu")
    print("✅ [EMBED] Legal-BERT model is ready")
    return model


def embed_text(text: str) -> np.ndarray:

    print(f"🧩 [EMBED] Received text length = {len(text)} chars")

    if not text or not text.strip():
        print("⚠️  [EMBED] Empty text, returning zero vector")
        return np.zeros(768, dtype="float32")

    model = get_model()

    print("🚀 [EMBED] Encoding text chunk…")
    emb = model.encode(
        text,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False
    )

    print("✅ [EMBED] Embedding generated, shape =", emb.shape)

    return emb.astype("float32")
