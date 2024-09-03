import re

import requests
from bs4 import BeautifulSoup
from collections import defaultdict
import nltk
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('punkt_tab')
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
from nltk import word_tokenize
import heapq

cybersecurity_sites = {
    "Krebs on Security": "https://krebsonsecurity.com/",
    "ThreatPost": "https://threatpost.com/",
    "The Hacker News": "https://thehackernews.com/",
    "Dark Reading": "https://www.darkreading.com/",
    "Bleeping Computer": "https://www.bleepingcomputer.com/"
}


def fetch_site_content(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    return None


def parse_articles(site_name, html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    articles = []

    if site_name == "Krebs on Security":
        articles = soup.find_all('h2', class_='entry-title')
    elif site_name == "ThreatPost":
        articles = soup.find_all('h2', class_='post-title')
    elif site_name == "The Hacker News":
        articles = soup.find_all('h2', class_='home-title')
    elif site_name == "Dark Reading":
        articles = soup.find_all('h3', class_='listing-heading')
    elif site_name == "Bleeping Computer":
        articles = soup.find_all('h2', class_='bc-title')

    parsed_articles = []
    for article in articles[:5]:
        link = article.find('a')
        if link is not None:
            parsed_articles.append((article.text.strip(), link['href']))
        else:
            print(f"Warning: No link found for article: {article.text.strip()}")

    return parsed_articles


def extract_article_content(url):
    html_content = fetch_site_content(url)
    soup = BeautifulSoup(html_content, 'html.parser')

    # This will vary depending on the site's structure.
    if "krebsonsecurity.com" in url:
        content = soup.find('div', class_='entry-content')
    elif "threatpost.com" in url:
        content = soup.find('div', class_='post-content')
    elif "thehackernews.com" in url:
        content = soup.find('div', class_='articlebody')
    elif "darkreading.com" in url:
        content = soup.find('div', class_='article-content')
    elif "bleepingcomputer.com" in url:
        content = soup.find('article')

    if content:
        # Extract and clean the text
        paragraphs = content.find_all('p')
        text = "\n\n".join([para.get_text(strip=True) for para in paragraphs])
        return text
    else:
        return "Content could not be extracted."


import re


def save_to_html(site_name, article_title, article_content):
    # Sanitize the article title for use in the filename
    sanitized_title = re.sub(r'[^\w\s]', '', article_title)
    filename = f"{site_name}_{sanitized_title}.html"

    # Replace newlines with <br> tags outside of the f-string
    formatted_content = article_content.replace("\n", "<br>")

    with open(filename, 'w', encoding='utf-8') as file:
        file.write(f"<html><head><title>{article_title}</title></head><body>")
        file.write(f"<h1>{article_title}</h1>")
        file.write(f"<p>{formatted_content}</p>")  # Using the already formatted content
        file.write("</body></html>")

    print(f"Saved article '{article_title}' to {filename}")


def fetch_and_display_articles(site_name, articles):
    """
    Process articles and print them to console,
    save them to HTML file if valid content is found.
    """
    print(f"\nTop articles from {site_name}:")

    for title, link in articles:
        if link:
            print(f"\nTitle: {title}\nLink: {link}")
            article_content = extract_article_content(link)
            if article_content.strip():  # Only save if content is non-empty
                print(f"Content: {article_content[:500]}...")  # Show the first 500 characters
                save_to_html(site_name, title, article_content)
            else:
                print(f"Content could not be extracted from {link}")
        else:
            print(f"Warning: No link found for article: {title}")

    print(f"Finished processing {site_name}.\n")


def summarize_text(text, num_sentences=3):
    stop_words = set(stopwords.words('english'))
    word_frequencies = defaultdict(int)

    for word in word_tokenize(text.lower()):
        if word not in stop_words and word.isalnum():
            word_frequencies[word] += 1

    maximum_frequency = max(word_frequencies.values())
    for word in word_frequencies:
        word_frequencies[word] /= maximum_frequency

    sentence_scores = {}
    sentences = sent_tokenize(text)

    for sentence in sentences:
        for word in word_tokenize(sentence.lower()):
            if word in word_frequencies:
                if sentence not in sentence_scores:
                    sentence_scores[sentence] = word_frequencies[word]
                else:
                    sentence_scores[sentence] += word_frequencies[word]

    summary_sentences = heapq.nlargest(num_sentences, sentence_scores, key=sentence_scores.get)
    summary = ' '.join(summary_sentences)
    return summary


def search_for_keywords(articles, keywords):
    relevant_articles = []
    for title, link in articles:
        article_content = fetch_site_content(link)
        if any(keyword.lower() in article_content.lower() for keyword in keywords):
            relevant_articles.append((title, link))
    return relevant_articles


def main_two():
    keyword_mode = input("Search for specific keywords? (y/n): ").lower() == 'y'

    if keyword_mode:
        keywords = input("Enter keywords separated by commas: ").split(',')
        keywords = [keyword.strip() for keyword in keywords]

    for site_name, site_url in cybersecurity_sites.items():
        print(f"Fetching articles from {site_name}...")
        html_content = fetch_site_content(site_url)

        if html_content:
            articles = parse_articles(site_name, html_content)

            if keyword_mode:
                articles = search_for_keywords(articles, keywords)

            fetch_and_display_articles(site_name, articles)

