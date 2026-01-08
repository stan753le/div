import { useState } from 'react'
import StudentForm from './components/StudentForm'
import RecommendationsList from './components/RecommendationsList'

interface Student {
  id: string
  name: string
  email: string
  interests: string[]
  grades: Record<string, number>
}

interface Recommendation {
  program_id: string
  program_name: string
  program_description: string
  score: number
  explanation: string
  tags: string[]
  skills: string[]
}

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function App() {
  const [student, setStudent] = useState<Student | null>(null)
  const [recommendations, setRecommendations] = useState<Recommendation[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleStudentSubmit = async (studentData: Omit<Student, 'id'>) => {
    setLoading(true)
    setError(null)

    try {
      const createResponse = await fetch(`${API_BASE}/students`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(studentData),
      })

      if (!createResponse.ok) {
        throw new Error('Failed to create student profile')
      }

      const { student: createdStudent } = await createResponse.json()
      setStudent(createdStudent)

      const recResponse = await fetch(`${API_BASE}/recommendations`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          student_id: createdStudent.id,
          top_k: 5,
        }),
      })

      if (!recResponse.ok) {
        throw new Error('Failed to get recommendations')
      }

      const recs = await recResponse.json()
      setRecommendations(recs)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  const handleFeedback = async (programId: string, feedbackType: 'clicked' | 'accepted') => {
    if (!student) return

    try {
      const feedbackData = {
        program_id: programId,
        clicked: feedbackType === 'clicked',
        accepted: feedbackType === 'accepted',
      }

      await fetch(`${API_BASE}/feedback?student_id=${student.id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(feedbackData),
      })
    } catch (err) {
      console.error('Failed to submit feedback:', err)
    }
  }

  const handleReset = () => {
    setStudent(null)
    setRecommendations([])
    setError(null)
  }

  return (
    <div className="container">
      <div className="header">
        <h1>Study Program Recommender</h1>
        <p>
          Discover study programs that match your interests and strengths.
          Answer a few questions and get personalized recommendations.
        </p>
      </div>

      {error && <div className="error">{error}</div>}

      {!student ? (
        <StudentForm onSubmit={handleStudentSubmit} loading={loading} />
      ) : (
        <>
          <div className="card">
            <h2>Welcome, {student.name}!</h2>
            <p style={{ marginTop: '0.5rem', color: '#666' }}>
              Based on your profile, here are our top recommendations:
            </p>
            <button
              onClick={handleReset}
              style={{
                marginTop: '1rem',
                padding: '0.5rem 1rem',
                background: 'transparent',
                border: '2px solid #667eea',
                borderRadius: '8px',
                color: '#667eea',
                cursor: 'pointer',
                fontWeight: 600,
              }}
            >
              Start Over
            </button>
          </div>

          {loading ? (
            <div className="loading">Loading recommendations...</div>
          ) : (
            <RecommendationsList
              recommendations={recommendations}
              onFeedback={handleFeedback}
            />
          )}
        </>
      )}
    </div>
  )
}

export default App
