# System Architecture

## Overview

The Study Program Recommender System uses a sophisticated hybrid approach combining multiple recommendation algorithms with adaptive weighting and enhanced explanations.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER REQUEST                             │
│                    (Student Profile + Preferences)               │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
                    ┌────────────────┐
                    │  Main API      │
                    │  (main.py)     │
                    └────────┬───────┘
                             │
                ┌────────────┴────────────┐
                │                         │
                ▼                         ▼
    ┌──────────────────┐      ┌──────────────────┐
    │ Has Feedback?    │      │  No Feedback?    │
    │                  │      │                  │
    └────────┬─────────┘      └────────┬─────────┘
             │                         │
             │ YES                     │ NO
             │                         │
             ▼                         ▼
    ┌─────────────────┐       ┌──────────────────┐
    │ HYBRID           │       │ COLD START       │
    │ RECOMMENDER      │       │ HANDLER          │
    └────────┬─────────┘       └────────┬─────────┘
             │                          │
             │                          │
    ┌────────┴────────┐                │
    │                 │                │
    ▼                 ▼                │
┌────────┐      ┌──────────┐          │
│Content │      │Collaborative│        │
│Based   │      │Filtering │          │
│        │      │(ALS)     │          │
└───┬────┘      └─────┬────┘          │
    │                 │                │
    │                 │                │
    └────────┬────────┘                │
             │                         │
             ▼                         │
    ┌─────────────────┐               │
    │ ADAPTIVE        │               │
    │ WEIGHTING       │               │
    │ (Based on user  │               │
    │  experience)    │               │
    └────────┬─────────┘               │
             │                         │
             ▼                         │
    ┌─────────────────┐               │
    │ DIVERSITY       │               │
    │ BOOSTING        │               │
    │ (Prevent filter │               │
    │  bubbles)       │               │
    └────────┬─────────┘               │
             │                         │
             └────────┬────────────────┘
                      │
                      ▼
             ┌─────────────────┐
             │ EXPLANATION     │
             │ ENGINE          │
             │ (Multi-factor)  │
             └────────┬─────────┘
                      │
                      ▼
             ┌─────────────────┐
             │ RECOMMENDATIONS │
             │ + EXPLANATIONS  │
             └─────────────────┘
```

## Component Details

### 1. Main API (`main.py`)

Entry point for all recommendation requests.

**Responsibilities:**
- Route incoming requests
- Load student and program data
- Determine recommendation strategy
- Coordinate between components
- Store results in database

### 2. Content-Based Recommender (`recommender.py`)

Uses TF-IDF and cosine similarity.

**Inputs:**
- Student interests
- High-performing subjects (grades >= 80)

**Process:**
1. Build TF-IDF vectors for all programs
2. Create student profile vector
3. Calculate cosine similarity
4. Return top-k matches

**Output:** (program, score, basic_explanation) tuples

### 3. Matrix Factorization (`matrix_factorization.py`)

ALS collaborative filtering.

**Inputs:**
- User-item interaction matrix (from feedback/recommendations)
- Confidence weights

**Process:**
1. Gather interactions from database
2. Build sparse matrix
3. Run ALS iterations (15 iterations)
4. Optimize user and item factors
5. Apply regularization

**Output:** Normalized scores (0-1) for each program

### 4. Hybrid Recommender (`hybrid_recommender.py`)

Adaptive combination of content and collaborative.

**Process:**
1. Get content-based scores
2. Get collaborative scores (if available)
3. Calculate adaptive weights based on:
   - User feedback count
   - Individual score confidence
4. Combine: `final = α * content + (1-α) * CF`
5. Apply diversity boosting
6. Generate enhanced explanations

**Adaptive Weight Calculation:**

```python
if feedback_count <= 2:
    content_weight = 0.8
elif feedback_count <= 10:
    content_weight = 0.6
else:
    content_weight = 0.4

# Adjust based on score confidence
if cf_score < 0.1:
    content_weight += 0.2
elif cf_score > 0.8 and content_score < 0.3:
    content_weight -= 0.1

cf_weight = 1.0 - content_weight
```

### 5. Explanation Engine (`explanation_engine.py`)

Multi-faceted explanation generation.

**Factors Considered:**
1. Interest matching
2. Grade performance
3. Similar student preferences
4. Program acceptance rate
5. Skills development

**Process:**
1. Match interests with program tags/skills
2. Find relevant high-grade subjects
3. Query similar students who accepted
4. Calculate program's overall acceptance rate
5. Compose natural language explanation

**Example Composition:**
```
[Interest Match], [Grade Performance], [Social Proof], and [Skills]
```

### 6. Cold-Start Handler (`cold_start.py`)

Handles new users without feedback.

**Strategies:**
1. **Interest-Based**: Match interests with program tags
2. **Popularity**: Use most accepted programs
3. **Hybrid**: Combine both approaches

**Transition:** Once user has 3+ feedback items, switches to hybrid recommender

## Data Flow

### Recommendation Generation

```
1. User Request
   ├─ student_id
   └─ top_k

