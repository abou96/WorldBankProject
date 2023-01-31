import wbgapi as wb
import pandas as pd
import warnings
import itertools
import numpy as np
warnings.filterwarnings("ignore")
from datetime import datetime
from dataclasses import dataclass
from K_Means_model import kmeans_score 
import pycountry_convert as pc
from tools import HandlingFormatDateIndex

from HandlingMissingvalues import rolling_statistical, compute_uncertainty

QUERY_ID = ['EN.ATM.METH.EG.KT.CE']

FEATURES = ['EN.ATM.METH.EG.ZS','EN.ATM.METH.ZG', 
            'EN.ATM.METH.AG.ZS', 'EN.ATM.METH.AG.KT.CE',
           'NY.GDP.PCAP.CD', 'IS.AIR.DPRT', 'EG.USE.ELEC.KH.PC', 'AG.LND.TOTL.K2', 
            'EN.ATM.METH.AG.KT.CE', 'EN.ATM.METH.AG.ZS','EN.ATM.METH.EG.KT.CE', 'EN.ATM.METH.EG.ZS', 
            'EN.ATM.METH.KT.CE', 'EN.ATM.METH.ZG', 'EG.ELC.NGAS.ZS', 'EG.FEC.RNEW.ZS', 'EG.USE.COMM.FO.ZS',
            'EN.ATM.CO2E.KT', 'EG.USE.PCAP.KG.OE', 'EG.USE.CRNW.ZS'
           ]

def is_missing(df, year):
	ismiss = df.loc[df['year'] == year, 'GlobalMethane(ktco2)'].values[0]
	return np.isnan(ismiss)

@dataclass
class CountryEmission : 

    def getMethaneInfo(self, CountryAlpha2Code, year) -> pd.DataFrame :

    	dico = {}
    	map_alpha2_alpha3_dico = pc.map_country_alpha2_to_country_alpha3()
    	try :
    		CountryAlpha3Code = map_alpha2_alpha3_dico[CountryAlpha2Code]
    	except :
    		raise Exception('this is not a country alpha2 code')

    	map_alpha2_countryname = pc.map_country_alpha2_to_country_name()
    	dico['country_name'] = map_alpha2_countryname[CountryAlpha2Code]
    	dico['iso_alpha2'] = CountryAlpha2Code
    	dico['is_estimated'] = False

    	df_all_country = pd.read_csv('World_methane_emission_first_note.csv', index_col=False)

    	df_country = df_all_country[df_all_country['economy'] == CountryAlpha3Code]
    	
    	df_country['year'] = df_country['year'].apply(str)

    	df_country = HandlingFormatDateIndex(df_country, year)

    	df_country = df_country[['year', 'GlobalMethane(ktco2)']]

    	isMissing = is_missing(df_country, year)

    	if not isMissing :
    		dico['EmissionMethaneValue'] = df_country.loc[df_country['year'] == year, 'GlobalMethane(ktco2)'].values[0]
    		dico['Uncertainty'] = None
    	
    	else :

    		dico['is_estimated'] = True
    		df_country = df_country.set_index('year')
    		df_country = rolling_statistical(df_country, 5, 'SMA')
    		df_country = df_country.reset_index()
    		dico['EmissionMethaneValue'] = df_country.loc[df_country['year'] == year, 'GlobalMethane(ktco2)'].values[0]
    		dico['Uncertainty'] = compute_uncertainty(df_country, 'rolling_statistical', 5, kind_rolling= 'SMA', kind_interpo= 'linear', 
    									order = 1, windows_size = 4, k=3)


    	df_score = kmeans_score(CountryAlpha3Code, year, df_all_country)
    	dico['score_annuel'] = df_score.loc[df_score['economy']== CountryAlpha3Code, 'note_year'].values[0]
    	dico['score_cluster'] = df_score.loc[df_score['economy']== CountryAlpha3Code, 'score_cluster'].values[0]

    	return dico

    
if __name__ == '__main__':
	country = CountryEmission()
	print(country.getMethaneValue('CH', 2012))   


