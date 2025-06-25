# utils/emotion_lyrics.py

from cProfile import label
import os
import torch
from transformers import (
    BertTokenizer,
    BertForSequenceClassification,
    AutoConfig,
)

# Dynamically set base directory relative to this file
BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../emotion_lyrics_model")
)

MODEL_PATHS = {
    "model_a":  os.path.join(BASE_DIR, "modela"),
    "model_b":  os.path.join(BASE_DIR, "modelb"),
    "27labels": os.path.join(BASE_DIR, "27labels")
}

DEFAULT_KEY = "27labels"
_loaded = {}

def _load_model(which=DEFAULT_KEY):
    if which not in _loaded:
        path = MODEL_PATHS[which]
        tokenizer = BertTokenizer.from_pretrained(path)
        model     = BertForSequenceClassification.from_pretrained(path)
        cfg       = AutoConfig.from_pretrained(path)

        # Robust label extraction
        if getattr(cfg, "id2label", None):
            id2lab = {int(k): v for k, v in cfg.id2label.items()}
            labels = [id2lab[i] for i in range(model.num_labels)]
        elif getattr(cfg, "label2id", None):
            lab2id = cfg.label2id
            labels = sorted(lab2id, key=lambda x: lab2id[x])
        else:
            labels = [str(i) for i in range(model.num_labels)]

        _loaded[which] = (tokenizer, model, labels)
    return _loaded[which]

def detect(text: str, which: str = DEFAULT_KEY):
    tokenizer, model, labels = _load_model(which)
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)

    with torch.no_grad():
        logits = model(**inputs).logits
        probs = torch.softmax(logits, dim=-1)[0]
        idx = int(torch.argmax(probs))
        if which == "27labels":
            label_path = os.path.join(MODEL_PATHS["27labels"], "labels.txt")
            with open(label_path, "r", encoding="utf-8") as f:
                labels = [line.strip() for line in f if line.strip()]

        return {
            "label": labels[idx],
            "confidence": float(probs[idx]),
            "all_scores": {lbl: round(float(p), 4) for lbl, p in zip(labels, probs)},
            "model_used": which,
        }
