import unittest
import update_province as UP
import pandas as pd

class ProvinceUpdated(unittest.TestCase):
    def test_download_bad_url(self):
        """ValueError"""
        data = UP.get_data_from_github("sasda")
        self.assertEqual("bad_url", data)
    def test_download_wrong_url(self):
        """UnicodeDecodeError"""
        data = UP.get_data_from_github("https://google.com")
        self.assertEqual("bad_url", data)

    def test_pseudoinfected(self):
        """Comparing pre-computed data with the actual implementation"""
        folder = "./data/test/"
        region_name = "neverland"
        province_df = pd.read_csv(folder + "province_df.csv")\
                        .assign(region=region_name)\
                        .rename(columns={"Unnamed: 0": "time"})\
                        .set_index("time")\
                        .fillna(0)
        region_df   = pd.read_csv(folder + "reg_df.csv")\
                        .assign(name=region_name)\
                        .rename(columns={"Unnamed: 0": "time"}) \
                        .set_index("time")
        for t in region_df.index:
            prov_tmp_df = province_df.loc[t].copy()
            reg_tmp_df  = region_df.loc[[t]].copy()
            original_df = province_df.loc[t].sort_values("name")["pseudo_infected"].round(0).astype(int)

            resultdf = UP.pseudoinfected_for_provinces(prov_tmp_df, reg_tmp_df)
            new_df = resultdf.sort_values("name")["pseudo_infected"]
            check = original_df.equals(new_df)
            self.assertEqual(True, check)
