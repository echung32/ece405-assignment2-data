import fasttext

from cs336_data.config import DATA_DIR

model = fasttext.load_model((DATA_DIR / "lid.176.bin").as_posix())



def identify_language(text: str) -> tuple[str, float]:

    # to make it all one line, replace newlines with spaces
    text = text.replace("\n", " ")
    predictions = model.predict(text)

    # predictions is a tuple: (('__label__en',), array([0.98]))
    labels = predictions[0]
    scores = predictions[1]

    # to extract the language tag and remap label
    top_label = labels[0].replace("__label__", "")  # type: ignore
    top_score = float(scores[0])

    return top_label, top_score
