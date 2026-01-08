from typing import Dict, List
import numpy as np
import scipy.sparse as sp
from sklearn.decomposition import TruncatedSVD
from app.database import supabase


class CFRecommender:
    """Simple collaborative filtering using truncated SVD on implicit feedback.

    Builds a user-item interaction matrix from `feedback` and `recommendations`
    tables in Supabase and computes low-rank user/item factors.
    """
    def __init__(self, n_components: int = 50):
        self.n_components = n_components
        self.user_index: Dict[str, int] = {}
        self.item_index: Dict[str, int] = {}
        self.user_factors = None
        self.item_factors = None
        self.fitted = False

    def _gather_interactions(self):
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
                # treat being recommended as small positive signal
                weight = 0.1

            interactions[(sid, pid)] = interactions.get((sid, pid), 0.0) + weight

        for f in feedback:
            add_action(f)

        for r in recs:
            add_action(r)

        return interactions

    def fit(self):
        interactions = self._gather_interactions()

        if not interactions:
            self.fitted = False
            return

        users = sorted({u for (u, _) in interactions.keys()})
        items = sorted({i for (_, i) in interactions.keys()})

        self.user_index = {u: idx for idx, u in enumerate(users)}
        self.item_index = {i: idx for idx, i in enumerate(items)}

        rows = []
        cols = []
        data = []
        for (u, i), w in interactions.items():
            rows.append(self.user_index[u])
            cols.append(self.item_index[i])
            data.append(w)

        mat = sp.csr_matrix((data, (rows, cols)), shape=(len(users), len(items)))

        k = min(self.n_components, min(mat.shape) - 1)
        if k <= 0:
            self.fitted = False
            return

        svd = TruncatedSVD(n_components=k, random_state=42)
        user_factors = svd.fit_transform(mat)
        item_factors = svd.components_.T

        self.user_factors = user_factors
        self.item_factors = item_factors
        self.fitted = True

    def recommend_for_student(self, student_id: str, programs: List[Dict], top_k: int = 10) -> Dict[str, float]:
        if not self.fitted:
            return {}

        if student_id not in self.user_index:
            return {}

        uidx = self.user_index[student_id]
        user_vec = self.user_factors[uidx]

        scores = self.item_factors.dot(user_vec)

        prog_scores: Dict[str, float] = {}
        for prog in programs:
            pid = prog.get("id")
            if pid in self.item_index:
                idx = self.item_index[pid]
                prog_scores[pid] = float(scores[idx])

        if not prog_scores:
            return {}

        vals = np.array(list(prog_scores.values()))
        minv = vals.min()
        maxv = vals.max()
        if maxv > minv:
            for k in list(prog_scores.keys()):
                prog_scores[k] = (prog_scores[k] - minv) / (maxv - minv)
        else:
            for k in list(prog_scores.keys()):
                prog_scores[k] = 1.0

        # return top_k entries (but keep full dict for lookup)
        return prog_scores


cf_recommender = CFRecommender()
