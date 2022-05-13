from flask import Flask, render_template, request

import core


app = Flask(__name__)


@app.route("/")
def main():
    data = { }
    return render_template("index.html", data=data)


@app.route('/video')
def video():
    video_id = request.args.get("url")
    data = { }

    try:
        comments = core.video_comments(video_id)
        clean_comments = core.clean_comments(comments)
        lem_comments = core.lemmatize(clean_comments)
        word_count = core.word_count(lem_comments)
        clean_stop_words = core.clean_stop_words(word_count.keys())
        word_count = {k: word_count[k] for k in clean_stop_words}
        wc = core.wordcloud_from_dict(word_count)

        get_polarity = core.get_polarity(lem_comments)
        get_analysis = core.get_analysis(get_polarity)


        #data["comments"] = comments
        #data["word_count"] = word_count
        #data['get_subjectivity'] = get_subjectivity
        #data['subjectivity'] = data['comments'].apply(get_subjectivity)

        data['wc_svg'] = wc.to_svg()

        data['polarity'] = data['comments'].apply(get_polarity)
        data['analysis'] = data['polarity'].apply(get_analysis)

        return render_template("index.html", data=data)
    except Exception as e:
        return render_template("error.html", error=e, str=str)


if __name__ == "__main__":
    app.run()