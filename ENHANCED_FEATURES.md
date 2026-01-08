# Enhanced Recommendation System Features

This document describes the advanced features implemented in the Study Program Recommender System.

## Overview

The system now uses a sophisticated hybrid approach combining:
1. Advanced matrix factorization with ALS (Alternating Least Squares)
2. Adaptive weighting between content-based and collaborative filtering
3. Multi-faceted explanation generation
4. Diversity boosting to prevent filter bubbles

## Components

### 1. Matrix Factorization (ALS)

**File:** `backend/app/matrix_factorization.py`

Implements Alternating Least Squares for collaborative filtering, which offers several advantages over basic SVD:

**Key Features:**
- Iterative optimization of user and item latent factors
- Handles implicit feedback with confidence weighting
- Regularization to prevent overfitting
- Better performance with sparse data

**Weight Scheme:**
- Clicked: +1.0
- Accepted: +3.0
- Rating: +(rating/5.0) * 2.0
- Recommended only: +0.1

**How It Works:**
```python
from app.matrix_factorization import als_recommender

als_recommender.fit()

scores = als_recommender.recommend_for_user(
    student_id="uuid",
    programs=all_programs,
    top_k=10
)
```

**Configuration:**
- `n_factors=50`: Number of latent dimensions
- `n_iterations=15`: Number of optimization iterations
- `reg_lambda=0.1`: Regularization strength

### 2. Enhanced Explanation Engine

**File:** `backend/app/explanation_engine.py`

Generates sophisticated, multi-faceted explanations that combine:

**Explanation Factors:**
1. Interest matching with program tags/skills
2. Grade performance correlation
3. Social proof (similar students who liked this)
4. Program acceptance rate
5. Skills development opportunities

**Example Explanations:**

Simple match:
> "This program aligns with your interest in biology, your excellent performance in chemistry suggests you'll excel here, and you'll develop valuable skills including research methods, field work, data analysis."

With collaborative signal:
> "This program matches your interests in programming and math, your strong grades in computer science indicate great potential for success, 7 students with similar profiles were interested in this program, and you'll develop valuable skills including Python, machine learning, algorithms."

**API Usage:**
```python
from app.explanation_engine import explanation_engine

explanation = explanation_engine.generate_explanation(
    student_data=student_profile,
    program=program_info,
    content_score=0.85,
    cf_score=0.72,
    algorithm="hybrid"
)
```

### 3. Adaptive Hybrid Recommender

**File:** `backend/app/hybrid_recommender.py`

Intelligently combines content-based and collaborative filtering with dynamic weighting.

**Adaptive Weighting Strategy:**

| User Experience | Feedback Count | Content Weight | CF Weight | Strategy |
|----------------|----------------|----------------|-----------|----------|
| New User | 0-2 | 80% | 20% | Trust interests/grades |
| Growing User | 3-10 | 60% | 40% | Balanced approach |
| Established User | 10+ | 40% | 60% | Trust behavioral patterns |

**Additional Adjustments:**
- If CF score is very low (<0.1), increase content weight by 20%
- If CF score is high (>0.8) and content is low (<0.3), increase CF weight by 10%

**Diversity Boosting:**
The system applies a diversity penalty to avoid recommending programs with too much overlap in tags/skills:
- First recommendation: No penalty
- Subsequent recommendations: Penalized based on overlap with already-selected items
- Penalty factor: 10% per overlap ratio

**API Usage:**
```python
from app.hybrid_recommender import hybrid_recommender

recommendations = hybrid_recommender.recommend(
    student_data=student_profile,
    programs=all_programs,
    top_k=5,
    apply_diversity=True
)
```

## New API Endpoints

### 1. Get Recommendation Strategy

**Endpoint:** `GET /students/{student_id}/recommendation-strategy`

Returns transparency information about how recommendations are weighted for a specific student.

**Response:**
```json
{
  "feedback_count": 7,
  "content_weight": 0.6,
  "collaborative_weight": 0.4,
  "strategy": "Growing profile - balancing interests with behavioral patterns",
  "cf_available": true
}
```

**Use Cases:**
- Explain to users why they're getting certain recommendations
- Debug recommendation quality
- Educational transparency

### 2. Find Similar Programs

**Endpoint:** `GET /programs/{program_id}/similar?limit=5`

Returns programs similar to a given program based on collaborative filtering patterns.

**Response:**
```json
{
  "similar_programs": [
    {
      "program_id": "uuid",
      "program_name": "Data Science",
      "program_description": "...",
      "similarity_score": 0.872,
      "tags": ["math", "statistics", "programming"],
      "skills": ["Python", "statistics", "machine learning"]
    }
  ]
}
```

