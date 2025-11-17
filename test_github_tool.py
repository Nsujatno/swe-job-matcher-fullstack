from app.agents.tools import get_first_10_github_jobs, scrape_job_posting, match_job_to_resume
# jobs = get_first_10_github_jobs.invoke({})
# print(jobs)

job1 = "https://jobs.ea.com/en_US/careers/JobDetail/Systems-Software-Engineer-Co-op/210903?utm_source=Simplify&ref=Simplify"
job2 = "https://philips.wd3.myworkdayjobs.com/jobs-and-careers/job/Bothell/Intern---Ultrasound-Imaging-Acoustics---Bothell--WA---Summer-2026_567433?utm_source=Simplify&ref=Simplify"

resume_id = "4afe7d9b-1d99-426f-becd-ac94775182ec"

job_description_1_workday = """
### Job Description
**Intern – Ultrasound Acoustics Engineering – Bothell, WA – Summer 2026**

Are you interested in an Internship opportunity with Philips? We welcome individuals who are currently pursuing an undergraduate (BS) and/or graduate (MS) degree to participate in 3 month paid intern opportunities at our site in Bothell, WA. Through this role you will gain meaningful, hands-on experience working for a HealthTech company.

**Your role:**
  * You will support North America signal path acoustic engineers by engaging in prototyping on GPU and testing activities related to real-time imaging applications, signal processing, beamforming, and advanced imaging algorithms.
  * Analyses, designs, tests, codes, secures, debugs, modifies, deploys, integrates and maintains (system) software enhancements, test environment and/or new software in GPU environment.

  * Uses state-of-the-art technologies and practices. Interacts with users / product owners to define / adjust requirements and/or necessary modifications.
  * Keeps abreast of technical developments and practices in own field through literature, courses/trainings, technical contacts, and competitive environment.
  * Apply acoustic wave propagation in healthcare, develop signal processing theory to ultrasound system design.
  * Participate in development and implementation of new ultrasound imaging capabilities: including development plans, algorithm design, integration strategy, and SW implementation.
  * Participate in the design, development, and integration of new ultrasound systems and transducers.
  * Develop and participate in medical ultrasound feasibility and research projects to support research and development.

**You're the right fit if:**
  * Pursuing BS or MS in Electrical Engineering, Biomedical Engineering, Aerospace Engineering, Physics, or Computer Science

  * GPU/CUDA experience
  * Matlab, Python, R, or C++ programming languages

  * Experience in signal and / or image processing

  * Experience in AI and deep learning

  * Demonstrate excellent written and verbal interpersonal skills

  * Excellent problem-solving skills

  * You must be able to successfully perform the following minimum Physical, Cognitive and Environmental job requirements with or without accommodation for this position.
**How we work together**
We believe that we are better together than apart. For our office-based teams, this means working in-person at least 3 days per week. Onsite roles require full-time presence in the company’s facilities. Field roles are most effectively done outside of the company’s main facilities, generally at the customers’ or suppliers’ locations.
This is an office role.
**About Philips**
We are a health technology company. We built our entire company around the belief that every human matters, and we won't stop until everybody everywhere has access to the quality healthcare that we all deserve. Do the work of your life to help improve the lives of others.
  * Learn more about our business.
  * Discover our rich and exciting history.
  * Learn more about our purpose.
  * Learn more about our culture.
**Philips Transparency Details**

The hourly pay range for this position is $25.00 to $36.00, plus overtime eligible. The actual base pay offered may vary within the posted ranges depending on multiple factors including job-related knowledge/skills, experience, business needs, geographical location, and internal equity.
Details about our benefits can be found here.
At Philips, it is not typical for an individual to be hired at or near the top end of the range for their role and compensation decisions are dependent upon the facts and circumstances of each case.
**Additional Information**
US work authorization is a precondition of employment. The company will not consider candidates who require sponsorship for a work-authorized visa, now or in the future.
Company relocation benefits _**will not**_ be provided for this position. For this position, you must reside in _**or**_ within commuting distance to Bothell, WA**.**
This requisition is expected to stay active for 45 days but may close earlier if a successful candidate is selected or business necessity dictates. Interested candidates are encouraged to apply as soon as possible to ensure consideration.

The hourly pay range for this position is $25.00 to $36.00, plus overtime eligible. The actual base pay offered may vary within the posted ranges depending on multiple factors including job-related knowledge/skills, experience, business needs, geographical location, and internal equity.
Details about our benefits can be found here.
At Philips, it is not typical for an individual to be hired at or near the top end of the range for their role and compensation decisions are dependent upon the facts and circumstances of each case.
**Additional Information**
US work authorization is a precondition of employment. The company will not consider candidates who require sponsorship for a work-authorized visa, now or in the future.
Company relocation benefits _**will not**_ be provided for this position. For this position, you must reside in _**or**_ within commuting distance to Bothell, WA**.**
This requisition is expected to stay active for 45 days but may close earlier if a successful candidate is selected or business necessity dictates. Interested candidates are encouraged to apply as soon as possible to ensure consideration.
"""

# job = scrape_job_posting.invoke(job2)
# print(job)

# job = match_job_to_resume(job_description_1_workday, resume_id)
# print(job)