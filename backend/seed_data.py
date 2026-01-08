import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_ANON_KEY")
)

programs_data = [
    {
        "name": "Landscape Architecture",
        "description": "Combine creativity with environmental science to design outdoor spaces. This program integrates biological knowledge with artistic design principles to create sustainable and beautiful landscapes. Students learn about plant biology, ecology, design theory, and environmental planning.",
        "tags": ["biology", "drawing", "art", "design", "environment", "nature", "sustainability", "outdoor", "creative"],
        "skills": ["design thinking", "CAD software", "plant science", "environmental planning", "drawing", "project management"],
        "requirements": {"min_grade": 70, "preferred_subjects": ["biology", "art", "geography"]}
    },
    {
        "name": "Computer Science",
        "description": "Master programming, algorithms, and software development. Learn to build applications, solve complex problems, and understand the theoretical foundations of computing. Covers areas like AI, databases, web development, and system design.",
        "tags": ["technology", "programming", "math", "logic", "computers", "software", "problem-solving", "analytical"],
        "skills": ["programming", "algorithms", "data structures", "software engineering", "problem solving", "mathematics"],
        "requirements": {"min_grade": 75, "preferred_subjects": ["math", "physics", "computer science"]}
    },
    {
        "name": "Marine Biology",
        "description": "Explore ocean life and aquatic ecosystems. Study marine organisms, their behaviors, and their environments. Conduct field research, learn about conservation, and understand the complex relationships in marine ecosystems.",
        "tags": ["biology", "ocean", "nature", "science", "environment", "animals", "research", "conservation", "outdoor"],
        "skills": ["research methods", "field work", "data analysis", "scuba diving", "ecology", "conservation"],
        "requirements": {"min_grade": 72, "preferred_subjects": ["biology", "chemistry", "geography"]}
    },
    {
        "name": "Graphic Design",
        "description": "Create visual communications that inspire and inform. Learn typography, color theory, branding, and digital design tools. Develop your artistic vision while mastering technical skills in industry-standard software.",
        "tags": ["art", "design", "creative", "drawing", "digital", "visual", "technology", "communication"],
        "skills": ["Adobe Creative Suite", "typography", "branding", "visual communication", "creativity", "drawing"],
        "requirements": {"min_grade": 65, "preferred_subjects": ["art", "design", "computer science"]}
    },
    {
        "name": "Data Science",
        "description": "Extract insights from data using statistics, programming, and machine learning. Learn to analyze large datasets, build predictive models, and communicate findings. Combines mathematics, computer science, and domain expertise.",
        "tags": ["math", "statistics", "programming", "technology", "analytical", "problem-solving", "computers", "research"],
        "skills": ["Python", "statistics", "machine learning", "data visualization", "SQL", "critical thinking"],
        "requirements": {"min_grade": 78, "preferred_subjects": ["math", "computer science", "statistics"]}
    },
    {
        "name": "Environmental Engineering",
        "description": "Design solutions for environmental challenges. Apply engineering principles to protect air, water, and soil quality. Work on sustainable infrastructure, waste management, and pollution control systems.",
        "tags": ["environment", "engineering", "science", "sustainability", "nature", "problem-solving", "technology", "math"],
        "skills": ["engineering design", "environmental science", "project management", "CAD", "sustainability planning"],
        "requirements": {"min_grade": 76, "preferred_subjects": ["math", "physics", "chemistry", "biology"]}
    },
    {
        "name": "Psychology",
        "description": "Understand human behavior and mental processes. Study cognition, development, social interactions, and mental health. Learn research methods and apply psychological principles to real-world situations.",
        "tags": ["psychology", "people", "behavior", "research", "science", "communication", "social", "analytical"],
        "skills": ["research methods", "statistical analysis", "counseling", "communication", "critical thinking"],
        "requirements": {"min_grade": 70, "preferred_subjects": ["biology", "psychology", "sociology"]}
    },
    {
        "name": "Mechanical Engineering",
        "description": "Design and build mechanical systems and machines. Learn about mechanics, thermodynamics, materials science, and manufacturing. Apply physics and mathematics to create innovative solutions.",
        "tags": ["engineering", "math", "physics", "technology", "design", "problem-solving", "analytical", "hands-on"],
        "skills": ["CAD", "mechanics", "thermodynamics", "manufacturing", "problem solving", "mathematics"],
        "requirements": {"min_grade": 80, "preferred_subjects": ["math", "physics", "design"]}
    },
    {
        "name": "Digital Marketing",
        "description": "Master modern marketing strategies in the digital age. Learn SEO, social media marketing, content creation, analytics, and campaign management. Combine creativity with data-driven decision making.",
        "tags": ["business", "technology", "communication", "creative", "social", "digital", "writing", "analytical"],
        "skills": ["SEO", "social media", "content marketing", "analytics", "copywriting", "strategy"],
        "requirements": {"min_grade": 68, "preferred_subjects": ["business", "english", "computer science"]}
    },
    {
        "name": "Biomedical Engineering",
        "description": "Combine engineering with medical sciences to improve healthcare. Design medical devices, prosthetics, and diagnostic equipment. Bridge the gap between engineering innovation and medical applications.",
        "tags": ["biology", "engineering", "medicine", "technology", "science", "health", "problem-solving", "research"],
        "skills": ["engineering design", "biology", "medical devices", "CAD", "research methods", "mathematics"],
        "requirements": {"min_grade": 82, "preferred_subjects": ["biology", "physics", "math", "chemistry"]}
    },
    {
        "name": "Architecture",
        "description": "Design buildings and spaces that shape how people live. Combine artistic vision with technical knowledge, structural engineering, and sustainable practices. Create functional and beautiful built environments.",
        "tags": ["design", "art", "drawing", "math", "creative", "engineering", "technology", "visual"],
        "skills": ["architectural design", "CAD", "3D modeling", "drawing", "structural analysis", "creativity"],
        "requirements": {"min_grade": 75, "preferred_subjects": ["math", "art", "physics"]}
    },
    {
        "name": "Music Production",
        "description": "Create and produce music using modern technology. Learn audio engineering, mixing, composition, and digital audio workstations. Combine musical creativity with technical production skills.",
        "tags": ["music", "creative", "art", "technology", "audio", "digital", "performance", "sound"],
        "skills": ["audio engineering", "music theory", "DAW software", "mixing", "composition", "sound design"],
        "requirements": {"min_grade": 65, "preferred_subjects": ["music", "computer science", "math"]}
    },
    {
        "name": "Artificial Intelligence",
        "description": "Build intelligent systems that learn and adapt. Study machine learning, neural networks, natural language processing, and computer vision. Apply AI to solve real-world problems.",
        "tags": ["technology", "programming", "math", "computers", "AI", "machine-learning", "analytical", "research"],
        "skills": ["Python", "machine learning", "deep learning", "mathematics", "algorithms", "data science"],
        "requirements": {"min_grade": 85, "preferred_subjects": ["math", "computer science", "statistics"]}
    },
    {
        "name": "Fashion Design",
        "description": "Create innovative clothing and accessories. Learn garment construction, textile science, pattern making, and fashion illustration. Develop your unique design aesthetic while mastering technical skills.",
        "tags": ["art", "design", "creative", "drawing", "fashion", "sewing", "visual", "business"],
        "skills": ["fashion illustration", "pattern making", "sewing", "textiles", "design software", "creativity"],
        "requirements": {"min_grade": 65, "preferred_subjects": ["art", "design", "business"]}
    },
    {
        "name": "Cybersecurity",
        "description": "Protect digital systems from threats and attacks. Learn about network security, cryptography, ethical hacking, and risk management. Develop skills to secure information and infrastructure.",
        "tags": ["technology", "computers", "programming", "security", "problem-solving", "analytical", "networks"],
        "skills": ["network security", "cryptography", "penetration testing", "risk assessment", "programming"],
        "requirements": {"min_grade": 78, "preferred_subjects": ["computer science", "math"]}
    },
    {
        "name": "Game Design",
        "description": "Create engaging interactive entertainment experiences. Learn game mechanics, level design, storytelling, and game engines. Combine creativity, programming, and art to build compelling games.",
        "tags": ["technology", "creative", "art", "programming", "design", "digital", "storytelling", "visual"],
        "skills": ["Unity/Unreal Engine", "game mechanics", "3D modeling", "programming", "storytelling", "design"],
        "requirements": {"min_grade": 70, "preferred_subjects": ["computer science", "art", "design"]}
    },
    {
        "name": "Nutrition Science",
        "description": "Study food, health, and human nutrition. Learn about metabolism, dietary planning, food chemistry, and public health. Apply scientific knowledge to promote healthy eating and prevent disease.",
        "tags": ["biology", "health", "science", "food", "research", "people", "wellness", "chemistry"],
        "skills": ["nutrition assessment", "biochemistry", "research methods", "counseling", "food science"],
        "requirements": {"min_grade": 73, "preferred_subjects": ["biology", "chemistry", "health"]}
    },
    {
        "name": "Film Production",
        "description": "Tell stories through moving images. Learn cinematography, directing, editing, and screenwriting. Master both creative and technical aspects of filmmaking from concept to final cut.",
        "tags": ["creative", "art", "technology", "storytelling", "visual", "digital", "communication", "media"],
        "skills": ["cinematography", "video editing", "directing", "screenwriting", "lighting", "sound design"],
        "requirements": {"min_grade": 68, "preferred_subjects": ["art", "english", "media studies"]}
    },
    {
        "name": "Renewable Energy Engineering",
        "description": "Develop sustainable energy solutions for the future. Focus on solar, wind, and other renewable technologies. Apply engineering principles to create efficient and environmentally friendly energy systems.",
        "tags": ["engineering", "environment", "sustainability", "technology", "science", "math", "problem-solving", "nature"],
        "skills": ["renewable energy systems", "electrical engineering", "sustainability", "project management"],
        "requirements": {"min_grade": 77, "preferred_subjects": ["physics", "math", "chemistry"]}
    },
    {
        "name": "Business Analytics",
        "description": "Use data to drive business decisions. Learn statistical analysis, data mining, visualization, and business intelligence. Bridge the gap between data science and business strategy.",
        "tags": ["business", "math", "technology", "analytical", "statistics", "problem-solving", "data", "strategy"],
        "skills": ["data analysis", "statistics", "SQL", "business intelligence", "Excel", "data visualization"],
        "requirements": {"min_grade": 72, "preferred_subjects": ["math", "business", "computer science"]}
    }
]

def seed_programs():
    try:
        existing = supabase.table("programs").select("id").execute()
        if existing.data:
            print(f"Programs already exist ({len(existing.data)} found). Skipping seed.")
            return

        result = supabase.table("programs").insert(programs_data).execute()
        print(f"Successfully seeded {len(result.data)} programs!")

    except Exception as e:
        print(f"Error seeding programs: {e}")

if __name__ == "__main__":
    seed_programs()
