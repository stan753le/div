# Study Program Recommender System

A Netflix/Amazon-style recommendation system that matches student interests and grades to suggest study programs they might not have considered.

## Features

- **Advanced Hybrid Recommendation Engine**: Combines content-based filtering with ALS matrix factorization
- **Adaptive Weighting**: Intelligently balances content and collaborative signals based on user experience
- **Enhanced Explanations**: Multi-faceted reasoning that explains why programs are recommended
- **Diversity Boosting**: Prevents filter bubbles by ensuring variety in recommendations
- **Interactive Questionnaire**: Simple UI for students to input their interests and grades
- **Personalized Recommendations**: Provides top 5 program recommendations with sophisticated explanations
- **Feedback Collection**: Captures user interactions (clicks, ratings, acceptance) for continuous learning
- **Similar Programs Discovery**: Find programs similar to ones you're interested in
- **Transparent Strategy**: See how your recommendations are being calculated
- **RESTful API**: FastAPI backend with comprehensive endpoints
- **Modern UI**: React-based frontend with responsive design
- **Docker Support**: Easy deployment with Docker and Docker Compose

## Architecture

### Backend (FastAPI + Python)
- **Content-Based Recommender**: TF-IDF vectorization with cosine similarity
- **Collaborative Filtering**: ALS (Alternating Least Squares) matrix factorization
- **Hybrid System**: Adaptive weighting based on user experience
- **Explanation Engine**: Multi-faceted reasoning for transparency
- **Database**: Supabase PostgreSQL with Row Level Security
- **API Endpoints**:
  - Create/update student profiles
  - Get personalized hybrid recommendations
  - Submit feedback and retrain models
  - Retrieve program catalog
  - Get recommendation strategy (transparency)
  - Find similar programs

### Frontend (React + TypeScript)
- Interest selection interface
- Grade input for subjects
- Recommendation cards with explanations
- Feedback mechanisms

### Database Schema
- **students**: User profiles with interests and grades
- **programs**: Study program catalog with tags and skills
- **recommendations**: Generated recommendations history
- **feedback**: User interaction data for model improvement

## Prerequisites

- Docker and Docker Compose
- Supabase account (database is pre-configured)
- Python 3.11+ (for local development)
- Node.js 20+ (for local development)

## Quick Start with Docker

### 1. Clone the repository
```bash
cd project
```

### 2. Set up environment variables

Create a `.env` file in the `backend` directory:

```bash
cd backend
cp .env.example .env
```

Edit `.env` and add your Supabase credentials:
```
SUPABASE_URL=your_supabase_url_here
SUPABASE_ANON_KEY=your_supabase_anon_key_here
```

### 3. Build Docker images

From the project root:
```bash
docker-compose build
```

This will build both the backend and frontend Docker images.

### 4. Seed the database

Before starting the application, seed the database with sample study programs:

```bash
cd backend
pip install -r requirements.txt
python seed_data.py
cd ..
```

### 5. Run the application

```bash
docker-compose up
```

This will start:
- Backend API on `http://localhost:8000`
- Frontend on `http://localhost:80`

### 6. Access the application

Open your browser and navigate to:
- Frontend: `http://localhost`
- API Documentation: `http://localhost:8000/docs`

## Local Development Setup

### Backend

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables (see step 2 above)

5. Seed the database:
```bash
python seed_data.py
```

6. Run the development server:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### Frontend

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Run the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

## API Endpoints

### Students
- `POST /students` - Create a new student profile
- `GET /students/{student_id}` - Get student profile
- `PUT /students/{student_id}` - Update student profile

### Recommendations
- `POST /recommendations` - Get personalized recommendations
  - Body: `{"student_id": "uuid", "top_k": 5}`
- `GET /students/{student_id}/recommendations` - Get recommendation history

### Feedback
- `POST /feedback?student_id={id}` - Submit feedback
  - Body: `{"program_id": "uuid", "rating": 5, "clicked": true, "accepted": true}`

### Programs
- `GET /programs` - Get all available programs

## How It Works

### 1. Student Profile Creation
Students fill out a questionnaire including:
- Basic information (name, email)
- Interests (select from predefined tags)
- Subject grades (0-100 scale)

### 2. Recommendation Generation
The system:
1. Builds a TF-IDF representation of all programs
2. Creates a profile vector from student interests and high-performing subjects
3. Calculates cosine similarity between student profile and all programs
4. Returns top-K programs with personalized explanations

