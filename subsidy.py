"""
This script calculates Affordable Care Act (ACA) Premium Tax Credits (PTC) 
Basically, it estimates how much government subsidy a person/household receives to help pay for a health insurance plan. 
It does this using:

Household income
Household size
Federal Poverty Level (FPL) percentage
The benchmark insurance premium (SLCSP = Second Lowest Cost Silver Plan)

It has two main purposes:

Test the subsidy math using fake premiums
Use actual North Carolina insurance dataset (clean-insurance-NC.csv) to find the benchmark premium and calculate subsidies

Based on IRS Rev. Proc. 2025-25 rules, effective for 2026 plan-year coverage
(enhanced ARPA/IRA subsidies expired end of 2025; original ACA cliff structure restored).

"""

import pandas as pd

FPL_2025 = {
    1: 15650, 2: 21150, 3: 26650, 4: 32150,
    5: 37650, 6: 43150, 7: 48650, 8: 54150,
}


def get_fpl(household_size):
    if household_size <= 8:
        return FPL_2025[household_size]
    return FPL_2025[8] + (household_size - 8) * 5500


def get_applicable_percentage(fpl_pct):
    """
    Returns the required contribution rate as a decimal (e.g. 0.0314 = 3.14%).
    Returns None if outside the 100%-400% FPL eligibility window.
    """
    if fpl_pct < 100:
        return None
    if fpl_pct > 400:
        return None

    brackets = [
        (0,   133, 0.0210, 0.0210),
        (133, 150, 0.0314, 0.0419),
        (150, 200, 0.0419, 0.0660),
        (200, 250, 0.0660, 0.0844),
        (250, 300, 0.0844, 0.0996),
        (300, 400, 0.0996, 0.0996),
    ]

    for lower, upper, pct_lower, pct_upper in brackets:
        if lower <= fpl_pct <= upper:
            if upper == lower:
                return pct_lower
            frac = (fpl_pct - lower) / (upper - lower)
            return pct_lower + frac * (pct_upper - pct_lower)

    return None


def calculate_subsidy(income, household_size, slcsp_annual_premium):
    """
    income: annual household income (MAGI)
    household_size: number of people in tax household
    slcsp_annual_premium: annual premium of the benchmark
        (second-lowest-cost Silver plan) for the household's rating area
    """
    fpl = get_fpl(household_size)
    fpl_pct = (income / fpl) * 100

    applicable_pct = get_applicable_percentage(fpl_pct)

    if applicable_pct is None:
        if fpl_pct < 100:
            status = "likely Medicaid-eligible (NC expanded Medicaid); not PTC-eligible"
        else:
            status = "above 400% FPL — subsidy cliff applies, $0 PTC under 2026 rules"
        return {
            "fpl_percentage": round(fpl_pct, 1),
            "applicable_percentage": None,
            "required_contribution": None,
            "annual_ptc": 0,
            "monthly_ptc": 0,
            "status": status,
        }

    required_contribution = income * applicable_pct
    annual_ptc = max(0, slcsp_annual_premium - required_contribution)
    annual_ptc = min(annual_ptc, slcsp_annual_premium)

    return {
        "fpl_percentage": round(fpl_pct, 1),
        "applicable_percentage": round(applicable_pct * 100, 2),
        "required_contribution": round(required_contribution, 2),
        "annual_ptc": round(annual_ptc, 2),
        "monthly_ptc": round(annual_ptc / 12, 2),
        "status": "eligible",
    }


def get_slcsp_monthly(df, rating_area, age):
    """
    Returns the second-lowest-cost Silver plan's MONTHLY premium
    for a given rating area and age band, using the merged NC dataset.
    Returns None if fewer than 2 Silver plans are available (can't determine
    a second-lowest in that case).
    """
    silver = df[
        (df["RatingAreaId"] == rating_area)
        & (df["Age"] == age)
        & (df["MetalLevel"] == "Silver")
    ]

    rates = silver["IndividualRate"].sort_values().values

    if len(rates) < 2:
        return None

    return float(rates[1])  # second-lowest


if __name__ == "__main__":
    # Test 1: fixed benchmark premium, isolates the subsidy math from the data lookup
    print("Test 1: subsidy math with fixed benchmark premiums \n")
    test_cases = [
        {"income": 20000, "household_size": 1, "slcsp_annual_premium": 6000},
        {"income": 35000, "household_size": 1, "slcsp_annual_premium": 6000},
        {"income": 50000, "household_size": 1, "slcsp_annual_premium": 6000},
        {"income": 65000, "household_size": 1, "slcsp_annual_premium": 6000},  # near/above cliff
        {"income": 12000, "household_size": 1, "slcsp_annual_premium": 6000},  # below 100% FPL
        {"income": 85000, "household_size": 4, "slcsp_annual_premium": 18000},
    ]

    for case in test_cases:
        result = calculate_subsidy(**case)
        print(case)
        print(result)
        print()

    # Test 2: end-to-end using the real NC dataset for the benchmark premium
    print("\nTest 2: end-to-end using real SLCSP from clean-insurance-NC.csv \n")
    df = pd.read_csv("clean-insurance-NC.csv")

    end_to_end_cases = [
        {"income": 20000, "household_size": 1, "rating_area": "Rating Area 1", "age": "30"},
        {"income": 50000, "household_size": 1, "rating_area": "Rating Area 1", "age": "30"},
        {"income": 65000, "household_size": 1, "rating_area": "Rating Area 1", "age": "30"},
        {"income": 45000, "household_size": 2, "rating_area": "Rating Area 7", "age": "45"},
    ]

    for case in end_to_end_cases:
        monthly_slcsp = get_slcsp_monthly(df, case["rating_area"], case["age"])
        if monthly_slcsp is None:
            print(case, "-> no SLCSP found (fewer than 2 Silver plans)")
            continue

        annual_slcsp = monthly_slcsp * 12
        result = calculate_subsidy(
            income=case["income"],
            household_size=case["household_size"],
            slcsp_annual_premium=annual_slcsp,
        )
        print(f"{case}")
        print(f"  SLCSP monthly premium: ${monthly_slcsp:.2f}")
        print(f"  {result}")
        print()