**Use Cases:**
- Show "Students who liked this also liked..."
- Help users explore related programs
- Provide alternatives

### 3. Enhanced Retrain Endpoint

**Endpoint:** `POST /retrain`

Now trains both the SVD-based CF model and the ALS model.

**Response:**
```json
{
  "status": "ok",
  "cf_trained": true,
  "als_trained": true
}
```

## Performance Improvements

### 1. Matrix Factorization Quality

ALS provides better recommendations because:
- Handles implicit feedback naturally
- Confidence weighting (strong signals count more)
- Regularization prevents overfitting to noise
- Iterative optimization finds better local optima

### 2. Explanation Quality

The new explanation engine provides:
- Multi-factor reasoning (not just one reason)
- Social proof integration
- Natural language flow
- Context-aware details

### 3. Diversity

Prevents filter bubbles by:
- Penalizing overly similar recommendations
- Balancing exploration vs exploitation
- Ensuring variety in recommended skills/tags

## Technical Details

### ALS Algorithm

The ALS algorithm alternates between fixing user factors and optimizing item factors, then vice versa:

```
For each iteration:
  1. Fix item factors Y, solve for user factors X
     For each user u:
       X_u = (Y^T C^u Y + λI)^-1 Y^T C^u p(u)

  2. Fix user factors X, solve for item factors Y
     For each item i:
       Y_i = (X^T C^i X + λI)^-1 X^T C^i p(i)
```

Where:
- `C^u` is the confidence matrix for user u
- `p(u)` is the preference vector
- `λ` is the regularization parameter

### Hybrid Scoring

Final score calculation:
```
final_score = α * content_score + (1 - α) * cf_score
```

Where `α` is adaptively determined based on:
- User feedback history
- Individual score confidence
- CF model availability

### Diversity Scoring

Diversity penalty:
```
overlap_ratio = (overlap_tags + overlap_skills) / (total_tags + total_skills)
diversity_penalty = overlap_ratio * diversity_factor (0.1)
adjusted_score = original_score * (1 - diversity_penalty)
```

## Usage Examples

### Complete Recommendation Flow

```python
student_data = {
    "id": "student-uuid",
    "interests": ["programming", "math", "AI"],
    "grades": {"math": 95, "computer science": 92}
}

programs = supabase.table("programs").select("*").execute().data

recommendations = hybrid_recommender.recommend(
    student_data=student_data,
    programs=programs,
    top_k=5,
    apply_diversity=True
)

for program, score, explanation in recommendations:
    print(f"{program['name']} (Score: {score:.2f})")
    print(f"  {explanation}\n")
```

### Check Recommendation Strategy

```bash
curl http://localhost:8000/students/{student_id}/recommendation-strategy
```

### Find Similar Programs

```bash
curl http://localhost:8000/programs/{program_id}/similar?limit=5
```

## Evaluation Metrics

The enhanced system can be evaluated using:

1. **NDCG@k**: Measures ranking quality
2. **Precision@k**: Measures relevance
3. **Diversity**: Intra-list diversity score
4. **Coverage**: How many different programs get recommended
5. **Serendipity**: Unexpected but relevant recommendations

See `evaluation/recommendation_evaluation.ipynb` for evaluation tools.

## Configuration Options

### ALS Parameters

```python
als_recommender = ALSMatrixFactorization(
    n_factors=50,       # Number of latent dimensions
    n_iterations=15,    # Optimization iterations
    reg_lambda=0.1      # Regularization strength
)
```

### Hybrid Parameters

```python
hybrid_recommender = HybridRecommender(
    base_content_weight=0.6  # Default content weight before adaptation
)
```

### Diversity Parameters

In `hybrid_recommender.py`:
```python
diversity_factor = 0.1  # Penalty strength for similar items
```

## Best Practices

1. **Regular Retraining**: Call `/retrain` endpoint after significant feedback accumulation
2. **Monitor Strategy**: Use `/recommendation-strategy` to ensure adaptive weights are working
3. **Track Diversity**: Measure intra-list diversity to ensure variety
4. **Evaluate Explanations**: Collect user feedback on explanation quality
5. **A/B Testing**: Compare enhanced vs basic recommendations

## Migration Notes

The system automatically falls back gracefully:
- If ALS model isn't trained yet, uses content-based only
- If CF scores unavailable, increases content weight
- If no feedback history, uses cold-start handler

No breaking changes to existing API contracts.

## Future Enhancements

Potential improvements:
1. Deep learning-based embeddings
2. Context-aware recommendations (time, location)
3. Multi-armed bandit for exploration
4. Federated learning for privacy
5. Real-time streaming updates
