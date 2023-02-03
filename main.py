from fastapi import FastAPI, Query
from computeInfoMethaneEmission import CountryEmission

app = FastAPI()

country_methane = CountryEmission()

@app.get("/{iso_alpha2}/{year}")
async def emissions(
    iso_alpha2: str,
    year: int = Query(None, gt=2013, lt=2028)
):
    # retrieve methane emissions data for the given country and year
    data = country_methane.getMethaneInfo(iso_alpha2, year)
    return {
        "methane_emissions": data['EmissionMethaneValue'],
        "is_estimated": data['is_estimated'],
        "iso_alpha2": data['iso_alpha2'],
        "country_name": data['country_name'],
        "uncertainty": data['Uncertainty'],
        "score_annuel": data['score_annuel'],
        "score_interne": data['score_cluster']

    }
