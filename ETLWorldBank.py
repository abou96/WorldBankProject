import pandas as pd
import wbgapi as wb
import warnings
import itertools
import numpy as np
from tools import compute_score
import logging as _log

_log.basicConfig(filename='ETL_WorldBank.log', level=_log.INFO, 
					format='%(asctime)s - %(message)s', datefmt ='%d-%m-%y %H:%M:%S')



CODE_CSV_FILE = 'data/countries_codes.csv'

def load_code_countries(code_csv_file):
	df = pd.read_csv(code_csv_file, sep=';')
	df['Alpha-3 code'] = df['Alpha-3 code'].str.replace('"','')
	df['Alpha-3 code'] = df['Alpha-3 code'].str.strip()
	return df

def column_as_float(df, col):
	df[col]= df[col].astype(float)
	return df[col]

_log.info('load country code.....')
df_code = load_code_countries(CODE_CSV_FILE)

CODE_LIST = list(df_code['Alpha-3 code'].unique())

DICO_GLOBAL_METHANE = {
	'EN.ATM.METH.ZG':'GlobalMethane(pct_change)', 
	'EN.ATM.METH.KT.CE':'GlobalMethane(ktco2)'
	}

DICO_ENERGY = {
	'EN.ATM.METH.EG.ZS':'EnergieMethane', 
	'EN.ATM.METH.EG.KT.CE':'EnergieMethane(ktco2)', 

}

DICO_ENERGY_RELATED = {

	'IS.AIR.DPRT':'AirTransport', 'EG.USE.ELEC.KH.PC': 'ConsoElec', 
	'EG.ELC.NGAS.ZS':'EnergieNatualGaz(%total)',
	'EG.FEC.RNEW.ZS':'RenewableConso(%totalconso)', 
	'EG.USE.COMM.FO.ZS':'FossilfuelConso(%totalconso)',
	'EN.ATM.CO2E.KT': 'CO2Emission(kt)', 
	'EG.USE.PCAP.KG.OE':'PrimaryEnergy(kgoil)', 
	'EG.USE.CRNW.ZS':'PrimaryEnergy(%total)'

	}

DICO_AGRICULTURE_METHANE = {

	'EN.ATM.METH.AG.KT.CE':'AgricultureMethane(ktco2)', 
	'EN.ATM.METH.AG.ZS':'AgricultureMethane(٪total)'
}

DICO_AGRICULTURE_RELATED = {'AG.LND.TOTL.K2':'LandArea(count)' }

FEATURES = [
	'EN.ATM.METH.EG.ZS','EN.ATM.METH.ZG', 'EN.ATM.METH.AG.KT.CE', 'IS.AIR.DPRT', 
	'EG.USE.ELEC.KH.PC', 'AG.LND.TOTL.K2',
	'EN.ATM.METH.AG.ZS','EN.ATM.METH.EG.KT.CE','EN.ATM.METH.EG.ZS', 
	'EN.ATM.METH.KT.CE', 'EN.ATM.METH.ZG', 'EG.ELC.NGAS.ZS', 'EG.FEC.RNEW.ZS', 
	'EG.USE.COMM.FO.ZS','EN.ATM.CO2E.KT', 'EG.USE.PCAP.KG.OE', 'EG.USE.CRNW.ZS', 'NY.GDP.MKTP.CD',
	'SP.POP.TOTL', 'EN.POP.DNST']

# features = ['EN.ATM.METH.KT.CE']
_log.info('starting request....')
world_methane_emission = wb.data.DataFrame(FEATURES, CODE_LIST , columns = 'series').reset_index()


_log.info('request done !!!')

_log.info('start change columns.....')

columns_rename_list = [
		DICO_GLOBAL_METHANE, DICO_ENERGY, DICO_ENERGY_RELATED, 
		DICO_AGRICULTURE_METHANE, DICO_AGRICULTURE_RELATED
]

dico_final = {}
for dico in columns_rename_list:
	dico_final.update(dico)

dico_final.update({'time':'year'})
dico_final.update({'NY.GDP.MKTP.CD':'GDP($)'})
dico_final.update({'SP.POP.TOTL':'Population'})
dico_final.update({'EN.POP.DNST':'Population density'})

world_methane_emission = world_methane_emission.rename(columns = dico_final)

_log.info('change columns done.....')

_log.info('start format year.....')

world_methane_emission['year'] = world_methane_emission['year'].str[2:]
world_methane_emission['year'] = pd.to_datetime(world_methane_emission['year']).dt.year

_log.info('format year done.....')

for col in ['GlobalMethane(ktco2)', 'LandArea(count)', 'GDP($)', 'Population', 'Population density' ] :
	world_methane_emission[col] = column_as_float(world_methane_emission, col)

world_methane_emission['meth_valuebylandaera'] = world_methane_emission['GlobalMethane(ktco2)'] / world_methane_emission['LandArea(count)']
world_methane_emission['Emissions intensity'] = world_methane_emission['GlobalMethane(ktco2)'] / world_methane_emission['GDP($)']
world_methane_emission['Per capita emissions'] = world_methane_emission['GlobalMethane(ktco2)'] / world_methane_emission['Population']
world_methane_emission['Per capita density emissions'] = world_methane_emission['GlobalMethane(ktco2)'] / world_methane_emission['Population density']

_log.info('start writing to excel.....')

world_methane_emission.to_excel('data/world_methane_emission.xlsx')

_log.info('writing to excel done .....')

_log.info('start compute score country by year .....')

# Ajout des colonnes note_year_{cols} pour la notation d'un payes par année (un classement)
score_list = []
for col in ['GlobalMethane(ktco2)', 'meth_valuebylandaera', 'Emissions intensity', 'Per capita emissions', 'Per capita density emissions']:
	world_methane_emission, note_col = compute_score(world_methane_emission, 'year', col)
	score_list.append(note_col)

_log.info(' end compute score country by year .....')

_log.info(' start feature selection .....')

#selection des features en fonctions des resultats de la correlation avec les valeurs d emission du methane
columns = ['economy', 'year', 'GlobalMethane(ktco2)', 'LandArea(count)', 'CO2Emission(kt)', 
'AgricultureMethane(ktco2)','EnergieMethane(ktco2)', 'AirTransport',  'meth_valuebylandaera', 'Emissions intensity',
 'Per capita emissions', 'Per capita density emissions'] + score_list


world_methane_emission = world_methane_emission[columns]

_log.info(' end feature selection .....')

_log.info('start final writing to excel.....')
world_methane_emission.to_excel('data/world_methane_emission_with_notebyyear.xlsx')
_log.info('end final writing to excel.....')

_log.info('done ETL.....')


