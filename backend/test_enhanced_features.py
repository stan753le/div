"""
Test script for enhanced recommendation features.

This script demonstrates:
1. Matrix factorization with ALS
2. Hybrid recommendation with adaptive weighting
3. Enhanced explanation generation
4. Similar program discovery
"""

import os
from dotenv import load_dotenv
from app.database import supabase
from app.matrix_factorization import als_recommender
from app.hybrid_recommender import hybrid_recommender
from app.explanation_engine import explanation_engine

load_dotenv()


def test_als_recommender():
    """Test ALS matrix factorization."""
    print("\n" + "="*60)
    print("Testing ALS Matrix Factorization")
    print("="*60)

    success = als_recommender.fit()

    if success:
        print("ALS model trained successfully")
        print(f"- Users: {als_recommender.n_users}")
        print(f"- Items: {als_recommender.n_items}")
        print(f"- Factors: {als_recommender.n_factors}")
    else:
        print("ALS model training failed (may need more data)")

    return success


def test_hybrid_recommender():
    """Test hybrid recommendation system."""
    print("\n" + "="*60)
    print("Testing Hybrid Recommender")
    print("="*60)

    try:
        students_result = supabase.table("students").select("*").limit(1).execute()

        if not students_result.data:
            print("No students found. Create a student profile first.")
            return False

        student = students_result.data[0]
        print(f"\nTesting recommendations for: {student['name']}")

        programs_result = supabase.table("programs").select("*").execute()
        programs = programs_result.data

        recommendations = hybrid_recommender.recommend(
            student_data=student,
            programs=programs,
            top_k=5,
            apply_diversity=True
        )

        print(f"\nGenerated {len(recommendations)} recommendations:\n")

        for i, (program, score, explanation) in enumerate(recommendations, 1):
            print(f"{i}. {program['name']}")
            print(f"   Score: {score:.3f}")
            print(f"   {explanation}")
            print()

        strategy = hybrid_recommender.explain_recommendation_weights(student['id'])
        print("Recommendation Strategy:")
        print(f"- Feedback count: {strategy['feedback_count']}")
        print(f"- Content weight: {strategy['content_weight']}")
        print(f"- Collaborative weight: {strategy['collaborative_weight']}")
        print(f"- Strategy: {strategy['strategy']}")

        return True

    except Exception as e:
        print(f"Error: {e}")
        return False


def test_explanation_engine():
    """Test enhanced explanation generation."""
    print("\n" + "="*60)
    print("Testing Explanation Engine")
    print("="*60)

    try:
        students_result = supabase.table("students").select("*").limit(1).execute()
        programs_result = supabase.table("programs").select("*").limit(3).execute()

        if not students_result.data or not programs_result.data:
            print("Need student and program data")
            return False

        student = students_result.data[0]
        programs = programs_result.data

        print(f"\nGenerating explanations for: {student['name']}\n")

        for i, program in enumerate(programs, 1):
            explanation = explanation_engine.generate_explanation(
                student_data=student,
                program=program,
                content_score=0.75,
                cf_score=0.60,
                algorithm="hybrid"
            )

            print(f"{i}. {program['name']}")
            print(f"   {explanation}\n")

            short_explanation = explanation_engine.generate_short_explanation(
                student_data=student,
                program=program,
                content_score=0.75
            )
            print(f"   Short: {short_explanation}\n")

        return True

    except Exception as e:
        print(f"Error: {e}")
        return False


def test_similar_programs():
    """Test similar program discovery."""
    print("\n" + "="*60)
    print("Testing Similar Programs Discovery")
    print("="*60)

    if not als_recommender.fitted:
        print("ALS model not trained. Skipping similar programs test.")
        return False

    try:
        programs_result = supabase.table("programs").select("*").limit(3).execute()

        if not programs_result.data:
            print("No programs found")
            return False

        for program in programs_result.data:
            print(f"\nPrograms similar to: {program['name']}")

            similar = als_recommender.get_similar_items(program['id'], top_k=3)

            if similar:
                similar_ids = [pid for pid, _ in similar]
                similar_progs = supabase.table("programs").select("*").in_(
                    "id", similar_ids
                ).execute()

                prog_map = {p['id']: p for p in similar_progs.data}

                for pid, similarity in similar:
                    if pid in prog_map:
                        prog = prog_map[pid]
                        print(f"  - {prog['name']} (similarity: {similarity:.3f})")
            else:
                print("  No similar programs found")

        return True

    except Exception as e:
        print(f"Error: {e}")
        return False


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("ENHANCED RECOMMENDATION SYSTEM TEST SUITE")
    print("="*60)

    results = {
        "ALS Recommender": test_als_recommender(),
        "Hybrid Recommender": test_hybrid_recommender(),
        "Explanation Engine": test_explanation_engine(),
        "Similar Programs": test_similar_programs()
    }

    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")

    print("\nNote: Some tests may fail if there's insufficient data.")
    print("Generate more feedback by using the application to improve results.")


if __name__ == "__main__":
    main()
