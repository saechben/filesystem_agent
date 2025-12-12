from __future__ import annotations

from pathlib import Path
import shutil

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
AGENT_ROOT = DATA_DIR / "agent_workspace"

SAMPLE_FILES = {
    "project_plan.md": """# Project Plan

## Objective
Launch the new client onboarding portal by the end of Q3 while meeting security and compliance requirements.

## Milestones
- Discovery interviews with stakeholders
- Wireframes + UX validation sprint
- Backend API implementation
- Integration testing and security review
- Beta rollout to top 5 customers

## Action Items
- Assign tasks to engineering team
- Track deliverables in Jira
- Prepare executive progress report
""",
    "meeting_notes.txt": """Meeting Notes (Work)

Participants: Product, Finance, Sales Engineering

- Follow up with finance on budget adjustments for cloud spend
- Prepare slide deck covering roadmap risks
- Email client regarding onboarding timeline expectations
- Capture questions about single sign-on support
- Schedule next sync for Tuesday 10am
""",
    "holiday_itinerary.txt": """Holiday Itinerary (Private)

Destination: Lisbon + Cascais

1. Book flights to Lisbon departing July 8, returning July 18
2. Reserve Airbnb near the beach for nights 1-5, boutique hotel in city center for nights 6-10
3. Compile restaurant list (Time Out Market, Cervejaria Ramiro, Ao 26 Vegan)
4. Plan day trips to Sintra and Cascais with train schedules
5. Create packing checklist for camera gear, sunscreen, and adapters
""",
    "family_budget.xlsx.txt": """Family Budget (Private)

Categories:
- Rent / Mortgage
- Utilities (power, water, internet)
- Groceries and household essentials
- Transportation (fuel, metro cards, maintenance)
- Kids activities and daycare
- Savings goals: emergency fund + vacation fund

Notes:
- Review subscription services for potential cuts
- Track monthly spending in spreadsheet tab "2025"
""",
    "recipe_book.md": """# Favorite Recipes (Private)

## Comfort Foods
- Grandma's lasagna with homemade ricotta
- Vegan ramen with miso broth

## Quick Meals
- Chickpea tacos with lime slaw
- 10-minute stir-fry with seasonal veggies

## Drinks & Treats
- Quick breakfast smoothies (banana + spinach + oat milk)
- Cold brew concentrate with vanilla syrup
- Dark chocolate energy bites
""",
}


def initialize_agent_data():
    """Reset the agent workspace directory with sample files."""
    if AGENT_ROOT.exists():
        shutil.rmtree(AGENT_ROOT)
    AGENT_ROOT.mkdir(parents=True, exist_ok=True)

    for filename, content in SAMPLE_FILES.items():
        file_path = AGENT_ROOT / filename
        file_path.write_text(content.strip() + "\n", encoding="utf-8")

    return AGENT_ROOT
if __name__ == "__main__":
    initialize_agent_data()
