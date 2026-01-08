from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.database import supabase
from app.models import (
    StudentProfile,
    StudentUpdate,
    Recommendation,
    FeedbackSubmit,
    RecommendationRequest
)
from app.recommender import recommender_engine
from app.cf_recommender import cf_recommender
from app.cold_start import cold_start_handler
from app.matrix_factorization import als_recommender
from app.hybrid_recommender import hybrid_recommender
from app.explanation_engine import explanation_engine
from typing import List
import json

app = FastAPI(title="Study Program Recommender API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    result = supabase.table("programs").select("*").execute()
    programs = result.data
    if programs:
        recommender_engine.fit(programs)

    try:
        cf_recommender.fit()
    except Exception:
        pass

    try:
        als_recommender.fit()
    except Exception:
        pass

@app.get("/")
def read_root():
    return {"message": "Study Program Recommender API", "status": "running"}

@app.get("/programs")
def get_programs():
    try:
        result = supabase.table("programs").select("*").execute()
        return {"programs": result.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/students")
def create_student(student: StudentProfile):
    try:
        existing = supabase.table("students").select("*").eq("email", student.email).execute()

        if existing.data:
            raise HTTPException(status_code=400, detail="Student with this email already exists")

        result = supabase.table("students").insert({
            "name": student.name,
            "email": student.email,
            "interests": student.interests,
            "grades": student.grades
        }).execute()

        return {"student": result.data[0]}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/students/{student_id}")
def get_student(student_id: str):
    try:
        result = supabase.table("students").select("*").eq("id", student_id).execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Student not found")

        return {"student": result.data[0]}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/students/{student_id}")
def update_student(student_id: str, student_update: StudentUpdate):
    try:
        update_data = {}
        if student_update.name is not None:
            update_data["name"] = student_update.name
        if student_update.interests is not None:
            update_data["interests"] = student_update.interests
        if student_update.grades is not None:
            update_data["grades"] = student_update.grades

        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")

        update_data["updated_at"] = "now()"

        result = supabase.table("students").update(update_data).eq("id", student_id).execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Student not found")

        return {"student": result.data[0]}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/recommendations", response_model=List[Recommendation])
def get_recommendations(request: RecommendationRequest):
    try:
        student_result = supabase.table("students").select("*").eq("id", request.student_id).execute()

        if not student_result.data:
            raise HTTPException(status_code=404, detail="Student not found")

        student_data = student_result.data[0]

        programs_result = supabase.table("programs").select("*").execute()
        programs = programs_result.data

        if not programs:
            return []

        feedback_history = supabase.table("feedback").select("*").eq("student_id", request.student_id).execute()
        has_feedback = len(feedback_history.data) > 0

        if not has_feedback:
            cold_start_recs = cold_start_handler.recommend_for_new_user(
                student_data,
                top_k=request.top_k
            )

            response_recommendations = []
            for program, score, explanation in cold_start_recs:
                rec_data = {
                    "student_id": request.student_id,
                    "program_id": program['id'],
                    "score": score,
                    "explanation": explanation,
                    "algorithm": "cold_start"
                }

                try:
                    supabase.table("recommendations").insert(rec_data).execute()
                except Exception:
                    pass

                response_recommendations.append(
                    Recommendation(
                        program_id=program['id'],
                        program_name=program['name'],
                        program_description=program['description'],
                        score=score,
                        explanation=explanation,
                        tags=program.get('tags', []),
                        skills=program.get('skills', [])
                    )
                )

            return response_recommendations

        recommender_engine.fit(programs)

        try:
            als_recommender.fit()
        except Exception:
            pass

        hybrid_recs = hybrid_recommender.recommend(
            student_data,
            programs,
            top_k=request.top_k,
            apply_diversity=True
        )

        response_recommendations = []
        for program, final_score, explanation in hybrid_recs:
            pid = program['id']

            rec_data = {
                "student_id": request.student_id,
                "program_id": pid,
                "score": final_score,
                "explanation": explanation,
                "algorithm": "hybrid_enhanced"
            }

            try:
                supabase.table("recommendations").insert(rec_data).execute()
            except Exception:
                pass

            response_recommendations.append(
                Recommendation(
                    program_id=pid,
                    program_name=program['name'],
                    program_description=program['description'],
                    score=final_score,
                    explanation=explanation,
                    tags=program.get('tags', []),
                    skills=program.get('skills', [])
                )
            )

        return response_recommendations

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/feedback")
def submit_feedback(student_id: str, feedback: FeedbackSubmit):
    try:
        feedback_data = {
            "student_id": student_id,
            "program_id": feedback.program_id,
            "clicked": feedback.clicked,
            "accepted": feedback.accepted
        }

        if feedback.rating is not None:
            if feedback.rating < 1 or feedback.rating > 5:
                raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
            feedback_data["rating"] = feedback.rating

        result = supabase.table("feedback").insert(feedback_data).execute()

        try:
            cf_recommender.fit()
            als_recommender.fit()
        except Exception:
            pass

        return {"feedback": result.data[0]}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/retrain")
def retrain_models():
    try:
        cf_recommender.fit()
        als_success = als_recommender.fit()

        return {
            "status": "ok",
            "cf_trained": cf_recommender.fitted,
            "als_trained": als_success
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/students/{student_id}/recommendations")
def get_student_recommendations(student_id: str):
    try:
        result = supabase.table("recommendations").select(
            "*, programs(*)"
        ).eq("student_id", student_id).order("created_at", desc=True).limit(10).execute()

        return {"recommendations": result.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analytics/engagement")
def get_engagement_metrics():
    try:
        recommendations_result = supabase.table("recommendations").select("*").execute()
        feedback_result = supabase.table("feedback").select("*").execute()

        total_recommendations = len(recommendations_result.data)

        if total_recommendations == 0:
            return {
                "total_recommendations": 0,
                "total_clicks": 0,
                "total_accepts": 0,
                "ctr": 0.0,
                "acceptance_rate": 0.0,
                "avg_rating": 0.0,
                "num_ratings": 0,
                "unique_students": 0,
                "unique_programs": 0
            }

        feedback_data = feedback_result.data

        total_clicks = sum(1 for f in feedback_data if f.get('clicked', False))
        total_accepts = sum(1 for f in feedback_data if f.get('accepted', False))

        ratings = [f['rating'] for f in feedback_data if f.get('rating') is not None]
        avg_rating = sum(ratings) / len(ratings) if ratings else 0.0

        ctr = (total_clicks / total_recommendations) * 100
        acceptance_rate = (total_accepts / total_recommendations) * 100

        unique_students = len(set(r['student_id'] for r in recommendations_result.data))
        unique_programs = len(set(r['program_id'] for r in recommendations_result.data))

        return {
            "total_recommendations": total_recommendations,
            "total_clicks": total_clicks,
            "total_accepts": total_accepts,
            "ctr": round(ctr, 2),
            "acceptance_rate": round(acceptance_rate, 2),
            "avg_rating": round(avg_rating, 2),
            "num_ratings": len(ratings),
            "unique_students": unique_students,
            "unique_programs": unique_programs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analytics/program-performance")
def get_program_performance():
    try:
        recommendations_result = supabase.table("recommendations").select("*").execute()
        feedback_result = supabase.table("feedback").select("*").execute()
        programs_result = supabase.table("programs").select("*").execute()

        program_stats = {}
        for prog in programs_result.data:
            program_stats[prog['id']] = {
                "program_id": prog['id'],
                "program_name": prog['name'],
                "times_recommended": 0,
                "clicks": 0,
                "accepts": 0,
                "avg_rating": 0.0,
                "num_ratings": 0
            }

        for rec in recommendations_result.data:
            prog_id = rec['program_id']
            if prog_id in program_stats:
                program_stats[prog_id]['times_recommended'] += 1

        for feedback in feedback_result.data:
            prog_id = feedback['program_id']
            if prog_id in program_stats:
                if feedback.get('clicked', False):
                    program_stats[prog_id]['clicks'] += 1
                if feedback.get('accepted', False):
                    program_stats[prog_id]['accepts'] += 1
                if feedback.get('rating') is not None:
                    program_stats[prog_id]['num_ratings'] += 1
                    current_avg = program_stats[prog_id]['avg_rating']
                    count = program_stats[prog_id]['num_ratings']
                    program_stats[prog_id]['avg_rating'] = (
                        (current_avg * (count - 1) + feedback['rating']) / count
                    )

        for prog_id in program_stats:
            stats = program_stats[prog_id]
            if stats['times_recommended'] > 0:
                stats['ctr'] = round((stats['clicks'] / stats['times_recommended']) * 100, 2)
                stats['acceptance_rate'] = round((stats['accepts'] / stats['times_recommended']) * 100, 2)
            else:
                stats['ctr'] = 0.0
                stats['acceptance_rate'] = 0.0
            stats['avg_rating'] = round(stats['avg_rating'], 2)

        sorted_programs = sorted(
            program_stats.values(),
            key=lambda x: x['times_recommended'],
            reverse=True
        )

        return {"programs": sorted_programs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analytics/dashboard")
def get_analytics_dashboard():
    try:
        engagement = get_engagement_metrics()
        program_performance = get_program_performance()

        top_programs = sorted(
            program_performance['programs'],
            key=lambda x: x['acceptance_rate'],
            reverse=True
        )[:5]

        return {
            "engagement": engagement,
            "top_performing_programs": top_programs,
            "total_programs": len(program_performance['programs'])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/students/{student_id}/recommendation-strategy")
def get_recommendation_strategy(student_id: str):
    try:
        strategy_info = hybrid_recommender.explain_recommendation_weights(student_id)
        return strategy_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/programs/{program_id}/similar")
def get_similar_programs(program_id: str, limit: int = 5):
    try:
        if not als_recommender.fitted:
            raise HTTPException(
                status_code=503,
                detail="Collaborative filtering model not yet trained. Need more user feedback."
            )

        similar = als_recommender.get_similar_items(program_id, top_k=limit)

        if not similar:
            return {"similar_programs": []}

        programs_result = supabase.table("programs").select("*").in_(
            "id", [pid for pid, _ in similar]
        ).execute()

        program_map = {p['id']: p for p in programs_result.data}

        similar_programs = []
        for pid, similarity in similar:
            if pid in program_map:
                prog = program_map[pid]
                similar_programs.append({
                    "program_id": pid,
                    "program_name": prog['name'],
                    "program_description": prog['description'],
                    "similarity_score": round(similarity, 3),
                    "tags": prog.get('tags', []),
                    "skills": prog.get('skills', [])
                })

        return {"similar_programs": similar_programs}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
