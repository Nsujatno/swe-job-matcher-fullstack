from app.agents.tools import get_first_10_github_jobs, scrape_job_posting
# jobs = get_first_10_github_jobs.invoke({})
# print(jobs)

job = scrape_job_posting.invoke("https://philips.wd3.myworkdayjobs.com/jobs-and-careers/job/Bothell/Intern---Ultrasound-Imaging-Acoustics---Bothell--WA---Summer-2026_567433?utm_source=Simplify&ref=Simplify")
print(job)