import os
import pickle

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

from utils import create_folder

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class HeroCosineModel:

    abilities_sim_matrix = None
    stats_sim_matrix = None
    hero_idx = None

    def __init__(self):
        self.model_dir = 'model'
        self.abilities_sim_matrix_file_path = os.path.join(BASE_DIR, self.model_dir, "abilities_sim_matrix.pkl")
        self.stats_sim_matrix_file_path = os.path.join(BASE_DIR, self.model_dir, "stats_sim_matrix.pkl")
        self.hero_idx_file_path = os.path.join(BASE_DIR, self.model_dir, "hero_idx.pkl")


    def build_similarity_model(self, heroes_ability, heroes_stats):
        abilities_matrix = heroes_ability.iloc[:, 1:].values
        stats_matrix = heroes_stats.iloc[:, 1:].values

        # Precompute similarity matrices
        abilities_sim_matrix = cosine_similarity(abilities_matrix)
        stats_sim_matrix = cosine_similarity(stats_matrix)

        # Store hero index for lookups
        hero_idx = heroes_stats['id'].values

        return abilities_sim_matrix, stats_sim_matrix, hero_idx


    def save_similarity_model(self):
        create_folder(self.model_dir)

        with open(os.path.join(self.abilities_sim_matrix_file_path), 'wb') as f:
            pickle.dump(self.abilities_sim_matrix, f)

        with open(os.path.join(self.stats_sim_matrix_file_path), 'wb') as f:
            pickle.dump(self.stats_sim_matrix, f)

        with open(os.path.join(self.hero_idx_file_path), 'wb') as f:
            pickle.dump(self.hero_idx, f)


    def load_similarity_model(self):
        if self.abilities_sim_matrix is None:
            with open(self.abilities_sim_matrix_file_path, 'rb') as f:
                self.abilities_sim_matrix = pickle.load(f)
        if self.stats_sim_matrix is None:
            with open(self.stats_sim_matrix_file_path, 'rb') as f:
                self.stats_sim_matrix = pickle.load(f)
        if self.hero_idx is None:
            with open(self.hero_idx_file_path, 'rb') as f:
                self.hero_idx = pickle.load(f)


    def build(self):
        # Load data
        abilities = pd.read_csv(os.path.join(BASE_DIR, 'dataset/heroes_ability_preprocessed.csv'))
        heroes_stats = pd.read_csv(os.path.join(BASE_DIR, 'dataset/heroes_stats_preprocessed.csv'))

        self.abilities_sim_matrix, self.stats_sim_matrix, self.hero_idx = self.build_similarity_model(abilities, heroes_stats)

        self.save_similarity_model()


    def get_similar_heroes(self, hero_ids, top_n=3):
        self.load_similarity_model()

        hero_indices = [np.where(self.hero_idx == hero_id)[0][0] for hero_id in hero_ids]

        similar_indices = []
        for i in hero_indices:
            ability_sims = self.abilities_sim_matrix[i]
            stats_sims = self.stats_sim_matrix[i]

            final_sims = 0.5 * ability_sims + 0.5 * stats_sims

            # argsort returns indices that would sort array in ascending order
            # [::-1] reverses to get descending order
            # [1:top_n+1] takes next top_n elements after the hero itself
            indices = np.argsort(final_sims)[::-1][1:top_n + 1]
            similar_indices.extend(indices)

        return set(similar_indices)


# model = HeroCosineModel()
# model.build()
# print(model.get_similar_heroes([1, 2]))
