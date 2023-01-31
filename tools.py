import pandas as pd
import numpy as np
import random

BEGIN_YEAR_AVAILABLE = 1990
CURRENT_YEAR_AVAILABLE = 2019

def HandlingFormatDateIndex(df, year) :
	'''
	This code is handling the formatting of a dataframe's date index. 
	it creates a date range between the start year specified by the constant BEGIN_YEAR_AVAILABLE and the input year, 
	which will be used to reindex the dataframe.
	The index is then converted to year format and any 0 values are replaced with NaN.
	'''
	df['year'] = pd.to_datetime(df['year'])
	df = df.set_index('year')
	start = str(BEGIN_YEAR_AVAILABLE) + "-01-01"
	end = str(year) + "-01-01"
	dates = pd.date_range(start=start, end=end)
	df= df.reindex(dates, fill_value=0)
	df = df.resample('Y').sum().reset_index()
	df['index'] = df['index'].dt.year
	df= df.rename(columns={'index':'year'})
	df.replace(0.0, pd.np.nan, inplace=True)
	return df

def compute_score(df, group, col = 'GlobalMethane(ktco2)'):
	'''
	This code computes a score for a column in a dataframe based on a grouping column. 
	It first groups the dataframe by the group column and computes the maximum and minimum values
	of the column col (default value is 'GlobalMethane(ktco2)'). 
	The computed maximum and minimum values are then merged back into the original dataframe.
	The score is then calculated by using a min-max scaler method and scaling the values between 0 and 4. 
	The score is stored in a new column, 'note_group', where 'group' is the input group column. 
	Finally, the intermediate columns 'max_meth' and 'min_meth' are dropped and the modified dataframe is returned.
	'''
	#compute max value methan emission by group
	dfgrouped = pd.DataFrame(df.groupby(group)[col].max()).reset_index()
	dfgrouped = dfgrouped.rename(columns={col: 'max_meth'})
	df = df.merge(dfgrouped, on=[group], how='left')
	#compute min value methan emission by group
	dfgrouped = pd.DataFrame(df.groupby(group)[col].min()).reset_index()
	dfgrouped = dfgrouped.rename(columns={col: 'min_meth'})
	df = df.merge(dfgrouped, on=[group], how='left')
	# scale the score between 0 to 4 by using min=max scaler method
	df[f'note_{group}']= np.where(df[col].notnull(), 
	                          4*(df[col] - df['min_meth'])/
	                          (df['max_meth'] - df['min_meth']), -1)
	del df['max_meth']
	del df['min_meth']
	return df

def replace_random_values(df, fraction):
	
	'''
	This code replaces a specified fraction of the values in a dataframe
	with NaN values. It will help to compute the uncertainty.
	'''
	for column in df.columns:

	    df_train = df.copy()
	    print(np.random.rand(len(df_train)))
	    mask = np.random.rand(len(df_train)) < fraction
	    if mask[0] == True:
	        mask[0] = False
	    df_train[column][mask] = np.nan
	return df_train

    