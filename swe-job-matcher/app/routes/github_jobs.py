from typing import List, Dict
import requests
from bs4 import BeautifulSoup
from fastapi import APIRouter, HTTPException

router = APIRouter()

GITHUB_URL = "https://raw.githubusercontent.com/SimplifyJobs/Summer2026-Internships/dev/README.md"

def get_github_jobs(limit: int = 40) -> List[Dict]:
  try:
    r = requests.get(GITHUB_URL, timeout=10)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    table = soup.find("table")
    if not table:
      raise ValueError("No table found on page")

    body = table.find("tbody")
    rows = body.find_all("tr")

    jobs: List[Dict] = []

    for row in rows:
      if len(jobs) >= limit:
        break

      cells = row.find_all("td")
      if len(cells) < 4:
        continue

      raw_company = cells[0].get_text(strip=True)

      # Skip sub‑listings
      if "↳" in raw_company or not raw_company:
        continue

      company = raw_company
      role = cells[1].get_text(strip=True)
      location = cells[2].get_text(strip=True)

      link_tag = cells[3].find("a")
      link = link_tag["href"] if link_tag else "No link"

      jobs.append(
        {
          "company": company,
          "role": role,
          "location": location,
          "link": link,
        }
      )

    return jobs
  except Exception as e:
      raise HTTPException(status_code=502, detail=f"Failed to fetch jobs: {e}")

@router.get("/get_jobs")
def get_jobs(limit: int = 40):
    jobs = get_github_jobs(limit=limit)
    return jobs