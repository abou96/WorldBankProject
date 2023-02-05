import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error
from tools import replace_random_values
from sklearn.impute import KNNImputer
import random


def rolling_statistical(df, window_size, kind):

	'''
	This code computes a statistical measure of a dataframe and 
	imputes the NaN values using the computed values. 
	It takes as input the dataframe df, a window_size for the statistical
	measure, and a kind to specify the type of statistical measure to use.
	The available statistical measures are:
		'SMA' : Simple Moving Average
		'WMA' : Weighted Moving Average
		'EMA' : Exponential Moving Average

	'''

	weights = np.linspace(1, window_size, window_size)*0.1

	df_imputed = df.copy()

	for column in df.columns:
	    if kind == 'SMA':
	        function = df_imputed[column] \
	                            .rolling(window_size, min_periods=1) \
	                            .mean().interpolate() 
	        
	        df_imputed[column].fillna(function, inplace=True)
	        
	    elif kind == 'WMA' :
	        function = df_imputed[column].rolling(window_size).apply(
	            lambda x: np.sum(weights*x)).interpolate()
	        
	        df_imputed[column].fillna(function, inplace=True)
	        

	    elif kind == 'EMA' :
	        df_imputed[column] = df_imputed[column].fillna(df_imputed[column].ewm(span=window_size).mean())
	          
	return df_imputed



def imputwithKNNImputer(df, column, k):

	'''
	This function imputes missing values in a dataframe using 
	KNNImputer method. 
	'''
	imputer = KNNImputer(n_neighbors= k)
	imputed_data = imputer.fit_transform(df)
	df_imputed = pd.DataFrame(imputed_data, 
	                       columns = df.columns)
	df_imputed.index = df.index
	df_imputed[column].plot(figsize=(15, 6), title= 'KNNImputer', colormap='jet')

	  
	return df_imputed


def Imputewithlinear_interpolation(df, order, kind='linear'):
	'''
	This function uses the pandas interpolate method to fill missing values 
	in a DataFrame df. The method of interpolation used is specified by 
	the kind argument, which can take values such as 'linear', 'polynomial', etc. 
	'''
	for column in df.columns :
	    df[column ] = df[column].interpolate(method=kind, order=order)
	return df



def compute_uncertainty(df, model, nbr_sim, kind_rolling= 'SMA', kind_interpo= 'linear', order = 1, windows_size = 4, k=3):
	'''
	The compute_uncertainty function calculates the uncertainty of a given
	imputation model. It does this by randomly generating missing values 
	in a dataset, imputing the missing values using the specified model, 
	and then comparing the imputed values to the original values. 
	It repeats this process nbr_sim times and calculates the mean and 
	standard deviation of the root mean squared errors (RMSEs). 
	Finally, it returns the standard deviation as a measure of uncertainty.
	'''

	df = df.dropna()
	for column in df.columns :
	    all_estimations_error = []
	    for _ in range(1, nbr_sim + 1) :
	        df_random_null_value = replace_random_values(df, 0.5)
	        if model == 'rolling_statistical' :
	            df_predict = rolling_statistical(df_random_null_value, windows_size, kind_rolling)
	        elif model == 'KNNImputer' :
	            df_predict = imputwithKNNImputer(df_random_null_value , k)
	            
	    
	        elif model == 'Linear_interpolation':
	                df_predict = Imputewithlinear_interpolation(df_random_null_value, order, kind_interpo)
	                
	            
	        mse = np.sqrt(mean_squared_error(df[column], df_predict[column]))
	        all_estimations_error.append(mse)

	# compute the mean, standard deviation and confidence interval of the results
	mean = np.mean(all_estimations_error)
	std = np.std(all_estimations_error)
	confidence_interval = (mean - 1.96*std, mean + 1.96*std)

	print('Mean: ', mean)
	print('Standard deviation: ', std)
	print('Confidence interval: ', confidence_interval)

	return std