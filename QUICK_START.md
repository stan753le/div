# Quick Start Guide: Enhanced Recommendation System

## What's New

The recommendation system now includes:

1. Advanced collaborative filtering with ALS
2. Adaptive hybrid recommendations
3. Enhanced multi-factor explanations
4. Diversity boosting
5. Transparency features

## Installation

```bash
cd backend
pip install -r requirements.txt
```

## Key Files

```
backend/app/
├── matrix_factorization.py     # ALS collaborative filtering
├── hybrid_recommender.py        # Adaptive hybrid system
├── explanation_engine.py        # Enhanced explanations
└── main.py                      # Updated API endpoints
```

## Usage Examples

### 1. Get Recommendations

```python
import requests

response = requests.post(
    "http://localhost:8000/recommendations",
    json={
        "student_id": "student-uuid",
        "top_k": 5
    }
)

recommendations = response.json()
for rec in recommendations:
    print(f"{rec['program_name']}: {rec['score']:.3f}")
    print(f"  {rec['explanation']}\n")
```

### 2. Check Recommendation Strategy

```python
response = requests.get(
    "http://localhost:8000/students/student-uuid/recommendation-strategy"
)

strategy = response.json()
print(f"Content weight: {strategy['content_weight']}")
print(f"CF weight: {strategy['collaborative_weight']}")
print(f"Strategy: {strategy['strategy']}")
```

### 3. Find Similar Programs

```python
response = requests.get(
    "http://localhost:8000/programs/program-uuid/similar?limit=5"
)

similar = response.json()
for prog in similar['similar_programs']:
    print(f"{prog['program_name']}: {prog['similarity_score']:.3f}")
```

### 4. Submit Feedback

```python
response = requests.post(
    "http://localhost:8000/feedback?student_id=student-uuid",
    json={
        "program_id": "program-uuid",
        "clicked": True,
        "accepted": True,
        "rating": 5
    }
)
```

### 5. Retrain Models

```python
response = requests.post("http://localhost:8000/retrain")
result = response.json()
print(f"CF trained: {result['cf_trained']}")
print(f"ALS trained: {result['als_trained']}")
```

## Testing

```bash
cd backend
python3 test_enhanced_features.py
```

## Key Concepts

### Adaptive Weighting

The system automatically adjusts how much it trusts content-based vs collaborative filtering based on user experience:

- **New users (0-2 feedback)**: 80% content, 20% CF
- **Growing users (3-10 feedback)**: 60% content, 40% CF
- **Established users (10+ feedback)**: 40% content, 60% CF

### Diversity Boosting

Prevents recommending too many similar programs by penalizing overlap in tags and skills.

### Enhanced Explanations

Each recommendation includes multiple reasons:
- Interest matching
- Grade performance
- Social proof (similar students)
- Acceptance rate
- Skills to be developed

## API Quick Reference

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/recommendations` | Get hybrid recommendations |
| POST | `/feedback?student_id={id}` | Submit feedback |
| POST | `/retrain` | Retrain all models |

### Transparency Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/students/{id}/recommendation-strategy` | See weighting strategy |
| GET | `/programs/{id}/similar` | Find similar programs |

### Analytics Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/analytics/engagement` | Overall metrics |
| GET | `/analytics/program-performance` | Per-program stats |
| GET | `/analytics/dashboard` | Combined dashboard |

## Configuration

### ALS Parameters

Edit `backend/app/matrix_factorization.py`:

```python
als_recommender = ALSMatrixFactorization(
    n_factors=50,       # Latent dimensions (10-100)
    n_iterations=15,    # Optimization iterations (5-20)
    reg_lambda=0.1      # Regularization (0.01-1.0)
)
```

### Hybrid Parameters

Edit `backend/app/hybrid_recommender.py`:

```python
hybrid_recommender = HybridRecommender(
    base_content_weight=0.6  # Default content weight (0.0-1.0)
)

# Diversity factor in _diversify_recommendations
diversity_factor = 0.1  # Penalty strength (0.0-0.5)
```

## Common Tasks

### Add New Explanation Factor

Edit `backend/app/explanation_engine.py`:

```python
def generate_explanation(self, ...):
    # Add your new factor
    new_factor = self._calculate_new_factor(student_data, program)

    if new_factor:
        explanation_parts.append(f"new reason: {new_factor}")
```

### Adjust Adaptive Weights

Edit `backend/app/hybrid_recommender.py`:

```python
def _calculate_adaptive_weights(self, ...):
    if feedback_count <= 2:
        base_content = 0.8  # Adjust these values
    elif feedback_count <= 10:
        base_content = 0.6
    else:
        base_content = 0.4
```

### Change Weight Scheme

Edit `backend/app/matrix_factorization.py`:

```python
def add_action(record):
    weight = 0.0
    if record.get("clicked"):
        weight += 1.0  # Adjust click weight
    if record.get("accepted"):
        weight += 3.0  # Adjust accept weight
    # Add more factors...
```

## Troubleshooting

### Models Not Training

Check if there's enough data:
- Need at least 2 students with feedback
- Need at least 2 programs recommended
- Need some interactions (clicks/accepts)

### Low Quality Recommendations

- Increase feedback collection
- Adjust ALS parameters (more iterations)
- Check diversity factor
- Verify weight scheme

### Slow Performance

- Reduce ALS iterations (10 instead of 15)
- Reduce n_factors (30 instead of 50)
- Cache program vectors
- Use background jobs for training

## Evaluation

Use the evaluation notebook:

```bash
cd evaluation
jupyter notebook recommendation_evaluation.ipynb
```

Metrics to track:
- NDCG@k (ranking quality)
- Precision@k (relevance)
- Diversity (variety)
- User engagement (CTR, acceptance)

## Best Practices

1. **Regular Retraining**: Retrain after every 10-20 feedback items
2. **Monitor Strategy**: Check adaptive weights are working as expected
3. **Track Diversity**: Ensure recommendations aren't too similar
4. **A/B Testing**: Compare different configurations
5. **User Feedback**: Collect explanation quality ratings

## Documentation

- `ENHANCED_FEATURES.md`: Detailed feature documentation
- `ARCHITECTURE.md`: System architecture
- `IMPLEMENTATION_SUMMARY.md`: Implementation details
- `IMPROVEMENTS.md`: Project roadmap

## Support

For issues or questions:
1. Check the documentation files
2. Run the test suite
3. Review the evaluation notebook
4. Inspect API logs for errors

## Next Steps

1. Generate test data
2. Run test suite
3. Explore API endpoints
4. Review evaluation metrics
5. Tune parameters for your use case
