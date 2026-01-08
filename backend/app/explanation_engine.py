from typing import Dict, List, Set, Tuple
import json
from app.database import supabase


class ExplanationEngine:
    """
    Enhanced explanation generation for recommendations.

    Generates multi-faceted explanations combining:
    - Interest matching (content-based)
    - Grade performance (content-based)
    - Similar student preferences (collaborative)
    - Program popularity (social proof)
    - Skills development opportunities
    """

    def __init__(self):
        self.program_cache = {}
        self.student_cache = {}

    def _load_program(self, program_id: str) -> Dict:
        """Load program data with caching."""
        if program_id in self.program_cache:
            return self.program_cache[program_id]

        try:
            result = supabase.table("programs").select("*").eq("id", program_id).execute()
            if result.data:
                self.program_cache[program_id] = result.data[0]
                return result.data[0]
        except Exception:
            pass

        return {}

    def _get_similar_students_who_liked(self, program_id: str, student_id: str) -> int:
        """Count how many students with similar interests accepted this program."""
        try:
            feedback_result = supabase.table("feedback").select("student_id").eq(
                "program_id", program_id
            ).eq("accepted", True).execute()

            if not feedback_result.data:
                return 0

            return len([f for f in feedback_result.data if f['student_id'] != student_id])
        except Exception:
            return 0

    def _get_program_acceptance_rate(self, program_id: str) -> float:
        """Calculate program's acceptance rate."""
        try:
            recs_result = supabase.table("recommendations").select("id").eq(
                "program_id", program_id
            ).execute()

            feedback_result = supabase.table("feedback").select("id").eq(
                "program_id", program_id
            ).eq("accepted", True).execute()

            total_recs = len(recs_result.data) if recs_result.data else 0
            total_accepts = len(feedback_result.data) if feedback_result.data else 0

            if total_recs == 0:
                return 0.0

            return total_accepts / total_recs
        except Exception:
            return 0.0

    def _match_interests(self, student_interests: List[str], program: Dict) -> List[str]:
        """Find matching interests between student and program."""
        interests_set = set(i.lower() for i in student_interests)
        program_tags = set(t.lower() for t in program.get('tags', []))
        program_skills = set(s.lower() for s in program.get('skills', []))

        all_program_terms = program_tags.union(program_skills)

        matching = []
        for interest in student_interests:
            interest_lower = interest.lower()
            for term in all_program_terms:
                if interest_lower in term or term in interest_lower:
                    if interest not in matching:
                        matching.append(interest)
                    break

        return matching

    def _match_high_performance_subjects(self, grades: Dict, program: Dict, threshold: float = 80) -> List[str]:
        """Find subjects where student excels that relate to program."""
        if isinstance(grades, str):
            try:
                grades = json.loads(grades)
            except:
                grades = {}

        high_performers = [
            subject for subject, grade in grades.items()
            if grade >= threshold
        ]

        program_tags = set(t.lower() for t in program.get('tags', []))
        program_skills = set(s.lower() for s in program.get('skills', []))
        all_program_terms = program_tags.union(program_skills)

        relevant_subjects = []
        for subject in high_performers:
            subject_lower = subject.lower()
            for term in all_program_terms:
                if subject_lower in term or term in subject_lower:
                    if subject not in relevant_subjects:
                        relevant_subjects.append(subject)
                    break

        return relevant_subjects

    def generate_explanation(
        self,
        student_data: Dict,
        program: Dict,
        content_score: float,
        cf_score: float,
        algorithm: str = "hybrid"
    ) -> str:
        """
        Generate a comprehensive, multi-faceted explanation for a recommendation.

        Args:
            student_data: Student profile including interests and grades
            program: Program information
            content_score: Content-based similarity score
            cf_score: Collaborative filtering score
            algorithm: Algorithm used (content, collaborative, hybrid, cold_start)

        Returns:
            Human-readable explanation string
        """
        explanation_parts = []

        interests = student_data.get('interests', [])
        grades = student_data.get('grades', {})

        matching_interests = self._match_interests(interests, program)
        relevant_subjects = self._match_high_performance_subjects(grades, program)

        if matching_interests:
            if len(matching_interests) == 1:
                explanation_parts.append(
                    f"This program aligns with your interest in {matching_interests[0]}"
                )
            elif len(matching_interests) == 2:
                explanation_parts.append(
                    f"This program matches your interests in {matching_interests[0]} and {matching_interests[1]}"
                )
            else:
                interest_list = ', '.join(matching_interests[:2])
                explanation_parts.append(
                    f"This program strongly aligns with your interests in {interest_list}, and more"
                )

        if relevant_subjects:
            if len(relevant_subjects) == 1:
                explanation_parts.append(
                    f"your excellent performance in {relevant_subjects[0]} suggests you'll excel here"
                )
            else:
                subject_list = ' and '.join(relevant_subjects[:2])
                explanation_parts.append(
                    f"your strong grades in {subject_list} indicate great potential for success"
                )

        if algorithm in ["hybrid", "collaborative"] and cf_score > 0.3:
            similar_count = self._get_similar_students_who_liked(
                program['id'],
                student_data.get('id', '')
            )

            if similar_count > 0:
                if similar_count == 1:
                    explanation_parts.append(
                        "a student with similar interests found this program valuable"
                    )
                elif similar_count < 5:
                    explanation_parts.append(
                        f"{similar_count} students with similar profiles were interested in this program"
                    )
                else:
                    explanation_parts.append(
                        f"this program is popular among students with similar backgrounds ({similar_count}+ accepted)"
                    )

        acceptance_rate = self._get_program_acceptance_rate(program['id'])
        if acceptance_rate > 0.5:
            explanation_parts.append(
                "it has a high satisfaction rate among recommended students"
            )

        skills = program.get('skills', [])
        if skills:
            key_skills = ', '.join(skills[:3])
            explanation_parts.append(
                f"you'll develop valuable skills including {key_skills}"
            )

        if not explanation_parts:
            explanation_parts.append("This program matches your academic profile")

        if len(explanation_parts) == 1:
            return explanation_parts[0].capitalize() + "."

        main_reasons = explanation_parts[:-1]
        last_reason = explanation_parts[-1]

        if len(main_reasons) == 1:
            return main_reasons[0].capitalize() + ", and " + last_reason + "."
        else:
            combined = main_reasons[0].capitalize() + ", " + ", ".join(main_reasons[1:])
            return combined + ", and " + last_reason + "."

    def generate_comparison_explanation(
        self,
        student_data: Dict,
        program: Dict,
        similar_programs: List[Dict]
    ) -> str:
        """
        Generate explanation that compares this program to similar alternatives.

        Args:
            student_data: Student profile
            program: Recommended program
            similar_programs: List of similar programs for comparison

        Returns:
            Comparative explanation string
        """
        program_skills = set(program.get('skills', []))

        unique_skills = []
        if similar_programs:
            other_skills = set()
            for other in similar_programs[:3]:
                other_skills.update(other.get('skills', []))

            unique_skills = list(program_skills - other_skills)

        if unique_skills:
            skill_list = ', '.join(unique_skills[:2])
            return f"Unlike similar programs, this offers unique training in {skill_list}, " \
                   f"while still covering core topics that match your interests."

        return f"This program offers a comprehensive curriculum that aligns well with your profile."

    def generate_short_explanation(
        self,
        student_data: Dict,
        program: Dict,
        content_score: float
    ) -> str:
        """
        Generate a concise, single-line explanation.

        Returns:
            Brief explanation string
        """
        interests = student_data.get('interests', [])
        matching_interests = self._match_interests(interests, program)

        if matching_interests:
            if len(matching_interests) == 1:
                return f"Matches your interest in {matching_interests[0]}"
            else:
                return f"Aligns with your interests in {', '.join(matching_interests[:2])}"

        if content_score > 0.5:
            return "Strong match with your academic profile"

        return "Recommended based on your preferences"


explanation_engine = ExplanationEngine()
