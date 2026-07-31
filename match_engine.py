"""
Combines zip_lookup, the NC plan dataset, and subsidy.py into one function
that takes raw user inputs and returns a full result: rating area, benchmark
premium, subsidy amount, and matching plans with subsidy applied.
"""

import pandas as pd
import math 
from subsidy import calculate_subsidy, get_slcsp_monthly
from zip_lookup import get_rating_area_from_zip


def get_plan_match(zip_code, age, income, household_size, zip_county_df, plans_df):
    """
    zip_code: 5-digit string
    age: string matching the Age column format in plans_df, e.g. "30", "64 and over"
    income: annual household income (MAGI), number
    household_size: number of people in tax household
    zip_county_df: loaded from zip-county-NC.csv
    plans_df: loaded from clean-insurance-NC.csv

    Returns a dict with rating area, subsidy details, and a list of
    matching plans (one row per unique plan) with the subsidy applied.
    """
    rating_area, county = get_rating_area_from_zip(zip_code, zip_county_df)

    if rating_area is None:
        return {"error": f"Could not determine rating area for ZIP {zip_code}"}

    slcsp_monthly = get_slcsp_monthly(plans_df, rating_area, age)

    if slcsp_monthly is None:
        return {"error": f"No SLCSP found for {rating_area}, age {age}"}

    slcsp_annual = slcsp_monthly * 12

    subsidy_result = calculate_subsidy(
        income=income,
        household_size=household_size,
        slcsp_annual_premium=slcsp_annual,
    )

    monthly_subsidy = subsidy_result["annual_ptc"] / 12 if subsidy_result["annual_ptc"] else 0

    # Pull all plans available in this rating area + age, apply the subsidy
    available = plans_df[
        (plans_df["RatingAreaId"] == rating_area) & (plans_df["Age"] == age)
    ].copy()

    available["MonthlyPremiumAfterSubsidy"] = (
        available["IndividualRate"] - monthly_subsidy
    ).clip(lower=0)

    plan_cols = [
        "StandardComponentId", "IssuerMarketPlaceMarketingName", "PlanMarketingName",
        "MetalLevel", "PlanType", "IndividualRate", "MonthlyPremiumAfterSubsidy",
        "TEHBDedInnTier1Individual", "TEHBInnTier1IndividualMOOP",
        "Specialist Visit", "Specialist Visit_Type",
        "Generic Drugs", "Generic Drugs_Type",
    ]
    available = available[plan_cols].sort_values("MonthlyPremiumAfterSubsidy")

    matching_plans = available.to_dict(orient="records")
    # NaN isn't valid JSON -- convert missing numeric values to None so they serialize as null
    for plan in matching_plans:
        for key, value in plan.items():
            if isinstance(value, float) and math.isnan(value):
                plan[key] = None

    return {
        "zip_code": zip_code,
        "county": county,
        "rating_area": rating_area,
        "slcsp_monthly_premium": round(slcsp_monthly, 2),
        "fpl_percentage": subsidy_result["fpl_percentage"],
        "applicable_percentage": subsidy_result["applicable_percentage"],
        "monthly_subsidy": round(monthly_subsidy, 2),
        "subsidy_status": subsidy_result["status"],
        "matching_plans": matching_plans,
        "plan_count": len(available),
    }


if __name__ == "__main__":
    plans_df = pd.read_csv("clean-insurance-NC.csv")

    try:
        zip_county_df = pd.read_csv("zip-county-NC.csv")
    except FileNotFoundError:
        print("zip-county-NC.csv not found — run zip_lookup.py setup first.")
        raise SystemExit

    result = get_plan_match(
        zip_code="27601",
        age="30",
        income=35000,
        household_size=1,
        zip_county_df=zip_county_df,
        plans_df=plans_df,
    )

    print(f"ZIP: {result['zip_code']} ({result['county']} County, {result['rating_area']})")
    print(f"SLCSP monthly premium: ${result['slcsp_monthly_premium']}")
    print(f"FPL %: {result['fpl_percentage']}")
    print(f"Monthly subsidy: ${result['monthly_subsidy']}")
    print(f"Status: {result['subsidy_status']}")
    print(f"\nTop 5 cheapest matching plans (after subsidy):")
    for plan in result["matching_plans"][:5]:
        print(f"  {plan['MetalLevel']:8} | {plan['IssuerMarketPlaceMarketingName']:35} | "
              f"${plan['MonthlyPremiumAfterSubsidy']:.2f}/mo (was ${plan['IndividualRate']:.2f})")