2. Load Data
   ├─ Student profile (interests, grades)
   ├─ All programs
   └─ Feedback history

3. Choose Strategy
   ├─ No feedback → Cold-start
   └─ Has feedback → Hybrid

4. Generate Recommendations
   ├─ Content scores
   ├─ CF scores (if available)
   ├─ Adaptive weighting
   └─ Diversity adjustment

5. Create Explanations
   ├─ Interest matching
   ├─ Grade correlation
   ├─ Social proof
   └─ Skills focus

6. Store & Return
   ├─ Save to recommendations table
   └─ Return to user
```

### Feedback Processing

```
1. User Feedback
   ├─ clicked: boolean
   ├─ accepted: boolean
   └─ rating: 1-5 (optional)

2. Store in Database
   └─ feedback table

3. Trigger Retraining
   ├─ SVD CF model
   └─ ALS model

4. Update Recommendations
   └─ New weights based on updated history
```

## Database Schema

```sql
students
├─ id (uuid)
├─ name (text)
├─ email (text)
├─ interests (text[])
├─ grades (jsonb)
└─ created_at (timestamp)

programs
├─ id (uuid)
├─ name (text)
├─ description (text)
├─ tags (text[])
├─ skills (text[])
└─ requirements (jsonb)

recommendations
├─ id (uuid)
├─ student_id (uuid) → students.id
├─ program_id (uuid) → programs.id
├─ score (float)
├─ explanation (text)
├─ algorithm (text)
└─ created_at (timestamp)

feedback
├─ id (uuid)
├─ student_id (uuid) → students.id
├─ program_id (uuid) → programs.id
├─ clicked (boolean)
├─ accepted (boolean)
├─ rating (integer, 1-5)
└─ created_at (timestamp)
```

## API Endpoints

### Core Endpoints

```
POST   /students                          Create student profile
GET    /students/{id}                     Get student profile
PUT    /students/{id}                     Update student profile
POST   /recommendations                   Get recommendations
POST   /feedback?student_id={id}          Submit feedback
POST   /retrain                           Retrain all models
```

### Analytics Endpoints

```
GET    /analytics/engagement              Overall metrics
GET    /analytics/program-performance     Per-program stats
GET    /analytics/dashboard               Combined dashboard
```

### Transparency Endpoints

```
GET    /students/{id}/recommendation-strategy    See weighting strategy
GET    /programs/{id}/similar                    Find similar programs
```

## Scaling Considerations

### Current Implementation

- In-memory model storage
- On-demand training
- Synchronous processing

### Production Recommendations

1. **Model Storage**: Redis/Memcached for factors
2. **Training**: Async background jobs
3. **Caching**: Program vectors, user profiles
4. **Sharding**: User-based sharding for large scale
5. **Monitoring**: Track model performance metrics

## Configuration

### ALS Parameters

```python
n_factors = 50        # Latent dimensions
n_iterations = 15     # ALS iterations
reg_lambda = 0.1      # Regularization
```

### Hybrid Parameters

```python
base_content_weight = 0.6    # Default content weight
diversity_factor = 0.1       # Diversity penalty
```

### Content-Based Parameters

```python
max_features = 500           # TF-IDF max features
ngram_range = (1, 2)         # Unigrams and bigrams
grade_threshold = 80         # High-grade cutoff
```

## Performance Characteristics

### Time Complexity

- **Content-Based**: O(n) where n = number of programs
- **ALS Training**: O(k * i * s) where k=factors, i=iterations, s=interactions
- **ALS Prediction**: O(k) where k=factors
- **Hybrid**: O(n + k) combined

### Space Complexity

- **User Factors**: O(u * k) where u=users, k=factors
- **Item Factors**: O(i * k) where i=items, k=factors
- **TF-IDF Matrix**: O(p * f) where p=programs, f=features

## Error Handling

### Graceful Degradation

1. **No CF Model**: Fall back to content-based
2. **No Feedback**: Use cold-start handler
3. **Invalid Input**: Return empty results with error
4. **Database Errors**: Cache and retry

### Logging

- Model training success/failure
- Recommendation generation time
- Explanation quality metrics
- User engagement tracking

## Testing Strategy

1. **Unit Tests**: Each component independently
2. **Integration Tests**: End-to-end flow
3. **Performance Tests**: Response time, throughput
4. **Quality Tests**: NDCG, Precision@k
5. **A/B Tests**: Compare strategies

## Monitoring Metrics

1. **Model Performance**: NDCG@k, Precision@k
2. **User Engagement**: CTR, acceptance rate
3. **System Health**: Response time, error rate
4. **Business Metrics**: User satisfaction, retention
