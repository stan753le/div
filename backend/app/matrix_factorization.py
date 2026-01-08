import numpy as np
import scipy.sparse as sp
from typing import Dict, List, Tuple
from app.database import supabase


class ALSMatrixFactorization:
    """
    Alternating Least Squares (ALS) matrix factorization for collaborative filtering.

    This is more sophisticated than basic SVD as it:
    - Handles implicit feedback better
    - Allows for regularization to prevent overfitting
    - Can incorporate confidence weights
    - Iteratively optimizes user and item factors
    """

    def __init__(self, n_factors: int = 50, n_iterations: int = 15, reg_lambda: float = 0.1):
        self.n_factors = n_factors
        self.n_iterations = n_iterations
        self.reg_lambda = reg_lambda

        self.user_index: Dict[str, int] = {}
        self.item_index: Dict[str, int] = {}
        self.user_factors: np.ndarray = None
        self.item_factors: np.ndarray = None

        self.fitted = False
        self.n_users = 0
        self.n_items = 0

    def _gather_interactions(self) -> Dict[Tuple[str, str], float]:
        """
        Gather user-item interactions from feedback and recommendations tables.

        Weight scheme:
        - Clicked: +1.0
        - Accepted: +3.0
        - Rating: +(rating/5.0) * 2.0
        - Just recommended: +0.1
        """
        interactions = {}

        try:
            feedback_res = supabase.table("feedback").select("*").execute()
            feedback = feedback_res.data or []
        except Exception:
            feedback = []

        try:
            recs_res = supabase.table("recommendations").select("*").execute()
            recs = recs_res.data or []
        except Exception:
            recs = []

        def add_action(record):
            sid = record.get("student_id")
            pid = record.get("program_id")
            if not sid or not pid:
                return

            weight = 0.0
            if record.get("clicked"):
                weight += 1.0
            if record.get("accepted"):
                weight += 3.0
            if record.get("rating") is not None:
                try:
                    rating = float(record.get("rating"))
                    weight += (rating / 5.0) * 2.0
                except Exception:
                    pass

            if weight <= 0:
                weight = 0.1

            interactions[(sid, pid)] = interactions.get((sid, pid), 0.0) + weight

        for f in feedback:
            add_action(f)

        for r in recs:
            add_action(r)

        return interactions

    def _build_interaction_matrix(self, interactions: Dict[Tuple[str, str], float]) -> sp.csr_matrix:
        """Build sparse interaction matrix from interactions dictionary."""
        users = sorted({u for (u, _) in interactions.keys()})
        items = sorted({i for (_, i) in interactions.keys()})

        self.user_index = {u: idx for idx, u in enumerate(users)}
        self.item_index = {i: idx for idx, i in enumerate(items)}

        self.n_users = len(users)
        self.n_items = len(items)

        rows = []
        cols = []
        data = []

        for (u, i), w in interactions.items():
            rows.append(self.user_index[u])
            cols.append(self.item_index[i])
            data.append(w)

        return sp.csr_matrix((data, (rows, cols)), shape=(self.n_users, self.n_items))

    def _als_step(self, ratings: sp.csr_matrix, solve_vecs: np.ndarray, fixed_vecs: np.ndarray) -> np.ndarray:
        """
        Single ALS optimization step.

        For each user/item, solve:
        x_u = (Y^T C^u Y + lambda * I)^-1 Y^T C^u p(u)

        where:
        - Y is the fixed factors (item or user)
        - C^u is the confidence matrix for user u
        - p(u) is the preference vector
        """
        A = fixed_vecs.T.dot(fixed_vecs) + self.reg_lambda * np.eye(self.n_factors)
        b = fixed_vecs.T

        new_vecs = np.zeros_like(solve_vecs)

        for i in range(solve_vecs.shape[0]):
            if ratings.indptr[i] != ratings.indptr[i + 1]:
                row_data = ratings.data[ratings.indptr[i]:ratings.indptr[i + 1]]
                row_indices = ratings.indices[ratings.indptr[i]:ratings.indptr[i + 1]]

                Cu = np.diag(row_data)
                p = (row_data > 0).astype(float)

                Y_u = fixed_vecs[row_indices]

                A_u = Y_u.T.dot(Cu).dot(Y_u) + self.reg_lambda * np.eye(self.n_factors)
                b_u = Y_u.T.dot(Cu).dot(p)

                new_vecs[i] = np.linalg.solve(A_u, b_u)
            else:
                new_vecs[i] = solve_vecs[i]

        return new_vecs

    def fit(self) -> bool:
        """
        Fit the ALS model on interaction data.

        Returns:
            True if fitting succeeded, False otherwise
        """
        interactions = self._gather_interactions()

        if not interactions or len(interactions) < 2:
            self.fitted = False
            return False

        ratings = self._build_interaction_matrix(interactions)

        if self.n_users < 2 or self.n_items < 2:
            self.fitted = False
            return False

        n_factors = min(self.n_factors, min(self.n_users, self.n_items) - 1)
        if n_factors <= 0:
            self.fitted = False
            return False

        self.user_factors = np.random.normal(0, 0.01, (self.n_users, n_factors))
        self.item_factors = np.random.normal(0, 0.01, (self.n_items, n_factors))

        for iteration in range(self.n_iterations):
            self.user_factors = self._als_step(ratings, self.user_factors, self.item_factors)
            self.item_factors = self._als_step(ratings.T.tocsr(), self.item_factors, self.user_factors)

        self.fitted = True
        return True

    def predict(self, user_id: str, item_id: str) -> float:
        """
        Predict score for a user-item pair.

        Returns:
            Predicted score (0-1 range after normalization)
        """
        if not self.fitted:
            return 0.0

        if user_id not in self.user_index or item_id not in self.item_index:
            return 0.0

        user_idx = self.user_index[user_id]
        item_idx = self.item_index[item_id]

        score = np.dot(self.user_factors[user_idx], self.item_factors[item_idx])
        return float(score)

    def recommend_for_user(self, user_id: str, programs: List[Dict], top_k: int = 10) -> Dict[str, float]:
        """
        Generate recommendations for a user.

        Returns:
            Dictionary mapping program_id to normalized score (0-1)
        """
        if not self.fitted or user_id not in self.user_index:
            return {}

        user_idx = self.user_index[user_id]
        user_vec = self.user_factors[user_idx]

        scores = {}
        for prog in programs:
            pid = prog.get("id")
            if pid in self.item_index:
                item_idx = self.item_index[pid]
                score = np.dot(user_vec, self.item_factors[item_idx])
                scores[pid] = float(score)

        if not scores:
            return {}

        score_values = np.array(list(scores.values()))
        min_score = score_values.min()
        max_score = score_values.max()

        if max_score > min_score:
            normalized_scores = {
                pid: (score - min_score) / (max_score - min_score)
                for pid, score in scores.items()
            }
        else:
            normalized_scores = {pid: 0.5 for pid in scores.keys()}

        return normalized_scores

    def get_similar_items(self, item_id: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """
        Find items similar to a given item based on factor vectors.

        Returns:
            List of (item_id, similarity_score) tuples
        """
        if not self.fitted or item_id not in self.item_index:
            return []

        item_idx = self.item_index[item_id]
        item_vec = self.item_factors[item_idx]

        similarities = self.item_factors.dot(item_vec)

        top_indices = np.argsort(similarities)[::-1][1:top_k+1]

        reverse_index = {idx: item_id for item_id, idx in self.item_index.items()}

        return [(reverse_index[idx], float(similarities[idx])) for idx in top_indices]


als_recommender = ALSMatrixFactorization()
