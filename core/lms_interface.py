import json
import logging

logger = logging.getLogger(__name__)

class LMSInterface:
    def __init__(self):
        # Mock Data Database
        self.courses = [
            # Programming & Tech
            {
                "id": "py-101",
                "title": "Python for Beginners",
                "level": "Beginner",
                "skills": ["Python", "Basic Logic"],
                "career_path": ["Data Scientist", "Software Engineer", "Web Developer"],
                "url": "https://www.coursera.org/learn/python-for-everybody"
            },
            {
                "id": "ds-201",
                "title": "Data Science Fundamentals",
                "level": "Intermediate",
                "skills": ["Python", "Statistics"],
                "career_path": ["Data Scientist"],
                "url": "https://www.edx.org/learn/data-science/harvard-university-data-science-r-basics"
            },
            {
                "id": "web-101",
                "title": "Introduction to Web Development",
                "level": "Beginner",
                "skills": ["HTML", "CSS"],
                "career_path": ["Web Developer"],
                "url": "https://www.freecodecamp.org/learn/2022/responsive-web-design/"
            },
            {
                "id": "web-202",
                "title": "Advanced React Patterns",
                "level": "Advanced",
                "skills": ["JavaScript", "React"],
                "career_path": ["Web Developer"],
                "url": "https://react.dev/learn"
            },
            {
                "id": "ml-301",
                "title": "Machine Learning Mastery",
                "level": "Advanced",
                "skills": ["Python", "Math", "TensorFlow"],
                "career_path": ["Data Scientist", "AI Engineer"],
                "url": "https://www.coursera.org/specializations/machine-learning-introduction"
            },
            
            # Leadership & Management
            {
                "id": "lead-101",
                "title": "Leadership Foundations",
                "level": "Beginner",
                "skills": ["Communication", "Team Management"],
                "career_path": ["Manager", "Team Lead", "Executive"],
                "url": "https://www.coursera.org/learn/leadership-fundamentals"
            },
            {
                "id": "lead-201",
                "title": "Strategic Leadership",
                "level": "Intermediate",
                "skills": ["Strategy", "Decision Making", "Vision"],
                "career_path": ["Manager", "Executive", "Entrepreneur"],
                "url": "https://www.edx.org/learn/leadership/harvard-university-leadership-principles"
            },
            {
                "id": "lead-301",
                "title": "Executive Leadership",
                "level": "Advanced",
                "skills": ["Change Management", "Organizational Strategy"],
                "career_path": ["Executive", "CEO", "Director"],
                "url": "https://www.coursera.org/specializations/executive-leadership"
            },
            
            # Self Development & Personal Growth
            {
                "id": "self-101",
                "title": "Personal Productivity Mastery",
                "level": "Beginner",
                "skills": ["Time Management", "Goal Setting"],
                "career_path": ["Any"],
                "url": "https://www.udemy.com/course/personal-productivity/"
            },
            {
                "id": "self-201",
                "title": "Emotional Intelligence",
                "level": "Intermediate",
                "skills": ["Self-Awareness", "Empathy", "Communication"],
                "career_path": ["Manager", "Sales", "Any"],
                "url": "https://www.coursera.org/learn/emotional-intelligence"
            },
            {
                "id": "self-301",
                "title": "Mindfulness & Resilience",
                "level": "Intermediate",
                "skills": ["Stress Management", "Mindfulness"],
                "career_path": ["Any"],
                "url": "https://www.mindful.org/meditation/mindfulness-getting-started/"
            },
            
            # Sales & Marketing
            {
                "id": "sales-101",
                "title": "Sales Fundamentals",
                "level": "Beginner",
                "skills": ["Communication", "Persuasion", "Negotiation"],
                "career_path": ["Sales", "Business Development"],
                "url": "https://www.coursera.org/learn/sales-training-sales-techniques"
            },
            {
                "id": "sales-201",
                "title": "Consultative Selling",
                "level": "Intermediate",
                "skills": ["Relationship Building", "Problem Solving"],
                "career_path": ["Sales", "Account Manager"],
                "url": "https://www.linkedin.com/learning/consultative-selling"
            },
            {
                "id": "mkt-101",
                "title": "Digital Marketing Basics",
                "level": "Beginner",
                "skills": ["SEO", "Social Media", "Content Marketing"],
                "career_path": ["Marketer", "Digital Marketer"],
                "url": "https://www.coursera.org/specializations/digital-marketing"
            },
            {
                "id": "mkt-201",
                "title": "Growth Marketing",
                "level": "Intermediate",
                "skills": ["Analytics", "A/B Testing", "User Acquisition"],
                "career_path": ["Growth Marketer", "Product Manager"],
                "url": "https://www.udemy.com/course/growth-hacking/"
            },
            
            # Business & Entrepreneurship
            {
                "id": "biz-101",
                "title": "Business Strategy Essentials",
                "level": "Beginner",
                "skills": ["Business Planning", "Market Analysis"],
                "career_path": ["Entrepreneur", "Manager", "Consultant"],
                "url": "https://www.coursera.org/learn/business-strategy"
            },
            {
                "id": "biz-201",
                "title": "Startup Fundamentals",
                "level": "Intermediate",
                "skills": ["Lean Startup", "MVP", "Fundraising"],
                "career_path": ["Entrepreneur", "Founder"],
                "url": "https://www.udacity.com/course/how-to-build-a-startup--ep245"
            },
            
            # Communication & Soft Skills
            {
                "id": "comm-101",
                "title": "Effective Communication",
                "level": "Beginner",
                "skills": ["Public Speaking", "Writing", "Presentation"],
                "career_path": ["Any"],
                "url": "https://www.coursera.org/learn/communication-skills"
            },
            {
                "id": "comm-201",
                "title": "Conflict Resolution",
                "level": "Intermediate",
                "skills": ["Mediation", "Negotiation", "Active Listening"],
                "career_path": ["Manager", "HR", "Team Lead"],
                "url": "https://www.coursera.org/learn/conflict-resolution-skills"
            }
        ]

    def recommend_courses(self, goal, level, skills, career_path):
        """
        Recommend courses based on user profile.
        """
        # Normalize inputs (handle lists if LLM returns them)
        if isinstance(level, list):
            level = level[0] if level else ""
        if isinstance(skills, list):
            skills = ", ".join(skills)
        if isinstance(career_path, list):
            career_path = ", ".join(career_path)

        logger.info(f"Searching courses for: Level={level}, Career={career_path}, Skills={skills}")
        
        recommendations = []
        
        # Simple keyword matching logic
        for course in self.courses:
            score = 0
            
            # Level match
            if course["level"].lower() == level.lower():
                score += 3
            
            # Career Path match
            if any(c.lower() in career_path.lower() for c in course["career_path"]):
                score += 5
                
            # Skill overlap
            if skills and course["skills"]:
               # simple check if any skill matches
               user_skills = [s.strip().lower() for s in skills.split(',')]
               course_skills = [s.lower() for s in course["skills"]]
               if any(s in course_skills for s in user_skills):
                   score += 2

            if score > 0:
                recommendations.append({"course": course, "score": score})

        # Sort by score
        recommendations.sort(key=lambda x: x["score"], reverse=True)
        
        # Return top 3
        top_courses = [r["course"] for r in recommendations[:3]]
        return top_courses

if __name__ == "__main__":
    lms = LMSInterface()
    recs = lms.recommend_courses("Learn AI", "Beginner", "Python", "Data Scientist")
    print(json.dumps(recs, indent=2))
