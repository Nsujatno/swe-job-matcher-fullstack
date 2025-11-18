from app.agents.tools import get_first_3_github_jobs, scrape_job_posting, match_job_to_resume, explain_job_match
# jobs = get_first_3_github_jobs.invoke({})
# print(jobs)

job1 = "https://jobs.ea.com/en_US/careers/JobDetail/Systems-Software-Engineer-Co-op/210903?utm_source=Simplify&ref=Simplify"
job2 = "https://philips.wd3.myworkdayjobs.com/jobs-and-careers/job/Bothell/Intern---Ultrasound-Imaging-Acoustics---Bothell--WA---Summer-2026_567433?utm_source=Simplify&ref=Simplify"
job3 = "https://smithnephew.wd5.myworkdayjobs.com/en-US/External/job/Pittsburgh-PA/Intern-Robotics-Software--Pittsburgh--PA-_R86302?utm_source=Simplify&ref=Simplify"
job4 = "https://alsacstjude.wd1.myworkdayjobs.com/careersalsacstjude/job/Memphis-TN/Summer-2026-Intern---AI-Software-Engineer--Memphis--TN-_R0010291?utm_source=Simplify&ref=Simplify"

resume_id = "4afe7d9b-1d99-426f-becd-ac94775182ec"
resume_id_2 = "79e8ee7d-bcfe-4ce7-9526-d62de005b66e"

job_description_test = """
## _Job Description_
**Join the team behind one of the most trusted nonprofit brands in the world. ALSAC is the fundraising and awareness organization for St. Jude Children’s Research Hospital.**
Our**paid summer internship program** _Finding cures. Saving children._
**What You’ll**
Over10 weeks,you’llHere’s
  * **Meaningful Projects**
  * **Mentorship & Collaboration**
  * **Exclusive Chats** with ALSAC’s Executive Leadership Team
  * **Intern Project** you’ll
Named one of the**Top 100 Internship Programs in the U.S.** WayUp**impactful, collaborative, and inspiring**.
**Internship Details:**
  * **Dates** : June 1 – August 7, 2026
  * **Schedule** : Full-time,40 hours/week (Monday–Friday)
  * **Pay** : $14/hour
  * **Location** : Headquarters Office in Memphis, TN
**Application Process:**
After yousubmit _stjude.org/alsacintern_ _intern@alsac.stjude.org_.

**Qualifications:**
  * Must be currently enrolled as an undergraduate or graduate student at an accredited college/university or May 2026 graduate
  * Passionate about our mission

  * Strong organizational skills to manage multiple projects simultaneously
  * Must be 18 years of age or older
**Internship Focus:**

The Cultivation & Retention team is seeking an AI Software Engineering Intern to join our mission of enhancing donor engagement through intelligent, scalable, and user-friendly solutions. This internship offers hands-on experience in full-stack development with a focus on integrating AI technologies into modern web applications and backend systems.
**Key Projects Include:**
  * Building and enhancing donor self-service capabilities with AI-driven personalization.
  * Developing secure and responsive UI components using**NextJS**
  * Creating robust backend services using**Java** ,**Spring Boot** , and integrating**AI models**
  * Designing and integrating APIs and microservices to support logged-in user features and AI-powered recommendations.
**Daily Tasks:**
  * Participate in Agile ceremonies including daily standups, sprint planning, and retrospectives.
  * Collaborate with engineers, designers, and product managers to deliver new AI-enhanced features.
  * Write clean, maintainable code and contribute to code reviews.
  * Troubleshoot bugs andoptimize
**Majors Preferred :**Master’sBachelor’s inComputer Science,Information Technology,Artificial Intelligence, or related fields.

**Skills Preferred:**
  * **Frontend** :NextJS, ReactJS, or similar UI technologies.
  * **Backend** : Java, Spring Boot.
  * **AI/ML** : Familiarity with Python, TensorFlow,PyTorch, or similar frameworks.

  * Experience with REST APIs, Git, and Agile development practices.

  * Strong problem-solving and communication skills.
# **_Benefits & Perks_**
## _The following Benefits & Perks apply to _Full-Time Roles_ _Only**.**__
## _We’re dedicated to ensuring children and their families have every opportunity to enjoy life’s special moments. We’re also committed to giving our staff excellent benefits so they can do the same._
  * Core Medical Coverage: (low cost low deductible Medical, Dental, and Vison Insurance plans)​
  * 401K Retirement Plan with 7% Employer Contribution
  * Exceptional Paid Time Off
  * Maternity / Paternity Leave
  * Infertility Treatment Program
  * Adoption Assistance
  * Education Assistance
  * Enterprise Learning and Development
  * And more

  * Strong problem-solving and communication skills.
# **_Benefits & Perks_**
## _The following Benefits & Perks apply to _Full-Time Roles_ _Only**.**__
## _We’re dedicated to ensuring children and their families have every opportunity to enjoy life’s special moments. We’re also committed to giving our staff excellent benefits so they can do the same._
  * Core Medical Coverage: (low cost low deductible Medical, Dental, and Vison Insurance plans)​
  * 401K Retirement Plan with 7% Employer Contribution
  * Exceptional Paid Time Off
  * Maternity / Paternity Leave
  * Infertility Treatment Program
  * Adoption Assistance
  * Education Assistance
  * Enterprise Learning and Development
  * And more
"""

# result = diagnose_workday_site(job3)
# print(result)

# job = scrape_job_posting.invoke(job4)
# print(job)

# job = match_job_to_resume(job_description_1_workday, resume_id_2)
# print(job)

# explanation = explain_job_match.invoke({
#     "company": "Philips",
#     "title": "Ultrasound Imaging Acoustics Intern",
#     "job_description": """
#     Intern working on GPU-based signal processing for ultrasound imaging.
#     Requires: GPU/CUDA, Python/Matlab, signal processing, AI/ML experience.
#     """,
#     "matched_sections": [
#         {
#             "text": "Experience: Software Engineer Intern at TechCorp - REST APIs with FastAPI",
#             "type": "experience",
#             "relevance": 33.4
#         },
#         {
#             "text": "Skills: Python, FastAPI, PostgreSQL, REST APIs, Docker",
#             "type": "skills",
#             "relevance": 21.1
#         }
#     ],
#     "match_score": 30.9
# })

# print(explanation)

result = match_job_to_resume.invoke({
    "job_description": job_description_test,
    "resume_id": resume_id_2
})

print(f"Match Score: {result['match_score']}%")
print(f"Message: {result['message']}")