### 3. Explanation Generation
For each recommendation, the system generates explanations like:
> "Based on your interests in biology, drawing, your strong performance in art, you'll develop skills in design thinking, CAD software, plant science."

### 4. Feedback Collection
The system tracks:
- **Clicks**: When users view program details
- **Acceptance**: When users mark programs as interesting
- **Ratings**: Optional 1-5 star ratings

This data is stored for future model improvements.

## Evaluation Metrics

The system is designed to support the following evaluation metrics:

- **NDCG@k**: Normalized Discounted Cumulative Gain
- **Precision@k**: Proportion of relevant recommendations in top-k
- **Click-Through Rate**: Percentage of recommendations clicked
- **Acceptance Rate**: Percentage of recommendations accepted

Additional tools:
- **Offline evaluation notebook**: see [evaluation/recommendation_evaluation.ipynb](evaluation/recommendation_evaluation.ipynb) for `precision_at_k` and `ndcg_at_k` helpers.
- **Retrain endpoint**: POST `/retrain` triggers a lightweight collaborative-filtering retrain using captured feedback.

## Project Structure

```
project/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI application
│   │   ├── config.py                  # Configuration
│   │   ├── database.py                # Supabase client
│   │   ├── models.py                  # Pydantic models
│   │   ├── recommender.py             # Content-based recommender
│   │   ├── cf_recommender.py          # SVD collaborative filtering
│   │   ├── matrix_factorization.py    # ALS matrix factorization
│   │   ├── hybrid_recommender.py      # Adaptive hybrid system
│   │   ├── explanation_engine.py      # Enhanced explanations
│   │   └── cold_start.py              # Cold-start handler
│   ├── seed_data.py                   # Database seeding script
│   ├── test_enhanced_features.py      # Test suite
│   ├── requirements.txt               # Python dependencies
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── StudentForm.tsx
│   │   │   └── RecommendationsList.tsx
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── index.css
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── Dockerfile
│   └── nginx.conf
├── evaluation/
│   └── recommendation_evaluation.ipynb
├── docker-compose.yml
├── README.md
├── ENHANCED_FEATURES.md
└── IMPROVEMENTS.md
```

## Technologies Used

### Backend
- **FastAPI**: Modern web framework for building APIs
- **scikit-learn**: Machine learning library for TF-IDF and cosine similarity
- **Supabase**: PostgreSQL database with real-time capabilities
- **Pydantic**: Data validation using Python type annotations

### Frontend
- **React 18**: UI library
- **TypeScript**: Type-safe JavaScript
- **Vite**: Fast build tool and dev server

### DevOps
- **Docker**: Containerization
- **Docker Compose**: Multi-container orchestration
- **Nginx**: Web server for production frontend

## Enhanced Features

The system now includes advanced recommendation capabilities:

### Hybrid Recommendation System
- **ALS Matrix Factorization**: Advanced collaborative filtering using Alternating Least Squares
- **Adaptive Weighting**: Dynamically adjusts content/collaborative balance based on user experience
- **Diversity Boosting**: Prevents filter bubbles by ensuring recommendation variety

### Enhanced Explanations
- Multi-faceted reasoning combining interests, grades, and social proof
- Explains why each program is recommended with multiple supporting factors
- Context-aware generation based on user history

### Transparency Features
- See your recommendation strategy: `/students/{id}/recommendation-strategy`
- Discover similar programs: `/programs/{id}/similar`
- Understand how weights are calculated

### Cold-Start Handling
- Interest-based matching for new users
- Popularity-based fallback when needed
- Smooth transition to personalized recommendations

For detailed documentation, see [ENHANCED_FEATURES.md](ENHANCED_FEATURES.md)

### Test the Enhanced Features

```bash
cd backend
python3 test_enhanced_features.py
```

## Troubleshooting

### Database Connection Issues
- Ensure your Supabase URL and keys are correct in `.env`
- Check that RLS policies allow your operations
- Verify the database migration was successful

### Docker Issues
- Make sure ports 8000 and 80 are not in use
- Try `docker-compose down` and then `docker-compose up --build`

### Frontend API Errors
- Ensure backend is running on port 8000
- Check CORS settings in backend
- Verify API URL in frontend matches backend location

## License

MIT License - feel free to use this project for educational purposes.

## Contributors

Built as a demonstration of modern recommendation system architecture.
