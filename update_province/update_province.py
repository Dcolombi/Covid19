import urllib.request
import pandas as pd
import json
import io
from typing import Union

#
# PARAMETERS
#
raw_province_data_url = "https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-province/dpc-covid19-ita-province-latest.csv"
raw_region_data_url   = "https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-regioni/dpc-covid19-ita-regioni-latest.csv"
province_population_filename   = "./data/Italian_population_data_by_provinces.csv"
region_population_filename     = "./data/Italian_population_data_by_regions.csv"
output_filename = "province_updated.json"

#
# FUNCTIONS
#
def get_population_data(path:str) -> dict:
    rename_dict = {"Territorio": "name", "Value": "population"}
    return pd.read_csv(path) \
      .rename(columns=rename_dict)\
      .set_index("name")\
      .population.to_dict()


def get_data_from_github(url:str) -> Union[pd.DataFrame, str]:
    try:
        with urllib.request.urlopen(url) as response:
            data_df: pd.DataFrame = pd.read_csv(response)
    except ValueError:
        return "bad_url"
    return data_df


def manage_problem(x):
    pass


def manage_undefined_old(datadf:pd.DataFrame) -> pd.DataFrame:
    undefined_name = "In fase di definizione/aggiornamento"
    corrected_names = lambda row: row["region"] + " - to be updated"\
                         if row["name"] == undefined_name else row["name"]

    return datadf.assign(
        name=lambda df: df.apply(corrected_names, axis=1)
    )

def manage_undefined(datadf:pd.DataFrame) -> pd.DataFrame:
    undefined_name = "In fase di definizione/aggiornamento"
    return datadf.loc[datadf["name"] != undefined_name].reset_index(drop=True)


def prepare_data(datadf:pd.DataFrame) -> list:
    rename_dict = {
        "denominazione_provincia": "name",
        "denominazione_regione"  : "region",
        "totale_casi"            : "cases",
    }
    tmpdf = datadf.rename(columns=rename_dict)\
                  .pipe(manage_undefined)
    json_data = tmpdf[["name","cases"]].to_json(orient="records")
    return json_data


def prepare_province_data(datadf:pd.DataFrame) -> pd.DataFrame:
    rename_dict = {
        "denominazione_provincia": "name",
        "denominazione_regione"  : "region",
        "totale_casi"            : "tot_cases",
    }
    tmpdf = datadf.rename(columns=rename_dict) \
                  .pipe(manage_undefined)
    return tmpdf[["name","tot_cases","region"]]


def prepare_region_data(datadf:pd.DataFrame) -> pd.DataFrame:
    rename_dict = {
        "denominazione_regione" : "name",
        "totale_casi"           : "tot_cases",
        "totale_positivi"       : "infected",
    }
    tmpdf = datadf.rename(columns=rename_dict)
    return tmpdf[["name","tot_cases","infected"]]


def pseudoinfected_for_provinces(provincedf:pd.DataFrame, regiondf:pd.DataFrame = None):
    """
    P_i[t] =  R_i[t] / (R_tot[t]/R_pop) * (P_tot[t]/P_pop)
           =  R_i[t] * R_pop / R_tot[t] * (P_tot[t]/P_pop)
    """
    provincedf["correction_addendum"] = provincedf["tot_cases"] / provincedf["population"]
    R_tot_dv_R_pop = provincedf.groupby("region").correction_addendum.sum()
    regiondf["correction"] = regiondf["infected"] / R_tot_dv_R_pop.values
    #regiondf["correction"] = regiondf["infected"] * regiondf["population"]/regiondf["tot_cases"]
    regiondf.loc[lambda df: df["tot_cases"]==0., "correction"] = 0.
    regional_correction = regiondf.set_index("name")["correction"].to_dict()
    provincedf["pseudo_infected"] = (provincedf["region"].map(regional_correction) * provincedf["tot_cases"] / provincedf["population"] )
    provincedf.loc[lambda df: df["tot_cases"]==0.,"pseudo_infected"] = 0.
    provincedf = provincedf.assign(pseudo_infected=lambda df: df.pseudo_infected.fillna(0))\
                           .assign(pseudo_infected=lambda df: df.pseudo_infected.round(0).astype(int))
    return provincedf


def parse_and_dump_json(data:list, file:io.TextIOWrapper) -> None:
    json.dump(json.loads(data), file, indent="\t", ensure_ascii=False)


def add_population_info(df:pd.DataFrame, population:dict={}) -> pd.DataFrame:
    return df.assign(population=lambda df: df.name.map(lambda name: population.get(name, 0)))


def write_to_disk(df:pd.DataFrame, filename:Union[str,None]) -> None:
    rename_dict = {"pseudo_infected":"cases"}
    tmpdf = df[["name","pseudo_infected"]].rename(columns=rename_dict)
    with open(filename, mode="w", encoding="utf-8") as file:
        parse_and_dump_json(tmpdf.to_json(orient="records"), file)


#
# MAIN
#

def main() -> int:
    region_population   = get_population_data(region_population_filename)
    province_population = get_population_data(province_population_filename)

    data_region_df   = get_data_from_github(raw_region_data_url)\
                      .pipe(prepare_region_data)\
                      .pipe(add_population_info, population=region_population)

    data_province_df = get_data_from_github(raw_province_data_url)\
                      .pipe(prepare_province_data) \
                      .pipe(add_population_info, population=province_population)\
                      .pipe(pseudoinfected_for_provinces, regiondf=data_region_df)\
                      .pipe(write_to_disk, filename=output_filename)


if __name__ == "__main__":
    main()