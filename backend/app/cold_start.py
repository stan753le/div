from typing import List, Dict, Tuple
from app.database import supabase
import random


class ColdStartHandler:
    def __init__(self):
        self.popular_programs_cache = []
        self.cache_valid = False

    def get_popular_programs(self, top_k: int = 10) -> List[Dict]:
        try:
            feedback_result = supabase.table("feedback").select("program_id, accepted").execute()
            recommendations_result = supabase.table("recommendations").select("program_id").execute()

            program_scores = {}

            for feedback in feedback_result.data:
                prog_id = feedback['program_id']
                if prog_id not in program_scores:
                    program_scores[prog_id] = 0
                if feedback.get('accepted', False):
                    program_scores[prog_id] += 3
                program_scores[prog_id] += 1

            for rec in recommendations_result.data:
                prog_id = rec['program_id']
                if prog_id not in program_scores:
                    program_scores[prog_id] = 0
                program_scores[prog_id] += 0.1

            if not program_scores:
                programs_result = supabase.table("programs").select("*").execute()
                return random.sample(programs_result.data, min(top_k, len(programs_result.data)))

            sorted_programs = sorted(program_scores.items(), key=lambda x: x[1], reverse=True)
            top_program_ids = [pid for pid, _ in sorted_programs[:top_k]]

            programs_result = supabase.table("programs").select("*").in_("id", top_program_ids).execute()

            program_map = {p['id']: p for p in programs_result.data}
            return [program_map[pid] for pid in top_program_ids if pid in program_map]

        except Exception:
            programs_result = supabase.table("programs").select("*").execute()
            return random.sample(programs_result.data, min(top_k, len(programs_result.data)))

    def get_interest_based_recommendations(
        self,
        interests: List[str],
        programs: List[Dict],
        top_k: int = 10
    ) -> List[Dict]:
        interest_set = set(interest.lower() for interest in interests)

        program_scores = []
        for program in programs:
            tags = set(tag.lower() for tag in program.get('tags', []))
            skills = set(skill.lower() for skill in program.get('skills', []))

            overlap = len(interest_set.intersection(tags.union(skills)))

            if overlap > 0:
                program_scores.append((program, overlap))

        program_scores.sort(key=lambda x: x[1], reverse=True)

        return [prog for prog, _ in program_scores[:top_k]]

    def recommend_for_new_user(
        self,
        student_data: Dict,
        top_k: int = 5
    ) -> List[Tuple[Dict, float, str]]:
        try:
            programs_result = supabase.table("programs").select("*").execute()
            all_programs = programs_result.data

            if not all_programs:
                return []

            interests = student_data.get('interests', [])

            if interests:
                interest_recs = self.get_interest_based_recommendations(
                    interests,
                    all_programs,
                    top_k=top_k
                )

                if interest_recs:
                    recommendations = []
                    for i, program in enumerate(interest_recs):
                        score = 1.0 - (i * 0.1)
                        explanation = self._generate_cold_start_explanation(
                            student_data,
                            program,
                            "interest_match"
                        )
                        recommendations.append((program, score, explanation))

                    return recommendations

            popular_programs = self.get_popular_programs(top_k=top_k)

            recommendations = []
            for i, program in enumerate(popular_programs):
                score = 0.8 - (i * 0.08)
                explanation = self._generate_cold_start_explanation(
                    student_data,
                    program,
                    "popular"
                )
                recommendations.append((program, score, explanation))

            return recommendations

        except Exception:
            return []

    def _generate_cold_start_explanation(
        self,
        student_data: Dict,
        program: Dict,
        reason: str
    ) -> str:
        if reason == "interest_match":
            interests = student_data.get('interests', [])
            program_tags = program.get('tags', [])

            matching = [
                interest for interest in interests
                if any(interest.lower() in tag.lower() or tag.lower() in interest.lower()
                       for tag in program_tags)
            ]

            if matching:
                return f"Based on your interests in {', '.join(matching[:3])}, this program could be a great fit. Many students with similar interests have found success here."

            return f"This program aligns with your interests and offers skills in {', '.join(program.get('skills', [])[:3])}."

        elif reason == "popular":
            return f"This is a popular program among students. It offers comprehensive training in {', '.join(program.get('skills', [])[:3])} and has high satisfaction ratings."

        return "This program may be of interest to you based on your profile."


cold_start_handler = ColdStartHandler()
