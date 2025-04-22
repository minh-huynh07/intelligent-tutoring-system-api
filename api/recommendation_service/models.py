import os
import pickle

import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from utils import create_folder

class CosineModelBuilder:
    def __init__(self, model_dir='model'):
        self.model_dir = model_dir

    def build_similarity_model(self, heroes_ability, heroes_stats):
        abilities_matrix = heroes_ability.iloc[:, 1:].values
        stats_matrix = heroes_stats.iloc[:, 1:].values

        # Precompute similarity matrices
        abilities_sim_matrix = cosine_similarity(abilities_matrix)
        stats_sim_matrix = cosine_similarity(stats_matrix)

        return abilities_sim_matrix, stats_sim_matrix

    def save_similarity_model(self, abilities_sim_matrix, stats_sim_matrix):
        create_folder(self.model_dir)

        with open(os.path.join(self.model_dir, 'abilities_sim_matrix.pkl'), 'wb') as f:
            pickle.dump(abilities_sim_matrix, f)

        with open(os.path.join(self.model_dir, 'stats_sim_matrix.pkl'), 'wb') as f:
            pickle.dump(stats_sim_matrix, f)

    def load_similarity_model(self):
        with open(os.path.join(self.model_dir, 'abilities_sim_matrix.pkl'), 'rb') as f:
            abilities_sim_matrix = pickle.load(f)
        with open(os.path.join(self.model_dir, 'stats_sim_matrix.pkl'), 'rb') as f:
            stats_sim_matrix = pickle.load(f)

        return abilities_sim_matrix, stats_sim_matrix

    def build(self):
        # Load data
        abilities = pd.read_csv('dataset/heroes_ability_preprocessed.csv')
        heroes_stats = pd.read_csv('dataset/heroes_stats_preprocessed.csv')

        abilities_sim_matrix, stats_sim_matrix = self.build_similarity_model(abilities, heroes_stats)

        self.save_similarity_model(abilities_sim_matrix, stats_sim_matrix)

    def get_similar_heroes(self, hero_ids, top_n=10):
        # Find index of hero_id in the matrices
        hero_idx = np.where(hero_ids == hero_id)[0][0]

        # Get similarities for the specific hero
        ability_sims = abilities_sim_matrix[hero_idx]
        stats_sims = stats_sim_matrix[hero_idx]

        # Combine similarities with equal weighting
        final_sims = 0.5 * ability_sims + 0.5 * stats_sims

        # Get indices of top similar heroes
        similar_indices = np.argsort(final_sims)[::-1][1:top_n + 1]  # Exclude self

        # Create recommendations dataframe
        recommendations = pd.DataFrame({
            'hero_id': hero_ids[similar_indices],
            'similarity_ability': ability_sims[similar_indices],
            'similarity_stats': stats_sims[similar_indices],
            'final_similarity': final_sims[similar_indices]
        })

        return recommendations


# Build and save model
# model_builder = CosineModelBuilder()
# abilities_sim_matrix, stats_sim_matrix, hero_ids = model_builder.build_similarity_model(abilities, heroes_stats_scaled)
# model_builder.save_similarity_model(abilities_sim_matrix, stats_sim_matrix, hero_ids)
#
# # Load model and get recommendations
# abilities_sim_matrix, stats_sim_matrix, hero_ids = model_builder.load_similarity_model()
# hero_recommendations = model_builder.get_hero_recommendations_fast(
#     input_heroes_id,
#     abilities_sim_matrix,
#     stats_sim_matrix,
#     hero_ids
# )
# print("\nMost similar heroes to hero ID", input_heroes_id)
# print(hero_recommendations)
