from textblob import TextBlob

def correct_spelling(query):
    if not query:
        return ""
    blob = TextBlob(query)
    return str(blob.correct()).strip()