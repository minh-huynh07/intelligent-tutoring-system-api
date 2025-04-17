import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

class HeroesPreprocessing:

    def preprocess(self):
        heroes_ability = pd.read_csv('heroes_data/heroes_ability.csv')


        vectorizer = TfidfVectorizer(stop_words='english', lowercase=True, ngram_range=(1, 2))

        tfidf_matrix = vectorizer.fit_transform(heroes_ability['ability'])

        # tfidf_df = pd.DataFrame(tfidf_matrix.toarray(), columns=vectorizer.get_feature_names_out())

        # Print or return the resulting DataFrame
        print(vectorizer.get_feature_names_out())

        return None


processor = HeroesPreprocessing()
processor.preprocess()
