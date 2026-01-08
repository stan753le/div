import { useState } from 'react'

interface StudentFormProps {
  onSubmit: (data: {
    name: string
    email: string
    interests: string[]
    grades: Record<string, number>
  }) => void
  loading: boolean
}

const availableInterests = [
  'art',
  'biology',
  'business',
  'chemistry',
  'computers',
  'design',
  'drawing',
  'engineering',
  'environment',
  'fashion',
  'health',
  'history',
  'math',
  'music',
  'nature',
  'people',
  'physics',
  'programming',
  'psychology',
  'science',
  'technology',
  'writing',
]

const subjects = [
  'math',
  'physics',
  'chemistry',
  'biology',
  'english',
  'history',
  'geography',
  'art',
  'music',
  'computer science',
]

function StudentForm({ onSubmit, loading }: StudentFormProps) {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [selectedInterests, setSelectedInterests] = useState<string[]>([])
  const [grades, setGrades] = useState<Record<string, number>>({})

  const toggleInterest = (interest: string) => {
    setSelectedInterests((prev) =>
      prev.includes(interest)
        ? prev.filter((i) => i !== interest)
        : [...prev, interest]
    )
  }

  const handleGradeChange = (subject: string, value: string) => {
    const numValue = parseFloat(value)
    if (!isNaN(numValue) && numValue >= 0 && numValue <= 100) {
      setGrades((prev) => ({ ...prev, [subject]: numValue }))
    } else if (value === '') {
      setGrades((prev) => {
        const newGrades = { ...prev }
        delete newGrades[subject]
        return newGrades
      })
    }
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    if (!name || !email || selectedInterests.length === 0) {
      alert('Please fill in all required fields')
      return
    }

    onSubmit({
      name,
      email,
      interests: selectedInterests,
      grades,
    })
  }

  return (
    <form onSubmit={handleSubmit} className="card">
      <h2 style={{ marginBottom: '1.5rem' }}>Tell us about yourself</h2>

      <div className="form-group">
        <label htmlFor="name">Name *</label>
        <input
          id="name"
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Enter your name"
          required
        />
      </div>

      <div className="form-group">
        <label htmlFor="email">Email *</label>
        <input
          id="email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="Enter your email"
          required
        />
      </div>

      <div className="form-group">
        <label>Interests * (select at least one)</label>
        <div className="interests-grid">
          {availableInterests.map((interest) => (
            <button
              key={interest}
              type="button"
              className={`interest-tag ${
                selectedInterests.includes(interest) ? 'selected' : ''
              }`}
              onClick={() => toggleInterest(interest)}
            >
              {interest}
            </button>
          ))}
        </div>
      </div>

      <div className="form-group">
        <label>Your Grades (0-100, optional)</label>
        <div className="grades-grid">
          {subjects.map((subject) => (
            <div key={subject} className="grade-input">
              <label htmlFor={subject}>{subject}</label>
              <input
                id={subject}
                type="number"
                min="0"
                max="100"
                value={grades[subject] || ''}
                onChange={(e) => handleGradeChange(subject, e.target.value)}
                placeholder="0-100"
              />
            </div>
          ))}
        </div>
      </div>

      <button type="submit" className="button" disabled={loading}>
        {loading ? 'Getting Recommendations...' : 'Get Recommendations'}
      </button>
    </form>
  )
}

export default StudentForm
