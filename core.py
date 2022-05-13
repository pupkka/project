import collections
import re
import time
from typing import Any

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
plt.style.use('fivethirtyeight')

from googleapiclient.discovery import build
from textblob import TextBlob
from nltk.corpus import stopwords
from wordcloud import WordCloud
from pymystem3 import Mystem

API_KEY = "AIzaSyDuV1ssRswKsW2uUjOWIyXWVh3sDDovBAw"
VIDEO_ID = "uaX3X3AF6Gw"

youtube = build("youtube", "v3", developerKey=API_KEY)
sw = ["br", "https", "это", "href", "youtu", "www", "com", "quot"]


def video_comments(video_id):
    video_response = youtube.commentThreads().list(part="snippet", videoId=video_id).execute()
    comments = []

    while video_response:
        for item in video_response["items"]:
            comment = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
            comments.append(comment)

        if not video_response.get("nextPageToken"):
            break

        video_response = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            pageToken=video_response["nextPageToken"]
        ).execute()
        time.sleep(2)

    return comments


def clean_comments(comments: list[str]) -> list[str]:
    return [re.sub(r"\W", " ", comment) for comment in comments]


def clean_stop_words(comments: list[str]) -> list[str]:
    text_tokens = clean_comments(comments)
    return [word for word in text_tokens
            if word not in stopwords.words('russian')
            and word not in stopwords.words('english')
            and word not in sw
            and len(word) > 1]


def word_count(comments: list[str]):
    word_count_dict = collections.defaultdict(lambda: 0)
    for comment in comments:
        for r in comment.split():
            word_count_dict[r] += 1

    return {k: v for k, v in sorted(word_count_dict.items(), key=lambda x: x[1], reverse=True)}


def wordcloud_from_dict(d: dict):
    wc = WordCloud(
        background_color="black",
        colormap='rainbow',
        max_words=200,
        mask=None,
        width=500,
        height=500
    ).generate_from_frequencies(d)

    return wc


def lemmatize(comments: list[str]) -> list[str]:
    lem_blacklist = ["", " ", "\n"]

    result = []
    m = Mystem()
    for comment in comments:
        lemmas = m.lemmatize(comment)
        result.append(' '.join([lem for lem in lemmas if lem.strip() not in lem_blacklist]))

    return result


#def get_subjectivity(comments: list[str]):
#    res = []
#    for comment in comments:
#        res.append(TextBlob(comment).sentiment.subjectivity)
#    return res


def get_polarity(comments: list[str]):
    respol = []
    for comment in comments:
        respol.append(TextBlob(comment).sentiment.polarity)
    return respol


def get_analysis(score):
    if score < 0:
        return 'Negative'
    elif score == 0:
        return 'Neutral'
    else:
        return 'Positive'


if __name__ == "__main__":
    comments_list = video_comments(VIDEO_ID)