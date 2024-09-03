import requests
from bs4 import BeautifulSoup
from transformers import pipeline


def fetch_articles():
    url = 'https://thehackernews.com/'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    articles = []
    # Look for anchor tags with the class 'story-link'
    for item in soup.find_all('a', class_='story-link'):
        # Extract the title from the <h2> tag inside the anchor tag
        title_tag = item.find('h2')
        if title_tag:
            title = title_tag.get_text(strip=True)
        else:
            title = 'No title found'

        # Extract the href attribute for the link
        link = item.get('href')
        if not link.startswith('http'):
            link = 'https://thehackernews.com' + link

        print(link, title)
        # Append the article details to the list
        articles.append((title, link))

    return articles


def search_articles_for_keyword(keyword, articles):
    matching_articles = []
    for title, link in articles:
        if keyword.lower() in title.lower():
            matching_articles.append((title, link))
        if len(matching_articles) >= 5:
            break
    return matching_articles


def format_output(articles):
    for title, link in articles:
        print(f"Title: {title}")
        print(f"URL: {link}")
        print()


def summarize_text(text):
    summarizer = pipeline('summarization', model='facebook/bart-large-cnn')
    summary = summarizer(text, max_length=150, min_length=50, length_penalty=2.0, do_sample=False)
    formatted_summary = summary[0]['summary_text'].replace('. ', '.\n')
    return formatted_summary

def fetch_article_text(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Adjust based on the HTML structure of the article
    article_text = soup.find('div', class_='post-body').get_text(strip=True)
    return article_text


if __name__ == "__main__":
    keyword = 'Microsoft'  # Change the keyword as needed
    articles = fetch_articles()
    matching_articles = search_articles_for_keyword(keyword, articles)
    print()
    format_output(matching_articles)
    for title, link in matching_articles:
        article_text = fetch_article_text(link)
        result = summarize_text(article_text)
        print(f"Title: {title}")
        print(f"URL: {link}\n")
        print("Summary:\n")
        print(result)
        print("\n" + "=" * 80 + "\nswag")

