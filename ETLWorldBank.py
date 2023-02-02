import pandas as pd
import wbgapi as wb
import warnings
import itertools
import numpy as np
from tools import compute_score

CODE_CSV_FILE = 'countries_codes.csv'

def load_code_countries(code_csv_file):
	df = pd.read_csv(code_csv_file, sep=';')
	df['Alpha-3 code'] = df['Alpha-3 code'].str.replace('"','')
	df['Alpha-3 code'] = df['Alpha-3 code'].str.strip()
	return df

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
	'EG.USE.COMM.FO.ZS','EN.ATM.CO2E.KT', 'EG.USE.PCAP.KG.OE', 'EG.USE.CRNW.ZS'
	]

# features = ['EN.ATM.METH.KT.CE']
print('starting request')
world_methane_emission = wb.data.DataFrame(FEATURES, CODE_LIST , columns = 'series').reset_index()

print('request done !!!')

print('start change columns.....')
columns_rename_list = [
		DICO_GLOBAL_METHANE, DICO_ENERGY, DICO_ENERGY_RELATED, 
		DICO_AGRICULTURE_METHANE, DICO_AGRICULTURE_RELATED
]

dico_final = {}
for dico in columns_rename_list:
	dico_final.update(dico)

dico_final.update({'time':'year'})

world_methane_emission = world_methane_emission.rename(columns = dico_final)

print('change columns done.....')


print('start format year.....')
world_methane_emission['year'] = world_methane_emission['year'].str[2:]
world_methane_emission['year'] = pd.to_datetime(world_methane_emission['year'] ).dt.year

print('format year done.....')

world_methane_emission['meth_valuebylandaera'] = world_methane_emission['GlobalMethane(ktco2)'] / world_methane_emission['LandArea(count)']

print('start writing to csv.....')
world_methane_emission.to_csv('world_methane_emission.csv')
print(' writing to csv done .....')


print(' start compute score country by year .....')
# Ajout de la colonne first_note pour la notation d'un payes par année (un classement)
world_methane_emission = compute_score(world_methane_emission, 'year', 'meth_valuebylandaera')
print(' end compute score country by year .....')

print(' start feature selection .....')

#selection des features en fonctions des resultats de la correlation avec les valeurs d emission du methane
predictors = ['GlobalMethane(ktco2)', 'LandArea(count)', 'CO2Emission(kt)', 'AgricultureMethane(ktco2)','EnergieMethane(ktco2)', 'AirTransport', 'note_year']
# predictors = ['GlobalMethane(ktco2)', 'CO2Emission(kt)', 'AgricultureMethane(ktco2)','EnergieMethane(ktco2)', 'AirTransport', 'note_year']
feature_selected = ['economy', 'year'] + predictors

world_methane_emission = world_methane_emission[feature_selected]

print(' end feature selection .....')

print('start final writing to csv.....')
world_methane_emission.to_csv('world_methane_emission_with_notebyyear.csv')
print('end final writing to csv.....')

print('done ETL.....')


