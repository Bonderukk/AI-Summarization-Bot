from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
from transformers import pipeline
from flask_caching import Cache
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)
app.config['CACHE_TYPE'] = 'simple'
cache = Cache(app)

summarizer = pipeline('summarization', model='facebook/bart-large-cnn')


@cache.memoize(timeout=600)
def fetch_articles():
    url = 'https://thehackernews.com/'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    articles = []
    for item in soup.find_all('a', class_='story-link'):
        title_tag = item.find('h2')
        title = title_tag.get_text(strip=True) if title_tag else 'No title found'
        link = item.get('href')
        if not link.startswith('http'):
            link = 'https://thehackernews.com' + link
        articles.append((title, link))
    return articles


def fetch_article_text(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    article_text = soup.find('div', class_='post-body').get_text(strip=True)
    return article_text


def summarize_text(text):
    summary = summarizer(text, max_length=150, min_length=50, length_penalty=2.0, do_sample=False)
    return summary[0]['summary_text'].replace('. ', '.\n')


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        keyword = request.form['keyword']
        articles = fetch_articles()
        matching_articles = [article for article in articles if keyword.lower() in article[0].lower()][:5]

        urls = [link for _, link in matching_articles]
        with ThreadPoolExecutor(max_workers=5) as executor:
            texts = list(executor.map(fetch_article_text, urls))

        results = []
        for (title, link), text in zip(matching_articles, texts):
            summary = summarize_text(text)
            results.append({
                'title': title,
                'url': link,
                'summary': summary
            })

        return render_template('results.html', keyword=keyword, results=results)

    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
