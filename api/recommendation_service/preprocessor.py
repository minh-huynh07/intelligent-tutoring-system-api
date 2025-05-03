import os
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import MultiLabelBinarizer

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

PCA_COMPONENTS = 67

class HeroesAbilityPreprocessing:

    def preprocess(self):
        hero_data = pd.read_csv(os.path.join(BASE_DIR, 'heroes_data/heroes_data.csv'))

        # TF-IDF vectorization
        vectorizer = TfidfVectorizer(
            stop_words='english',
            lowercase=True,
            ngram_range=(1, 3),
            min_df=0.4,
            max_df=0.8
        )
        tfidf_matrix = vectorizer.fit_transform(hero_data['ability'])
        tfidf_df = pd.DataFrame(tfidf_matrix.toarray(), columns=vectorizer.get_feature_names_out())

        # Combine with original data
        preprocessed_data = pd.concat([hero_data[['name']], tfidf_df], axis=1)

        # Merge with hero IDs
        heroes = pd.read_json(os.path.join(BASE_DIR, "heroes.json"), dtype={"id": int, "name": str, "img": str})
        preprocessed_data = preprocessed_data.merge(
            heroes[['id', 'name']], on='name', how='left'
        )
        preprocessed_data.sort_values('id', inplace=True)
        preprocessed_data.drop(columns=['name'], inplace=True)

        # PCA for dimensionality reduction
        pca = PCA(n_components=PCA_COMPONENTS)
        tfidf_columns = [col for col in vectorizer.get_feature_names_out() if col != 'id']
        pca_result = pca.fit_transform(preprocessed_data[tfidf_columns])

        # Standardize PCA components
        scaler = StandardScaler()
        pca_result_scaled = scaler.fit_transform(pca_result)

        # Replace TF-IDF columns with scaled PCA components
        preprocessed_data.drop(columns=tfidf_columns, inplace=True)
        pca_columns = [f'pca_{i}' for i in range(PCA_COMPONENTS)]
        preprocessed_data[pca_columns] = pca_result_scaled

        # Save to csv file
        preprocessed_data.to_csv(os.path.join(BASE_DIR, "dataset/heroes_ability_preprocessed.csv"), index=False)

class BasicStatsPreprocessing:
    def preprocess(self):
        heroes_stats = pd.read_csv(os.path.join(BASE_DIR, 'heroes_stats_data/heroes_stats.csv'))

        # --- Remove heroes ---
        heroes_stats = heroes_stats[~heroes_stats['localized_name'].str.lower().isin(['kez', 'ring master'])]

        # --- Handle missing values for base_health_regen and turn_rate by group mean ---
        # Group by primary_attr and fill missing values with group mean
        base_health_regen_by_attr = heroes_stats.groupby('primary_attr')['base_health_regen'].transform('mean')
        heroes_stats['base_health_regen'] = heroes_stats['base_health_regen'].fillna(base_health_regen_by_attr)
        
        # Group by primary_attr and fill missing values with group mean
        turn_rate_by_attr = heroes_stats.groupby('primary_attr')['turn_rate'].transform('mean')
        heroes_stats['turn_rate'] = heroes_stats['turn_rate'].fillna(turn_rate_by_attr)

        # --- One-hot encode roles, primary_attr, attack_type ---
        roles_df = heroes_stats['roles'].str.get_dummies(',')
        primary_attr_df = pd.get_dummies(heroes_stats['primary_attr'], dtype=int)
        attack_type_df = pd.get_dummies(heroes_stats['attack_type'], dtype=int)

        primary_attr_df.rename(columns={'agi': 'agility', 'int': 'intelligent', 'str': 'strength'}, inplace=True)
        if 'all' in primary_attr_df.columns:
            primary_attr_df.loc[primary_attr_df['all'] == 1, ['agility', 'intelligent', 'strength']] = 1
            primary_attr_df.drop(columns='all', inplace=True)

        # --- Combine all features ---
        stats = pd.concat([heroes_stats, roles_df, attack_type_df, primary_attr_df], axis=1)

        # --- Remove unnecessary columns ---
        drop_columns = [
            'roles', 'attack_type', 'primary_attr', 'img', 'icon', 'localized_name',
            'name', 'turbo_picks_trend', 'turbo_wins_trend', 'pub_pick_trend', 'pub_win_trend', 'base_health'
        ]
        stats.drop(columns=[col for col in drop_columns if col in stats.columns], inplace=True)
        stats.columns = stats.columns.str.lower()

        # --- Standardize all features except 'id' ---
        features = [col for col in stats.columns if col != 'id']
        scaler = StandardScaler()
        stats[features] = scaler.fit_transform(stats[features])

        # --- Save to csv file ---
        stats.to_csv(os.path.join(BASE_DIR, "dataset/basic_stats_preprocessed.csv"), index=False)

class AggregateStatsPreprocessing:

    def preprocess(self):
        heroes_stats = pd.read_csv(os.path.join(BASE_DIR, 'heroes_stats_data/heroes_stats.csv'))

        # --- Remove heroes ---
        heroes_stats = heroes_stats[~heroes_stats['localized_name'].str.lower().isin(['kez', 'ring master'])]

        # Select only aggregate stats columns
        agg_cols = [
            'id', 'gold_per_min', 'xp_per_min', 'kills_per_min', 'last_hits_per_min',
            'hero_damage_per_min', 'hero_healing_per_min', 'tower_damage'
        ]
        stats = heroes_stats[agg_cols]

        # Standardize all features except 'id'
        features = [col for col in stats.columns if col != 'id']
        scaler = StandardScaler()
        stats[features] = scaler.fit_transform(stats[features])

        # Save to csv file
        stats.to_csv(os.path.join(BASE_DIR, "dataset/aggregate_stats_preprocessed.csv"), index=False)

class RecommendedItemsPreprocessing:

    def preprocess(self):
        hero_data = pd.read_csv(os.path.join(BASE_DIR, 'heroes_data/heroes_data.csv'))

        # Merge with hero IDs
        heroes = pd.read_json(os.path.join(BASE_DIR, "heroes.json"), dtype={"id": int, "name": str, "img": str})
        hero_data = hero_data.merge(
            heroes[['id', 'name']], on='name', how='left'
        )
        hero_data.drop(columns=['name'], inplace=True)
        hero_data.sort_values('id', inplace=True)

        recommended_items = hero_data[['id', 'recommended_items']]

        # One-hot encode with MultiLabelBinarizer
        split_heroes_recommended_items = recommended_items['recommended_items'].str.lower().str.split(',')

        # One hot encode recommended items
        mlb = MultiLabelBinarizer()
        items_encoded = mlb.fit_transform(split_heroes_recommended_items)
        items_df = pd.DataFrame(items_encoded, columns=mlb.classes_)

        # Combine with id
        recommended_items = pd.concat([recommended_items[['id']], items_df], axis=1)

        # Save to csv file
        recommended_items.to_csv(
            os.path.join(BASE_DIR, "dataset/recommended_items_preprocessed.csv"),
            index=False
        )

# heroes_processor = HeroesAbilityPreprocessing()
# heroes_processor.preprocess()
#
# basic_stats_preprocessor = BasicStatsPreprocessing()
# basic_stats_preprocessor.preprocess()
#
# aggregate_stats_preprocessor = AggregateStatsPreprocessing()
# aggregate_stats_preprocessor.preprocess()
#
# recommended_items_preprocessor = RecommendedItemsPreprocessing()
# recommended_items_preprocessor.preprocess()