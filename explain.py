"""
Takes the top matched plans (already computed by match_engine.py) and asks
Claude to explain them in plain English -- premium, deductible, and tradeoffs.

Important: this function only ever passes it the numbers you already computed.
Claude is told explicitly not to invent or recalculate anything, so the
explanation is grounded in real data, not the model's own math.
"""

import os
import json
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()  # reads .env and loads ANTHROPIC_API_KEY into the environment

client = Anthropic()  # automatically picks up ANTHROPIC_API_KEY from the environment

MODEL = "claude-sonnet-4-6"


def explain_plans(match_result, top_n=3):
    """
    match_result: the dict returned by get_plan_match() in match_engine.py
    top_n: how many of the cheapest matching plans to explain

    Returns a plain-English string explaining the top plans and their tradeoffs.
    """
    top_plans = match_result["matching_plans"][:top_n]

    if not top_plans:
        return "No matching plans were found for this ZIP code and age."

    # Only send the fields relevant to the explanation -- keeps the prompt
    # small and keeps Claude from having anything extra to speculate about.
    plan_summaries = [
        {
            "issuer": p["IssuerMarketPlaceMarketingName"],
            "plan_name": p["PlanMarketingName"],
            "metal_level": p["MetalLevel"],
            "monthly_premium_before_subsidy": p["IndividualRate"],
            "monthly_premium_after_subsidy": round(p["MonthlyPremiumAfterSubsidy"], 2),
            "deductible": p["TEHBDedInnTier1Individual"],
            "out_of_pocket_max": p["TEHBInnTier1IndividualMOOP"],
            "specialist_visit_cost": p["Specialist Visit"],
            "generic_drug_cost": p["Generic Drugs"],
        }
        for p in top_plans
    ]

    prompt = f"""You are explaining health insurance plan options to someone comparing ACA marketplace plans.

Here is their situation:
- Monthly subsidy: ${match_result['monthly_subsidy']}
- Subsidy status: {match_result['subsidy_status']}

Here are their top {len(plan_summaries)} cheapest matching plans, with all dollar
figures already calculated (do not recompute or guess any numbers -- use only
the numbers given below):

{json.dumps(plan_summaries, indent=2)}

Write a short, plain-English explanation (3-5 sentences per plan) covering:
- What this plan costs per month after their subsidy
- The deductible and out-of-pocket max, in context (a null value means that
  field wasn't reported for this plan, not that it's zero -- say so explicitly)
- Any real tradeoffs between the plans (e.g. lower premium vs higher deductible)

Do not invent numbers that aren't in the data above. Do not give medical or
legal advice. Keep the tone clear and neutral, like a helpful explainer, not
a sales pitch.

Formatting: write in Markdown. Use a level-3 heading (###) for each plan name,
bold (**) for key numbers, and end with a markdown comparison table summarizing
all plans side by side."""

    response = client.messages.create(
        model=MODEL,
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}],
    )

    return response.content[0].text


if __name__ == "__main__":
    # Quick manual test -- run this directly to check the explanation output
    # without going through Flask at all.
    import pandas as pd
    from match_engine import get_plan_match

    plans_df = pd.read_csv("clean-insurance-NC.csv")
    zip_county_df = pd.read_csv("zip-county-NC.csv")

    result = get_plan_match(
        zip_code="27601",
        age="30",
        income=35000,
        household_size=1,
        zip_county_df=zip_county_df,
        plans_df=plans_df,
    )

    print(explain_plans(result))
