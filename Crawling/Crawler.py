import nltk
import requests
from bs4 import BeautifulSoup
from nltk import ngrams, WordNetLemmatizer

from utils import create_folder

base_url = "https://dota2.fandom.com"

def get_html(url):
    # Send GET request to fetch page content
    response = requests.get(base_url + url)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup

def get_all_heroes():
    url = "/wiki/Heroes"

    soup = get_html(url)

    hero_grid = soup.select("#content table tr td a[title]")

    heroes = []
    for hero_anchor in hero_grid:
        name = hero_anchor["title"].strip()
        if name:
            url = hero_anchor["href"]
        heroes.append({
            "name": name,
            "url": url
        })
    # for i, hero in enumerate(heroes, 1):
    #     print(f"{i}. {hero}")
    return heroes


def normalize_text(text):
    lemmatizer = WordNetLemmatizer()

    text = ''.join(e for e in text if e.isalnum() or e.isspace())

    tokens = nltk.word_tokenize(text)

    lemmatized_tokens = [lemmatizer.lemmatize(token.lower()) for token in tokens]
    return " ".join(lemmatized_tokens)

def get_hero(hero):
    soup = get_html(hero["url"])

    abilities_info = soup.find_all("div", class_="ability-background")

    results = []

    for info in abilities_info:
        parent = info.parent
        results.append(parent.text.strip())

    return " ".join(results)

def save_text_file(name, content):
    with open(name, "w", encoding="utf-8") as file:
        file.write(content)


# Run
create_folder("data")
heroes = get_all_heroes()
for hero in heroes:
    print(f"Fetching data for {hero['name']}...")
    abilities = get_hero(hero)

    save_text_file(f'data/{hero["name"]}.txt', abilities)
    print(f"Data for {hero['name']} saved.")
    #
    # # Save normalized text
    # norm = normalize_text(abilities)
    # # Calculate TF-IDF for normalized text
    # vectorizer = TfidfVectorizer()
    # tfidf_matrix = vectorizer.fit_transform([norm])
    #
    # # Save TF-IDF values to a file
    # tfidf_values = "\n".join(
    #     f"{word}: {tfidf_matrix[0, idx]:.4f}" for word, idx in vectorizer.vocabulary_.items()
    # )
    # save_text_file(f'preprocessing/{hero["name"]}_tfidf.txt', tfidf_values)



    # uni_grams = list(ngrams(tokens, 1))
    # bi_grams = list(ngrams(tokens, 2))
    # tri_grams = list(ngrams(tokens, 3))
    #
    # # union all grams to string
    # all_grams = list(set(uni_grams + bi_grams + tri_grams))
    # all_grams = ["\r\n".join(gram) for gram in all_grams]

    # save_text_file(f'preprocessing/{hero["name"]}.txt', all_grams)

print(f"Total heroes found: {len(heroes)}")