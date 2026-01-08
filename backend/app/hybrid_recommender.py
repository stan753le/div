from typing import List, Dict, Tuple
import numpy as np
from app.recommender import recommender_engine
from app.matrix_factorization import als_recommender
from app.explanation_engine import explanation_engine
from app.database import supabase


class HybridRecommender:
    """
    Adaptive hybrid recommender that intelligently combines:
    - Content-based filtering (TF-IDF + cosine similarity)
    - Collaborative filtering (ALS matrix factorization)

    Uses adaptive weighting based on:
    - User's feedback history (more feedback = trust CF more)
    - Confidence in CF predictions
    - Content-based score strength
    """

    def __init__(self, base_content_weight: float = 0.6):
        self.base_content_weight = base_content_weight
        self.base_cf_weight = 1.0 - base_content_weight

    def _get_user_feedback_count(self, student_id: str) -> int:
        """Get count of feedback items for a student."""
        try:
            result = supabase.table("feedback").select("id").eq("student_id", student_id).execute()
            return len(result.data) if result.data else 0
        except Exception:
            return 0

    def _calculate_adaptive_weights(
        self,
        student_id: str,
        cf_available: bool,
        content_score: float,
        cf_score: float
    ) -> Tuple[float, float]:
        """
        Calculate adaptive weights for content-based and collaborative filtering.

        Strategy:
        - New users (0-2 feedback): 80% content, 20% CF
        - Growing users (3-10 feedback): 60% content, 40% CF
        - Experienced users (10+ feedback): 40% content, 60% CF

        Also adjusts based on score confidence:
        - If CF score is very low, trust content more
        - If content score is very low, trust CF more
        """
        if not cf_available:
            return 1.0, 0.0

        feedback_count = self._get_user_feedback_count(student_id)

        if feedback_count <= 2:
            base_content = 0.8
            base_cf = 0.2
        elif feedback_count <= 10:
            base_content = 0.6
            base_cf = 0.4
        else:
            base_content = 0.4
            base_cf = 0.6

        if cf_score < 0.1:
            base_content += 0.2
            base_cf -= 0.2
        elif cf_score > 0.8 and content_score < 0.3:
            base_content -= 0.1
            base_cf += 0.1

        base_content = max(0.2, min(0.9, base_content))
        base_cf = 1.0 - base_content

        return base_content, base_cf

    def _diversify_recommendations(
        self,
        recommendations: List[Tuple[Dict, float, str]],
        diversity_factor: float = 0.1
    ) -> List[Tuple[Dict, float, str]]:
        """
        Add diversity to recommendations to avoid filter bubble.

        Penalizes programs with very similar tags/skills to already-selected items.
        """
        if len(recommendations) <= 1:
            return recommendations

        diversified = [recommendations[0]]
        selected_tags = set(recommendations[0][0].get('tags', []))
        selected_skills = set(recommendations[0][0].get('skills', []))

        for program, score, explanation in recommendations[1:]:
            prog_tags = set(program.get('tags', []))
            prog_skills = set(program.get('skills', []))

            overlap_tags = len(selected_tags.intersection(prog_tags))
            overlap_skills = len(selected_skills.intersection(prog_skills))

            total_overlap = overlap_tags + overlap_skills
            max_possible = len(selected_tags) + len(selected_skills)

            if max_possible > 0:
                overlap_ratio = total_overlap / max_possible
                diversity_penalty = overlap_ratio * diversity_factor
                adjusted_score = score * (1.0 - diversity_penalty)
            else:
                adjusted_score = score

            diversified.append((program, adjusted_score, explanation))

            selected_tags.update(prog_tags)
            selected_skills.update(prog_skills)

        diversified.sort(key=lambda x: x[1], reverse=True)

        return diversified

    def recommend(
        self,
        student_data: Dict,
        programs: List[Dict],
        top_k: int = 5,
        apply_diversity: bool = True
    ) -> List[Tuple[Dict, float, str]]:
        """
        Generate hybrid recommendations combining content-based and collaborative filtering.

        Args:
            student_data: Student profile information
            programs: List of all available programs
            top_k: Number of recommendations to return
            apply_diversity: Whether to apply diversity boost

        Returns:
            List of (program, score, explanation) tuples
        """
        student_id = student_data.get('id')

        content_recs = recommender_engine.recommend(student_data, top_k=top_k * 2)

        cf_scores = {}
        if als_recommender.fitted and student_id:
            cf_scores = als_recommender.recommend_for_user(student_id, programs, top_k=top_k * 2)

        program_map = {p['id']: p for p in programs}

        combined_scores = {}

        for program, content_score, _ in content_recs:
            pid = program['id']
            cf_score = cf_scores.get(pid, 0.0)

            content_weight, cf_weight = self._calculate_adaptive_weights(
                student_id or "",
                len(cf_scores) > 0,
                content_score,
                cf_score
            )

            final_score = content_weight * content_score + cf_weight * cf_score

            combined_scores[pid] = {
                'score': final_score,
                'content_score': content_score,
                'cf_score': cf_score,
                'content_weight': content_weight,
                'cf_weight': cf_weight
            }

        for pid, cf_score in cf_scores.items():
            if pid not in combined_scores and pid in program_map:
                content_weight, cf_weight = self._calculate_adaptive_weights(
                    student_id or "",
                    True,
                    0.0,
                    cf_score
                )

                final_score = cf_weight * cf_score

                combined_scores[pid] = {
                    'score': final_score,
                    'content_score': 0.0,
                    'cf_score': cf_score,
                    'content_weight': content_weight,
                    'cf_weight': cf_weight
                }

        sorted_programs = sorted(
            combined_scores.items(),
            key=lambda x: x[1]['score'],
            reverse=True
        )[:top_k * 2]

        recommendations = []
        for pid, scores in sorted_programs:
            if pid in program_map:
                program = program_map[pid]

                algorithm = "hybrid" if scores['cf_score'] > 0 and scores['content_score'] > 0 else \
                           "collaborative" if scores['cf_score'] > scores['content_score'] else \
                           "content"

                explanation = explanation_engine.generate_explanation(
                    student_data,
                    program,
                    scores['content_score'],
                    scores['cf_score'],
                    algorithm
                )

                recommendations.append((program, scores['score'], explanation))

        if apply_diversity and len(recommendations) > 1:
            recommendations = self._diversify_recommendations(recommendations)

        return recommendations[:top_k]

    def explain_recommendation_weights(self, student_id: str) -> Dict:
        """
        Provide transparency about how weights are calculated for a user.

        Returns:
            Dictionary with weight information and reasoning
        """
        feedback_count = self._get_user_feedback_count(student_id)

        content_weight, cf_weight = self._calculate_adaptive_weights(
            student_id,
            als_recommender.fitted,
            0.5,
            0.5
        )

        if feedback_count <= 2:
            strategy = "New user - relying primarily on interests and grades"
        elif feedback_count <= 10:
            strategy = "Growing profile - balancing interests with behavioral patterns"
        else:
            strategy = "Established user - emphasizing collaborative signals from similar students"

        return {
            "feedback_count": feedback_count,
            "content_weight": round(content_weight, 2),
            "collaborative_weight": round(cf_weight, 2),
            "strategy": strategy,
            "cf_available": als_recommender.fitted
        }


hybrid_recommender = HybridRecommender()
