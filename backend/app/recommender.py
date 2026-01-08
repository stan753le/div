import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Tuple
import json

class ContentBasedRecommender:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=500,
            stop_words='english',
            ngram_range=(1, 2)
        )
        self.program_vectors = None
        self.programs = []

    def fit(self, programs: List[Dict]):
        self.programs = programs

        program_texts = []
        for prog in programs:
            text_parts = [
                prog['name'],
                prog['description'],
                ' '.join(prog.get('tags', [])),
                ' '.join(prog.get('skills', []))
            ]
            program_texts.append(' '.join(text_parts))

        self.program_vectors = self.vectorizer.fit_transform(program_texts)

    def _build_student_profile_text(self, student_data: Dict) -> str:
        interests = student_data.get('interests', [])
        grades = student_data.get('grades', {})

        profile_parts = []

        profile_parts.extend(interests * 3)

        if isinstance(grades, str):
            try:
                grades = json.loads(grades)
            except:
                grades = {}

        high_grade_subjects = [
            subject for subject, grade in grades.items()
            if grade >= 80
        ]
        profile_parts.extend(high_grade_subjects * 2)

        return ' '.join(profile_parts)

    def recommend(
        self,
        student_data: Dict,
        top_k: int = 5
    ) -> List[Tuple[Dict, float, str]]:
        student_text = self._build_student_profile_text(student_data)

        if not student_text.strip():
            return []

        student_vector = self.vectorizer.transform([student_text])

        similarities = cosine_similarity(student_vector, self.program_vectors)[0]

        top_indices = np.argsort(similarities)[::-1][:top_k]

        recommendations = []
        for idx in top_indices:
            if similarities[idx] > 0:
                program = self.programs[idx]
                score = float(similarities[idx])
                explanation = self._generate_explanation(
                    student_data,
                    program,
                    score
                )
                recommendations.append((program, score, explanation))

        return recommendations

    def _generate_explanation(
        self,
        student_data: Dict,
        program: Dict,
        score: float
    ) -> str:
        interests = student_data.get('interests', [])
        grades = student_data.get('grades', {})

        if isinstance(grades, str):
            try:
                grades = json.loads(grades)
            except:
                grades = {}

        program_tags = set(program.get('tags', []))
        program_skills = set(program.get('skills', []))

        matching_interests = [
            interest for interest in interests
            if any(interest.lower() in tag.lower() or tag.lower() in interest.lower()
                   for tag in program_tags.union(program_skills))
        ]

        high_grade_subjects = [
            subject for subject, grade in grades.items()
            if grade >= 80
        ]

        relevant_subjects = [
            subject for subject in high_grade_subjects
            if any(subject.lower() in tag.lower() or tag.lower() in subject.lower()
                   for tag in program_tags.union(program_skills))
        ]

        explanation_parts = []

        if matching_interests:
            explanation_parts.append(
                f"Based on your interests in {', '.join(matching_interests[:3])}"
            )

        if relevant_subjects:
            explanation_parts.append(
                f"your strong performance in {', '.join(relevant_subjects[:3])}"
            )

        if not explanation_parts:
            explanation_parts.append("Based on your profile")

        key_skills = ', '.join(program.get('skills', [])[:3])
        if key_skills:
            explanation_parts.append(
                f"you'll develop skills in {key_skills}"
            )

        return ', '.join(explanation_parts) + '.'

recommender_engine = ContentBasedRecommender()
