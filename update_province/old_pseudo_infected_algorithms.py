def pseudoinfected_for_provinces_secondway(provincedf:pd.DataFrame, regiondf:pd.DataFrame = None):
    """
    P_i[t] =  R_i[t] / (Sum_i (P_i_tot[t]/P_i_pop)) * (P_tot[t]/P_pop)
    """
    provincedf["correction_addendum"] = provincedf["tot_cases"] / provincedf["population"]
    R_tot_dv_R_pop = provincedf.groupby("region").correction_addendum.sum()
    regiondf["correction"] = regiondf["infected"] / R_tot_dv_R_pop.values
    regiondf.loc[lambda df: df["tot_cases"]==0., "correction"] = 0.
    regional_correction = regiondf.set_index("name")["correction"].to_dict()
    provincedf["pseudo_infected"] = (provincedf["region"].map(regional_correction) * provincedf["tot_cases"] / provincedf["population"] )
    provincedf.loc[lambda df: df["tot_cases"]==0.,"pseudo_infected"] = 0.
    provincedf = provincedf.assign(pseudo_infected=lambda df: df.pseudo_infected.fillna(0)) \
        .assign(pseudo_infected=lambda df: df.pseudo_infected.round(0).astype(int))
    return provincedf


def pseudoinfected_for_provinces_firstway(provincedf:pd.DataFrame, regiondf:pd.DataFrame = None):
    """
    P_i[t] =  R_i[t] / (R_tot[t]/R_pop) * (P_tot[t]/P_pop)
           =  R_i[t] * R_pop / R_tot[t] * (P_tot[t]/P_pop)
    """
    regiondf["correction"] = regiondf["infected"] * regiondf["population"]/regiondf["tot_cases"]
    regiondf.loc[lambda df: df["tot_cases"]==0., "correction"] = 0.
    regional_correction = regiondf.set_index("name")["correction"].to_dict()
    provincedf["pseudo_infected"] = (provincedf["region"].map(regional_correction) * provincedf["tot_cases"] / provincedf["population"] )
    provincedf.loc[lambda df: df["tot_cases"]==0.,"pseudo_infected"] = 0.
    provincedf = provincedf.assign(pseudo_infected=lambda df: df.pseudo_infected.fillna(0)) \
        .assign(pseudo_infected=lambda df: df.pseudo_infected.round(0).astype(int))
    return provincedf


