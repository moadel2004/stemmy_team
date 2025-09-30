from __future__ import annotations

import os
from pathlib import Path
from typing import List, Tuple, Dict, Any

import numpy as np
import joblib

class TopicClassifier:
    """
    Loader/runner لنموذج التصنيف المبني بـ scikit-learn.
    يتوقع ملفات:
      - bow_vectorizer.pkl
      - label_encoder.pkl
      - trained_model.pkl
    داخل مجلد النموذج.
    """
    def __init__(self, vectorizer, label_encoder, model):
        self.vectorizer = vectorizer
        self.label_encoder = label_encoder
        self.model = model

        # أسماء الأصناف مرتبة مثل model.classes_
        if hasattr(model, "classes_"):
            self.class_names = list(self.label_encoder.inverse_transform(model.classes_))
        else:
            # fallback: استخدم label encoder classes
            self.class_names = list(getattr(self.label_encoder, "classes_", []))

    @classmethod
    def from_dir(cls, model_dir: str | Path) -> "TopicClassifier":
        model_dir = Path(model_dir)
        vec_path = model_dir / "bow_vectorizer.pkl"
        le_path = model_dir / "label_encoder.pkl"
        mdl_path = model_dir / "trained_model.pkl"

        if not vec_path.exists() or not le_path.exists() or not mdl_path.exists():
            raise FileNotFoundError(f"Missing one or more model files in: {model_dir}")

        vectorizer = joblib.load(vec_path)
        label_encoder = joblib.load(le_path)
        model = joblib.load(mdl_path)
        return cls(vectorizer, label_encoder, model)

    def _proba(self, X) -> np.ndarray:
        if hasattr(self.model, "predict_proba"):
            return self.model.predict_proba(X)
        # fallback لو فيه decision_function:
        if hasattr(self.model, "decision_function"):
            scores = self.model.decision_function(X)
            if scores.ndim == 1:
                scores = scores.reshape(-1, 1)
            # softmax
            e = np.exp(scores - np.max(scores, axis=1, keepdims=True))
            return e / np.sum(e, axis=1, keepdims=True)
        # ما فيش احتمالات متاحة: رجّع توزيع متساوٍ
        n_classes = len(self.class_names) if self.class_names else 1
        return np.full((X.shape[0], n_classes), 1.0 / n_classes, dtype=float)

    def predict(self, text: str) -> Tuple[str, float]:
        X = self.vectorizer.transform([text])
        proba = self._proba(X)[0]
        idx = int(np.argmax(proba))
        label = self.class_names[idx] if self.class_names else str(idx)
        conf = float(proba[idx])
        return label, conf

    def top_k(self, text: str, k: int = 3) -> List[Dict[str, Any]]:
        X = self.vectorizer.transform([text])
        proba = self._proba(X)[0]
        indices = np.argsort(-proba)[:k]
        return [
            {"label": self.class_names[i] if self.class_names else str(int(i)), "prob": float(proba[i])}
            for i in indices
        ]