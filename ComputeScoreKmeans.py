import wbgapi as wb
import pandas as pd
import warnings
import itertools
import numpy as np
warnings.filterwarnings("ignore")
from datetime import datetime
from dataclasses import dataclass
from sklearn.cluster import KMeans
from tools import compute_score

QUERY_ID = ['EN.ATM.METH.EG.KT.CE']

#all scores using each methods
columns = ['meth_valuebylandaera', 'Emissions intensity', 'Per capita emissions', 'Per capita density emissions']
scores_col_list= [f'note_year_{col}' for col in columns]

PREDICTORS = ['GlobalMethane(ktco2)', 'LandArea(count)', 'CO2Emission(kt)',
 			  'AgricultureMethane(ktco2)','EnergieMethane(ktco2)', 
 			  'AirTransport'
 			] + scores_col_list
CURRENT_YEAR_AVAILABLE = 2019


def kmeans_score(CountryAlphaCode, year, df, feature_score):
	 
	if type(year) != int :
		raise Exception('the year should be numerical value')

	df = df[df['year'] == min(float(year), CURRENT_YEAR_AVAILABLE)]
	df = df.dropna(subset=df.columns)
	df = df.reset_index()
	data = df[PREDICTORS].copy()

	#normalization
	data = ((data - data.min()) / (data.max() - data.min())) * 3 + 1
	kmeans = KMeans(4)
	kmeans.fit(data)
	labels = kmeans.labels_
	labels = pd.DataFrame(labels, columns = ['labels'])
	df = df.merge(labels, left_index=True, right_index=True)
	df, _ = compute_score(df, 'labels', feature_score)

	return df















