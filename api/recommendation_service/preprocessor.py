import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MinMaxScaler

base_dir = "api/recommendation_service/"

class HeroesPreprocessing:

    def preprocess(self):
        heroes_ability = pd.read_csv(base_dir + '/heroes_data/heroes_ability.csv')

        # run rf-idf
        vectorizer = TfidfVectorizer(stop_words='english', lowercase=True, ngram_range=(2, 4), min_df=0.01, max_df=0.9)
        tfidf_matrix = vectorizer.fit_transform(heroes_ability['ability'])
        tfidf_df = pd.DataFrame(tfidf_matrix.toarray(), columns=vectorizer.get_feature_names_out())

        # combine data
        preprocessed_data = pd.concat([heroes_ability, tfidf_df], axis=1)
        preprocessed_data.drop(columns=['ability', 'url'], inplace=True)

        # populate id column
        heroes_data = pd.read_json(base_dir + "/heroes.json", dtype={"id": int, "name": str, "img": str})
        preprocessed_data = preprocessed_data.merge(
            heroes_data[['id', 'name']], on='name', how='left'
        )
        preprocessed_data['id'] = preprocessed_data['id'].fillna(0).astype(int)
        preprocessed_data.drop(columns=['name'], inplace=True)
        preprocessed_data.sort_values('id', inplace=True)

        # Save to csv file
        preprocessed_data.to_csv(base_dir + "dataset/heroes_ability_preprocessed.csv", index=False)

class HeroesStatsPreprocessing:
    def __init__(self):
        self.heroes_stats = pd.read_csv(base_dir + 'heroes_stats_data/heroes_stats.csv')

    def drop_unnecessary_columns(self):
        drop_columns = ['roles', 'attack_type', 'primary_attr', 'img', 'icon', 'localized_name',
                        'name', 'turbo_picks_trend', 'turbo_wins_trend', 'pub_pick_trend', 'pub_win_trend']
        self.heroes_stats.drop(columns=drop_columns, inplace=True)
        self.heroes_stats.columns = self.heroes_stats.columns.str.lower()
        return self.heroes_stats

    def handle_missing_values(self):
        # Handle base_health_regen
        base_health_regen_mean = self.heroes_stats['base_health_regen'].mean()
        self.heroes_stats['base_health_regen'] = self.heroes_stats['base_health_regen'].fillna(base_health_regen_mean)

        # Handle turn_rate
        turn_rate_mean = self.heroes_stats['turn_rate'].mean()
        self.heroes_stats['turn_rate'] = self.heroes_stats['turn_rate'].fillna(turn_rate_mean)

        # Remove Kez for consistency between different dataset
        self.heroes_stats = self.heroes_stats[self.heroes_stats['localized_name'] != 'Kez']

        return self.heroes_stats

    def scale_min_max(self):
        scaler = MinMaxScaler()

        id_col = self.heroes_stats['id'].astype(int)
        features = self.heroes_stats.drop('id', axis=1)

        scaled_features = pd.DataFrame(scaler.fit_transform(features), columns=features.columns)

        heroes_stats_scaled = pd.concat([id_col, scaled_features], axis=1)
        heroes_stats_scaled.index = self.heroes_stats.index

        return heroes_stats_scaled

    def preprocess(self):
        # Flatten the object columns
        roles_df = self.heroes_stats['roles'].str.get_dummies(',')
        primary_attr_df = pd.get_dummies(self.heroes_stats['primary_attr'], dtype=int)
        attack_type_df = pd.get_dummies(self.heroes_stats['attack_type'], dtype=int)

        primary_attr_df.rename(columns={'agi': 'agility', 'int': 'intelligent', 'str': 'strength'}, inplace=True)
        primary_attr_df.loc[primary_attr_df['all'] == 1, ['agility', 'intelligent', 'strength']] = 1
        primary_attr_df.drop(columns='all', inplace=True)

        # Combine results
        self.heroes_stats = pd.concat([self.heroes_stats, roles_df, attack_type_df, primary_attr_df], axis=1)

        self.handle_missing_values()
        self.drop_unnecessary_columns()

        self.heroes_stats = self.scale_min_max()

        # Save to csv file
        self.heroes_stats.to_csv(base_dir + "dataset/heroes_stats_preprocessed.csv", index=False)

# heroes_processor = HeroesPreprocessing()
# heroes_processor.preprocess()

heroes_stats_preprocessor = HeroesStatsPreprocessing()
heroes_stats_preprocessor.preprocess()