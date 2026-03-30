import fasttext
from cs336_data.config import DATA_DIR


def classify_quality(text: str) -> tuple[str, float]:
    model_path = (DATA_DIR / "quality_classifier.bin").as_posix()
    model = fasttext.load_model(model_path)

    text = text.replace("\n", " ").replace("\r", " ").replace("\t", " ").strip()

    predictions = model.predict(text)

    labels = predictions[0]
    scores = predictions[1]

    top_label = labels[0].replace("__label__", "")
    top_score = float(scores[0])

    return top_label, top_score
