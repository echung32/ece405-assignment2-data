import fasttext
from cs336_data.config import DATA_DIR

nsfw_model = fasttext.load_model((DATA_DIR / "dolma_fasttext_nsfw_jigsaw_model.bin").as_posix())
toxic_model = fasttext.load_model((DATA_DIR / "dolma_fasttext_hatespeech_jigsaw_model.bin").as_posix())


def classify_nsfw(text: str) -> tuple[str, float]:
    text = text.replace("\n", " ")
    predictions = nsfw_model.predict(text)

    labels = predictions[0]
    scores = predictions[1]

    top_label = labels[0].replace("__label__", "")
    top_score = float(scores[0])

    return top_label, top_score


def classify_toxic_speech(text: str) -> tuple[str, float]:
    text = text.replace("\n", " ")
    predictions = toxic_model.predict(text)

    labels = predictions[0]
    scores = predictions[1]

    top_label = labels[0].replace("__label__", "")
    top_score = float(scores[0])

    return top_label, top_score
