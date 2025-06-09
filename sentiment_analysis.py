from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Sentiment analysis using TextBlob
def textblob_sentiment(text):
    analysis = TextBlob(text)
    return analysis.sentiment.polarity

# Sentiment analysis using VADER
def vader_sentiment(text):
    analyzer = SentimentIntensityAnalyzer()
    score = analyzer.polarity_scores(text)
    return score['compound']

# Choose your sentiment function here (TextBlob or VADER)
def analyze_sentiment(text, method='vader'):
    if method == 'textblob':
        return textblob_sentiment(text)
    else:
        return vader_sentiment(text)
