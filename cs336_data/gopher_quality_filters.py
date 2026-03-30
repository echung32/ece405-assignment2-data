import nltk

# Ensure punkt is available. Might need to download it in a real setup.
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt_tab")


def gopher_quality_filter(text: str) -> bool:
    """
    Returns True if the text passes the Gopher quality filters, False otherwise.
    Filters:
    1. Less than 50 or more than 100,000 words.
    2. Mean word length outside the range of 3 to 10 characters.
    3. More than 30% of lines ending with an ellipsis ("...").
    4. Less than 80% of words with at least one alphabetic character.
    """
    words = nltk.word_tokenize(text)

    # Filter 1: Less than 50 or more than 100,000 words.
    num_words = len(words)
    if num_words < 50 or num_words > 100000:
        return False

    # Filter 2: Mean word length outside the range of 3 to 10 characters.
    total_length = sum(len(word) for word in words)
    mean_length = total_length / num_words
    if mean_length < 3 or mean_length > 10:
        return False

    # Filter 3: More than 30% of lines ending with an ellipsis ("...").
    lines = text.split("\n")
    if len(lines) > 0:
        ellipsis_lines = sum(1 for line in lines if line.strip().endswith("..."))
        if (ellipsis_lines / len(lines)) > 0.3:
            return False

    # Filter 4: Less than 80% of words with at least one alphabetic character.
    alpha_words = sum(1 for word in words if any(c.isalpha() for c in word))
    if (alpha_words / num_words) < 0.8:
        return False

    return True
