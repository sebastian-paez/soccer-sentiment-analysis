from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import torch.nn.functional as F


class SocialSentiment:
    def __init__(self, model_name: str = "cardiffnlp/twitter-roberta-base-sentiment"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        self.labels = ["negative", "neutral", "positive"]

    def analyze(self, text: str):
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=256)
        with torch.no_grad():
            outputs = self.model(**inputs)
            probs = F.softmax(outputs.logits, dim=-1).squeeze().cpu()
            idx = int(torch.argmax(probs)) if hasattr(probs, 'numpy') else int(torch.argmax(probs))
            sentiment = self.labels[idx]
            confidence = float(torch.max(probs))
        return {"sentiment": sentiment, "confidence": confidence}
