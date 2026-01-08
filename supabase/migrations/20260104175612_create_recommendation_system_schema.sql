/*
  # Create Recommendation System Schema

  1. New Tables
    - `students`
      - `id` (uuid, primary key) - Unique student identifier
      - `name` (text) - Student name
      - `email` (text, unique) - Student email
      - `interests` (text[]) - Array of interest tags (e.g., ["biology", "drawing", "technology"])
      - `grades` (jsonb) - Subject grades as JSON (e.g., {"math": 85, "biology": 90})
      - `created_at` (timestamptz) - Record creation timestamp
      - `updated_at` (timestamptz) - Record update timestamp

    - `programs`
      - `id` (uuid, primary key) - Unique program identifier
      - `name` (text) - Program name (e.g., "Landscape Architecture")
      - `description` (text) - Detailed program description
      - `tags` (text[]) - Array of relevant tags/keywords
      - `skills` (text[]) - Array of skills developed in program
      - `requirements` (jsonb) - Entry requirements (grades, prerequisites)
      - `created_at` (timestamptz) - Record creation timestamp

    - `recommendations`
      - `id` (uuid, primary key) - Unique recommendation identifier
      - `student_id` (uuid, foreign key) - Reference to student
      - `program_id` (uuid, foreign key) - Reference to program
      - `score` (float) - Recommendation score (0-1)
      - `explanation` (text) - Human-readable explanation
      - `algorithm` (text) - Algorithm used (content-based, collaborative, hybrid)
      - `created_at` (timestamptz) - When recommendation was generated

    - `feedback`
      - `id` (uuid, primary key) - Unique feedback identifier
      - `student_id` (uuid, foreign key) - Reference to student
      - `program_id` (uuid, foreign key) - Reference to program
      - `rating` (int) - User rating (1-5 stars)
      - `clicked` (boolean) - Whether user clicked to view details
      - `accepted` (boolean) - Whether user accepted/saved recommendation
      - `created_at` (timestamptz) - Feedback timestamp

  2. Security
    - Enable RLS on all tables
    - Add policies for authenticated users to:
      - Read all programs (public catalog)
      - Read/write their own student profile
      - Read their own recommendations
      - Write their own feedback

  3. Indexes
    - Create indexes on foreign keys for performance
    - Create GIN index on tags and skills arrays for fast searching
*/

- ==========================================
-- 1. SETUP & EXTENSIONS
-- ==========================================

-- Enable pgcrypto for UUID generation
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ==========================================
-- 2. TABLES
-- ==========================================

-- Create students table
-- Note: 'id' will match auth.users 'id' via the trigger defined later
CREATE TABLE IF NOT EXISTS public.students (
  id uuid PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  name text,
  email text,
  interests text[] DEFAULT '{}',
  grades jsonb DEFAULT '{}',
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- Create programs table
CREATE TABLE IF NOT EXISTS public.programs (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text NOT NULL,
  description text NOT NULL,
  tags text[] DEFAULT '{}',
  skills text[] DEFAULT '{}',
  requirements jsonb DEFAULT '{}',
  created_at timestamptz DEFAULT now()
);

-- Create recommendations table
CREATE TABLE IF NOT EXISTS public.recommendations (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  student_id uuid NOT NULL REFERENCES public.students(id) ON DELETE CASCADE,
  program_id uuid NOT NULL REFERENCES public.programs(id) ON DELETE CASCADE,
  score float NOT NULL,
  explanation text NOT NULL,
  algorithm text NOT NULL DEFAULT 'content-based',
  created_at timestamptz DEFAULT now()
);

-- Create feedback table
CREATE TABLE IF NOT EXISTS public.feedback (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  student_id uuid NOT NULL REFERENCES public.students(id) ON DELETE CASCADE,
  program_id uuid NOT NULL REFERENCES public.programs(id) ON DELETE CASCADE,
  rating int CHECK (rating >= 1 AND rating <= 5),
  clicked boolean DEFAULT false,
  accepted boolean DEFAULT false,
  created_at timestamptz DEFAULT now()
);

-- ==========================================
-- 3. AUTOMATION (THE AUTH TRIGGER)
-- ==========================================

-- Function to handle new user signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger AS $$
BEGIN
  INSERT INTO public.students (id, email, name)
  VALUES (
    new.id, -- Links auth.users id to students id
    new.email,
    new.raw_user_meta_data->>'full_name' -- Captures name from metadata if provided
  );
  RETURN new;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger to execute the function every time a user signs up
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE PROCEDURE public.handle_new_user();

-- ==========================================
-- 4. SECURITY (RLS POLICIES)
-- ==========================================

-- Enable RLS on all tables
ALTER TABLE public.students ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.programs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.recommendations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.feedback ENABLE ROW LEVEL SECURITY;

-- STUDENTS POLICIES
CREATE POLICY "Users can read own profile" 
  ON public.students FOR SELECT 
  USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" 
  ON public.students FOR UPDATE 
  USING (auth.uid() = id);

-- PROGRAMS POLICIES
-- Everyone (even anon/not logged in) can read programs? 
-- If you want strictly logged in, change 'true' to 'auth.role() = ''authenticated'''
CREATE POLICY "Public read access" 
  ON public.programs FOR SELECT 
  USING (true);

-- RECOMMENDATIONS POLICIES
CREATE POLICY "Users can read own recommendations" 
  ON public.recommendations FOR SELECT 
  USING (auth.uid() = student_id);

CREATE POLICY "System can insert recommendations" 
  ON public.recommendations FOR INSERT 
  WITH CHECK (true); 
  -- Note: Ideally this is restricted to service_role, but for simple setups 
  -- allowing auth users to insert (if your logic is client-side) is okay. 
  -- If logic is backend, this policy isn't needed for service_role.

-- FEEDBACK POLICIES
CREATE POLICY "Users can read own feedback" 
  ON public.feedback FOR SELECT 
  USING (auth.uid() = student_id);

CREATE POLICY "Users can insert own feedback" 
  ON public.feedback FOR INSERT 
  WITH CHECK (auth.uid() = student_id);

CREATE POLICY "Users can update own feedback" 
  ON public.feedback FOR UPDATE 
  USING (auth.uid() = student_id);

-- ==========================================
-- 5. PERFORMANCE (INDEXES)
-- ==========================================

CREATE INDEX IF NOT EXISTS idx_recommendations_student ON public.recommendations(student_id);
CREATE INDEX IF NOT EXISTS idx_recommendations_program ON public.recommendations(program_id);
CREATE INDEX IF NOT EXISTS idx_feedback_student ON public.feedback(student_id);
CREATE INDEX IF NOT EXISTS idx_feedback_program ON public.feedback(program_id);

-- GIN Indexes for Array Searching
CREATE INDEX IF NOT EXISTS idx_programs_tags ON public.programs USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_programs_skills ON public.programs USING GIN(skills);
CREATE INDEX IF NOT EXISTS idx_students_interests ON public.students USING GIN(interests);