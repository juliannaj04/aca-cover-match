"""
Maps a NC ZIP code to its CMS Geographic Rating Area via county.

Chain: ZIP -> County (from SimpleMaps free zip database) -> Rating Area
(from CMS's official NC Geographic Rating Area table).

Source for county rating area mapping:
https://www.cms.gov/cciio/programs-and-initiatives/health-insurance-market-reforms/nc-gra
"""

import pandas as pd

df = pd.read_csv("uszips.csv") 
nc = df[df["state_id"] == "NC"]
nc.to_csv("zip-county-NC.csv", index=False)


COUNTY_TO_RATING_AREA = {
    "Avery": 1, "Buncombe": 1, "Cherokee": 1, "Clay": 1, "Graham": 1,
    "Haywood": 1, "Henderson": 1, "Jackson": 1, "McDowell": 1, "Macon": 1,
    "Madison": 1, "Mitchell": 1, "Polk": 1, "Rutherford": 1, "Swain": 1,
    "Transylvania": 1, "Yancey": 1,

    "Alexander": 2, "Burke": 2, "Caldwell": 2, "Iredell": 2, "Catawba": 2,

    "Alleghany": 3, "Ashe": 3, "Watauga": 3, "Wilkes": 3,

    "Anson": 4, "Cabarrus": 4, "Mecklenburg": 4, "Rowan": 4,
    "Stanly": 4, "Union": 4,

    "Cleveland": 5, "Gaston": 5, "Lincoln": 5,

    "Davidson": 6, "Davie": 6, "Forsyth": 6, "Stokes": 6,
    "Surry": 6, "Yadkin": 6,

    "Guilford": 7, "Randolph": 7, "Rockingham": 7,

    "Montgomery": 8, "Moore": 8,

    "Bladen": 9, "Cumberland": 9, "Harnett": 9, "Hoke": 9,
    "Richmond": 9, "Robeson": 9, "Sampson": 9, "Scotland": 9,

    "Granville": 10, "Vance": 10, "Warren": 10,

    "Alamance": 11, "Caswell": 11, "Chatham": 11, "Durham": 11,
    "Lee": 11, "Orange": 11, "Person": 11,

    "Bertie": 12, "Camden": 12, "Chowan": 12, "Currituck": 12, "Gates": 12,
    "Halifax": 12, "Hertford": 12, "Martin": 12, "Northampton": 12,
    "Pasquotank": 12, "Perquimans": 12,

    "Franklin": 13, "Johnston": 13, "Wake": 13,

    "Edgecombe": 14, "Greene": 14, "Nash": 14, "Pitt": 14,
    "Wilson": 14, "Wayne": 14,

    "Brunswick": 15, "Columbus": 15, "Duplin": 15, "New Hanover": 15,
    "Onslow": 15, "Pender": 15,

    "Beaufort": 16, "Carteret": 16, "Craven": 16, "Dare": 16, "Hyde": 16,
    "Jones": 16, "Pamlico": 16, "Tyrrell": 16, "Washington": 16, "Lenoir": 16,
}


def get_rating_area_from_county(county_name):
    """
    county_name: e.g. "Wake", "New Hanover" 
    case-sensitive match against the dict above & adjust casing if ZIP source formats
    it differently, e.g. strip "County" suffix before calling this
    """
    area_num = COUNTY_TO_RATING_AREA.get(county_name)
    if area_num is None:
        return None
    return f"Rating Area {area_num}"


def get_rating_area_from_zip(zip_code, zip_county_df):
    """
    zip_code: 5-digit string
    zip_county_df: DataFrame loaded from SimpleMaps zip-county-NC.csv
    """
    zip_code = str(zip_code).strip().zfill(5)

    match = zip_county_df[zip_county_df["zip"].astype(str).str.zfill(5) == zip_code]

    if match.empty:
        return None, None

    county_raw = match.iloc[0]["county_name"]
    county_clean = county_raw.replace(" County", "").strip()

    rating_area = get_rating_area_from_county(county_clean)
    return rating_area, county_clean


if __name__ == "__main__":
    try:
        zip_df = pd.read_csv("zip-county-NC.csv")
        print("Columns in your zip file:", zip_df.columns.tolist())
        print(zip_df.head(3))

        test_zips = ["27601", "28401", "28801", "27514"]
        for z in test_zips:
            area, county = get_rating_area_from_zip(z, zip_df)
            print(f"ZIP {z} -> County: {county}, {area}")

    except FileNotFoundError:
        print("zip-county-NC.csv not found yet.")
        print("Download the free CSV from simplemaps.com/data/us-zips,")
        print("filter to state_id == 'NC', and save it as zip-county-NC.csv")
        print("in this same folder, then re-run this script.")
