import urllib.request
import pandas as pd
import json
import io
from typing import Union


def get_data_from_github(url:str) -> Union[pd.DataFrame, str]:
    try:
        with urllib.request.urlopen(url) as response:
            data_df: pd.DataFrame = pd.read_csv(response)
    except ValueError:
        return "bad_url"
    return data_df


def manage_problem(x):
    pass


def manage_undefined(datadf:pd.DataFrame) -> pd.DataFrame:
    undefined_name = "In fase di definizione/aggiornamento"
    corrected_names = lambda row: row["region"] + " - to be updated"\
                         if row["name"] == undefined_name else row["name"]

    return datadf.assign(
        name=lambda df: df.apply(corrected_names, axis=1)
    )

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


def parse_and_dump_json(data:list, file:io.TextIOWrapper) -> None:
    json.dump(json.loads(data), file, indent="\t", ensure_ascii=False)


def main() -> int:
    raw_data_url = "https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-province/dpc-covid19-ita-province-latest.csv"
    filename = "province_updated.json"
    datadf = get_data_from_github(raw_data_url)

    if type(datadf)==str:
        manage_problem(datadf)
        return 1
    else:
        prepared_data = prepare_data(datadf)
        with open(filename, mode="w", encoding="utf-8") as file:
            parse_and_dump_json(prepared_data, file)
        return 0

if __name__ == "__main__":
    main()