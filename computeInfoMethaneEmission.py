import wbgapi as wb
import pandas as pd
import warnings
import itertools
import numpy as np
warnings.filterwarnings("ignore")
from datetime import datetime
from dataclasses import dataclass
from ComputeScoreKmeans import kmeans_score 
import pycountry_convert as pc
from tools import HandlingFormatDateIndex
from HandlingMissingvalues import rolling_statistical, compute_uncertainty
import logging as _log

_log.basicConfig(filename='worldbank_info.log', level=_log.DEBUG, 
					format='%(asctime)s - %(message)s', datefmt ='%d-%m-%y %H:%M:%S')


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

		_log.info('loading data of methane emission')
		df_all_country = pd.read_excel('data_csv/world_methane_emission_with_notebyyear.xlsx', index_col=False)
		
		df_country = df_all_country[df_all_country['economy'] == CountryAlpha3Code]
		
		df_country['year'] = df_country['year'].apply(str)

		df_country = HandlingFormatDateIndex(df_country, year)

		df_country = df_country[['year', 'GlobalMethane(ktco2)']]

		isMissing = is_missing(df_country, year)

		if not isMissing :
			_log.info('the value is available')
			dico['EmissionMethaneValue'] = df_country.loc[df_country['year'] == year, 'GlobalMethane(ktco2)'].values[0]
			dico['Uncertainty'] = None
		
		else :
			_log.info('the value is missing. starting estimation...')
			dico['is_estimated'] = True
			df_country = df_country.set_index('year')
			df_country = rolling_statistical(df_country, 5, 'SMA')
			df_country = df_country.reset_index()
			dico['EmissionMethaneValue'] = df_country.loc[df_country['year'] == year, 'GlobalMethane(ktco2)'].values[0]
			dico['Uncertainty'] = compute_uncertainty(df_country, 'rolling_statistical', 5, kind_rolling= 'SMA', kind_interpo= 'linear', 
										order = 1, windows_size = 4, k=3)

		#all scores using each methods
		columns = ['meth_valuebylandaera', 'Emissions intensity', 'Per capita emissions', 'Per capita density emissions']
		scores_col_list= [f'note_year_{col}' for col in columns]

		_log.info('starting compute score using clustering')
		print(columns[0])
		df_score = kmeans_score(CountryAlpha3Code, year, df_all_country, columns[1])
		#note by year using meth_valuebylandaera chosen
		dico['score_annuel'] = df_score.loc[df_score['economy']== CountryAlpha3Code, scores_col_list[1]].values[0]
		dico['score_cluster'] = df_score.loc[df_score['economy']== CountryAlpha3Code, 'score_cluster'].values[0]
		
		return dico

    
if __name__ == '__main__':
	country = CountryEmission()
	print(country.getMethaneInfo('CN', 2018))   


