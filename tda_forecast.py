# -*- coding: utf-8 -*-
"""TDA_Forecast.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1QasxsqoRzUukBilh-Evwj12Wic1g3wKO

#<u> Introduction </u>
### To predict the number of units sold in next 12 month based on previous month sales

##<u>Given Data:</u>
### Sale Record of 42 months
"""

import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.holtwinters import SimpleExpSmoothing
from statsmodels.tsa.holtwinters import ExponentialSmoothing

data = pd.read_csv('Forecasting_Case_Study_Data.csv')
data = data.iloc[:42] #taking the first 42 rows in data ( because the others are empty)
from datetime import datetime

# Convert 'Time' to datetime and set it as index
data['Time'] = pd.to_datetime(data['Time'], format='%Y_Month_%m')
data.set_index('Time', inplace=True)

data.to_csv('Forecasting_Date_Time.csv',index=False)

np.median(data['Actuals'])

# Removing 3 outliers - 40k,41k,70k (Experimented)
data2=pd.read_csv('Forecasting_Case_Study_Data_2.csv')
data2 = data2.iloc[:39]
data2.to_csv('Without_Outlier.csv',index=False)
data2['Time'] = pd.to_datetime(data2['Time'], format='%Y_Month_%m')
data2.set_index('Time', inplace=True)

"""# ADF Test for Stationarity

## ADF is Augmented-Dickey Fuller Test, it is a statistical test for checking the stationarity of the data.
"""

#KPSS
from statsmodels.tsa.stattools import kpss


def kpss_test(timeseries):
    print("Results of KPSS Test:")
    kpsstest = kpss(timeseries, regression="c", nlags="auto")
    kpss_output = pd.Series(
        kpsstest[0:3], index=["Test Statistic", "p-value", "Lags Used"]
    )
    for key, value in kpsstest[3].items():
        kpss_output["Critical Value (%s)" % key] = value
    print(kpss_output)

kpss_test(data['Actuals'])

from statsmodels.tsa.stattools import adfuller
def adf_test(timeseries):
    print ('Results of Dickey-Fuller Test:')
    dftest = adfuller(timeseries, autolag='AIC')
    dfoutput = pd.Series(dftest[0:4], index=['Test Statistic','p-value','#Lags Used','Number of Observations Used'])
    for key,value in dftest[4].items():
        dfoutput['Critical Value (%s)'%key] = value
    print (dfoutput)
# Call the function and run the test

adf_test(data['Actuals'])
adf_test(data2['Actuals'])

"""# Conclusion:

## Both tests indicate stationarity.
Case 1: Both tests conclude that the series is not stationary - The series is not stationary

Case 2: Both tests conclude that the series is stationary - The series is stationary

Case 3: KPSS indicates stationarity and ADF indicates non-stationarity - The series is trend stationary. Trend needs to be removed to make series strict stationary. The detrended series is checked for stationarity.

Case 4: KPSS indicates non-stationarity and ADF indicates stationarity - The series is difference stationary. Differencing is to be used to make series stationary. The differenced series is checked for stationarity.

# seasonal_decompose()

Additive:
y(t) = Level + Trend + Seasonality + Noise

Multiplicative:
y(t) = Level * Trend * Seasonality * Noise
"""

#Checking for trends
decompose_result = seasonal_decompose(data['Actuals'], model = 'multiplicative', period=12)
decompose_result.plot()

#Checking for trends
decompose_result = seasonal_decompose(data['Actuals'], model = 'additive', period=12)
decompose_result.plot()

"""# Simple Exponential Smoothing

Smoothing Factor (α): This parameter controls the extent of smoothing applied to the time series data. It is a value between 0 and 1, representing the weight assigned to the most recent observation when calculating the forecast. A smaller α gives more weight to older observations, resulting in less responsiveness to recent changes in the data. Conversely, a larger α gives more weight to recent observations, making the forecast more responsive to changes.

F(t+1)=F(t)+ α(A(t)-F(t))

F(t+1)=next forecast
F(t)=present forecast
A(t)=Actual value

General Guideline:

If the data contains a significant amount of noise or fluctuations, smaller value for α is chosen(e.g., closer to 0.1) to achieve a higher level of smoothing and filter out the noise effectively.

If the data has less noise and a more responsive forecast that closely tracks the recent observations is needed , then a slightly larger value for α (e.g., closer to 0.3) to give more weight to the recent observations while still maintaining some level of smoothing.
"""

data['HWES1'] = SimpleExpSmoothing(data['Actuals'],initialization_method='estimated').fit().fittedvalues

data[['Actuals', 'HWES1']].plot(title = 'Holt Winters Single Exponential Smoothing')

data2['HWES1'] = SimpleExpSmoothing(data2['Actuals'],initialization_method='estimated').fit().fittedvalues

data2[['Actuals', 'HWES1']].plot(title = 'Holt Winters Single Exponential Smoothing')

"""# Double Exponential Smoothing

It is the recursive application of an exponential filter twice, thus being termed "double exponential smoothing".

L(t+1)=L(t)+ α(A(t)-L(t))

B(t)=(1-β)B(t-1)+β(L(t)-L(t-1))
"""

data['HWES2_ADD'] = ExponentialSmoothing(data['Actuals'],initialization_method='estimated' ,trend = 'add').fit().fittedvalues

data['HWES2_MUL'] = ExponentialSmoothing(data['Actuals'], initialization_method='estimated',trend = 'mul').fit().fittedvalues

data[['Actuals', 'HWES2_ADD', 'HWES2_MUL']].plot(title='Holt Winters Double Exponential Smoothing: Additive and Multiplicative Trend')

data2['HWES2_ADD'] = ExponentialSmoothing(data2['Actuals'], trend = 'add').fit().fittedvalues

data2['HWES2_MUL'] = ExponentialSmoothing(data2['Actuals'], trend = 'mul').fit().fittedvalues

data2[['Actuals', 'HWES2_ADD', 'HWES2_MUL']].plot(title='Holt Winters Double Exponential Smoothing: Additive and Multiplicative Trend')

"""# Triple Exponential Smoothing

Triple exponential smoothing extends double exponential smoothing by incorporating a seasonal component in addition to the level and trend components.

St = α × (Xt − Ct−L) + (1 − α) × (St−1 + Bt−1)

Bt = β × (St − St−1) + (1 − β) × Bt−1

Ct = γ × (Xt − St) + (1 − γ) × Ct−L

Ft+m = St + m × Bt + Ct−L+1+((m−1)mod L)
"""

data['HWES3_ADD'] = ExponentialSmoothing(data['Actuals'],initialization_method='estimated', trend = 'add', seasonal = 'add', seasonal_periods=12).fit().fittedvalues

data['HWES3_MUL'] = ExponentialSmoothing(data['Actuals'],initialization_method='estimated', trend = 'mul', seasonal='mul', seasonal_periods=12).fit().fittedvalues

data[['Actuals', 'HWES3_ADD', 'HWES3_MUL']].plot(title = 'Holt Winters Triple Exponential Smoothing: Additive and Multiplicative Seasonality')

data2['HWES3_ADD'] = ExponentialSmoothing(data2['Actuals'], trend = 'add', seasonal = 'add', seasonal_periods=12).fit().fittedvalues

data2['HWES3_MUL'] = ExponentialSmoothing(data2['Actuals'], trend = 'mul', seasonal='mul', seasonal_periods=12).fit().fittedvalues

data2[['Actuals', 'HWES3_ADD', 'HWES3_MUL']].plot(title = 'Holt Winters Triple Exponential Smoothing: Additive and Multiplicative Seasonality')

train_data = data.iloc[:-int(len(data) * 0.2)]
test_data = data.iloc[-int(len(data) * 0.2):]
train_data2 = data2.iloc[:-int(len(data2) * 0.2)]
test_data2 = data2.iloc[-int(len(data2) * 0.2):]
print(test_data.shape)
print(test_data2.shape)

"""# Model Fitting"""

fitted_model = ExponentialSmoothing(train_data['Actuals'], trend='mul', seasonal='mul', seasonal_periods=12).fit()
test_predictions = fitted_model.forecast(len(test_data))

import seaborn as sns

sns.lineplot(data=train_data, x=train_data.index, y='Actuals',label='train')
# train_data['Actuals'].plot(label='TRAIN')
sns.lineplot(data=test_data, x=test_data.index, y='Actuals',label='test')
# test_data['Actuals'].plot(label='TEST')
test_predictions.index = test_data.index
test_predictions = pd.DataFrame(test_predictions, columns=['Actuals'])

sns.lineplot(data=test_predictions, x=test_predictions.index, y='Actuals',label='predictions')
# test_predictions.plot(label='PREDICTION')

# print(test_predictions)

# plt.title('Train, Test and Predicted using Holt Winters')
plt.legend()
plt.show()

test_predictions

fitted_model = ExponentialSmoothing(train_data['Actuals'], trend='add', seasonal='mul', seasonal_periods=12).fit()
test_predictions = fitted_model.forecast(len(test_data))

import seaborn as sns

sns.lineplot(data=train_data, x=train_data.index, y='Actuals',label='train')
# train_data['Actuals'].plot(label='TRAIN')
sns.lineplot(data=test_data, x=test_data.index, y='Actuals',label='test')
# test_data['Actuals'].plot(label='TEST')
test_predictions.index = test_data.index
test_predictions = pd.DataFrame(test_predictions, columns=['Actuals'])

sns.lineplot(data=test_predictions, x=test_predictions.index, y='Actuals',label='predictions')
# test_predictions.plot(label='PREDICTION')

# print(test_predictions)

# plt.title('Train, Test and Predicted using Holt Winters')
plt.legend()
plt.show()

test_predictions

fitted_model2 = ExponentialSmoothing(train_data2['Actuals'], trend='add', seasonal='mul', seasonal_periods=12).fit()
test_predictions2 = fitted_model2.forecast(len(test_data2))

import seaborn as sns

sns.lineplot(data=train_data2, x=train_data2.index, y='Actuals',label='Training Data')
# train_data['Actuals'].plot(label='TRAIN')
sns.lineplot(data=test_data2, x=test_data2.index, y='Actuals',label='Test Data')
# test_data['Actuals'].plot(label='TEST')
test_predictions2.index = test_data2.index
test_predictions2 = pd.DataFrame(test_predictions2, columns=['Actuals'])

sns.lineplot(data=test_predictions2, x=test_predictions2.index, y='Actuals',label='Predicted Data')
plt.legend()
plt.show()

#Performance measure
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_percentage_error
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import mean_squared_log_error
def metrics(test,predictions):
   #mean forecast error
   forecast_errors = [test[i]-predictions[i] for i in range(len(test))]
   bias = sum(forecast_errors) * 1.0/len(test)
   #root mean squared error
   rmse = mean_squared_error(test, predictions,squared=False)
   #mean absolute error
   mae = mean_absolute_error(test, predictions)
   #mean absolute percentage error
   mape= mean_absolute_percentage_error(test, predictions)
   #root mean squared error
   rmsle = mean_squared_log_error(test, predictions,squared=False)
   print('Test Bias: %f' % bias)
   print('Test RMSE: %.3f' % rmse)
   print('Test RMSLE: %.3f' % rmsle)
   print('Test MAE: %f' % mae)
   print('Test mape: %.3f' % mape)

from sklearn.metrics import mean_squared_error

data['Actuals'].plot(label='Data')
data['HWES3_ADD'].plot(label='HWSE3')
plt.legend()

data2['Actuals'].plot(label='Data')
data2['HWES3_ADD'].plot(label='HWSE3')
plt.legend()

metrics(test_data['Actuals'],test_predictions['Actuals'])

metrics(test_data2['Actuals'],test_predictions2['Actuals'])

"""# Forecasting the next 12 Months"""

# Train the model (assuming `data` is your complete dataset)
model = ExponentialSmoothing(data['Actuals'], trend='add', seasonal='mul', seasonal_periods=12).fit()

# Forecast for the next 12 months
forecast = model.forecast(12)




# Plotting
plt.figure(figsize=(10, 6))
data['Actuals'].plot(label='Actuals')
forecast.plot(label='Forecast', color='red')
plt.title('Actuals vs Forecast')
plt.xlabel('Time')
plt.ylabel('Units Sold')
plt.legend()
plt.show()

forecast

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.tsa.holtwinters import ExponentialSmoothing

# Train the model (assuming `data` is your complete dataset)
model2 = ExponentialSmoothing(data2['Actuals'], trend='add', seasonal='mul', seasonal_periods=12).fit()

# Forecast for the next 12 months starting from July 1, 2017
forecast2 = model2.forecast(12)

# Define the start date for the forecast range
start_date = '2017-07-01'

# Create a date range for the forecasted period
date_range = pd.date_range(start=start_date, periods=12, freq='MS')

# Create a DataFrame with the forecasted values and date range
forecast_df = pd.DataFrame({'Date': date_range, 'Forecasted': forecast2})

# Set the 'Date' column as the index
forecast_df.set_index('Date', inplace=True)

# Plotting
plt.figure(figsize=(10, 6))
sns.lineplot(data=data2, x=data2.index, y='Actuals', label='Actuals')
sns.lineplot(data=forecast_df, x=forecast_df.index, y='Forecasted', label='Forecasted')
plt.title('Actuals vs Forecasted')
plt.xlabel('Date')
plt.ylabel('Value')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

forecast2

"""# ARIMA"""

!pip install pmdarima
import pmdarima as pm

df = pd.read_csv('Forecasting_Case_Study_Data.csv')
df = df.iloc[:42]
df.info()

df.plot()

# Convert 'Time' to datetime and set it as index
df['Time'] = pd.to_datetime(df['Time'], format='%Y_Month_%m')
df.set_index('Time', inplace=True)

df_train = df.iloc[:-int(len(df) * 0.2)]
df_test = df.iloc[-int(len(df) * 0.2):]

"""### Manual ARIMA (Manually picking the parameters (p,d,q))

### ACF and PACF Plots
"""

from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

# ACF and PACF plots

acf_original = plot_acf(df_train)

pacf_original = plot_pacf(df_train)

"""case-1. ARIMA(p,d,0) ---> ACF is exponentially decaying or sinusoidal and there is significant lag at p and not beyond in PACF.

case-2. ARIMA(0,d,q) --->PACF is exponentially decaying or sinusoidal and there is significant lag at q and not beyond in ACF.



 Conclusion :  Since both these cases are equally followed, estimate the parameters to be (0, 0, 0)
"""

from statsmodels.tsa.arima.model import ARIMA
model = ARIMA(df_train, order = (0,0,0))

model_fit = model.fit()

print(model_fit.summary())

import matplotlib.pyplot as plt

residuals = model_fit.resid[1:]
fig, ax = plt.subplots(1, 2)
residuals.plot(title='Residuals', ax=ax[0])
residuals.plot(title='Density', kind='kde', ax=ax[1])

plt.show()

residuals.mean()

acf_res = plot_acf(residuals)
pacf_res = plot_pacf(residuals)

forecast_test = model_fit.forecast(len(df_test))

df['forecast_manual'] = [None]*len(df_train) + list(forecast_test)

df.plot()

"""Model Evaluation"""

# manual model

metrics(df_test['Actuals'], forecast_test)

"""Forecast For Next 1 year"""

# forecast for manual model
# Forecast the next 12 months
future_steps = 12
# forecast_values = model_fit.forecast(steps=future_steps)
forecast_values = model_fit.predict(start=len(df), end=len(df) + future_steps - 1, typ='levels')
# Generate a date range for the next 20 months starting after the test set
forecast_index = pd.date_range(start=df_test.index[-1] + pd.DateOffset(months=1), periods=future_steps, freq='MS')

# Create a DataFrame for the forecasted values with the correct index alignment
forecast_df = pd.DataFrame({'ARIMA Forecast': forecast_values}, index=forecast_index)

plt.figure(figsize=(10, 6))
plt.plot(df.index, df['Actuals'], label='Actuals')
plt.plot(forecast_df.index, forecast_df['ARIMA Forecast'], label='Manual ARIMA Forecast', color='red')
plt.title('Manual ARIMA Forecast for Next 12 Months')
plt.legend()
plt.show()

"""### Seasonal ARIMA"""

# with seasonality
sarima = pm.auto_arima(df_train, stepwise=False, seasonal=True, m=12)

sarima

sarima.summary()

forecast_test_sarima_auto = sarima.predict(n_periods = len(df_test))

df['Forecast_sarima_auto'] = [None]*len(df_train) + list(forecast_test_sarima_auto)

df.plot()

"""Evaluate The model

"""

# auto sarima model

print('Error metrics for seasonal arima model : \n')
metrics(df_test['Actuals'],forecast_test_sarima_auto)

"""Forecast For Next 1 year"""

# Forecast the next 12 months
future_steps = 20
forecast_values = sarima.predict(n_periods=future_steps)

# Get the last date in your existing data
last_date = df.index[-1]

# Generate a date range for the next 24 months starting from the last date in your data
forecast_index = pd.date_range(start=last_date , periods=future_steps, freq='MS')

# Create a DataFrame for the forecasted values with the correct index alignment
forecast_df = pd.DataFrame({'SARIMA Forecast': forecast_values}, index=forecast_index)

# Plot the forecast
plt.figure(figsize=(10, 6))
plt.plot(df.index, df['Actuals'], label='Actuals')
plt.plot(forecast_df.index, forecast_df['SARIMA Forecast'], label='SARIMA Forecast', color='red')
plt.title('SARIMA Forecast for Next 12 Months')
plt.legend()
plt.show()

forecast_df[1:13]

"""## Auto ARIMA"""

import pmdarima as pm

auto_arima = pm.auto_arima(df_train, stepwise=False, trace=True, seasonal=False)
auto_arima

auto_arima.summary()

forecast_test_auto = auto_arima.predict(n_periods = len(df_test))

df['Forecast_auto'] = [None]*len(df_train) + list(forecast_test_auto)

df.plot()

"""### Evaluate the Model"""

# auto model

print('Error metrics for auto model : \n')
metrics(df_test['Actuals'],forecast_test_auto)

"""### Forecast for next 1 year"""

#  forecast for auto model
# Forecast the next 12 months
future_steps = 20
forecast_values = auto_arima.predict(n_periods=future_steps)

#pd.DateOffset(months=1)
forecast_index = pd.date_range(start=df.index[-1] , periods=future_steps, freq='MS')

# Create a DataFrame for the forecasted values with the correct index alignment
forecast_df = pd.DataFrame({'ARIMA Forecast': forecast_values}, index=forecast_index)

plt.figure(figsize=(10, 6))
plt.plot(df.index, df['Actuals'], label='Actuals')
plt.plot(forecast_df.index, forecast_df['ARIMA Forecast'], label='Auto ARIMA Forecast', color='red')
plt.title('Auto ARIMA Forecast for Next 12 Months')
plt.legend()
plt.show()







"""#LSTM

## Single-layer LSTM
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense

data = pd.read_csv('Forecasting_Case_Study_Data.csv')
data = data.iloc[:42]
from datetime import datetime

# Convert 'Time' to datetime and set it as index
data['Time'] = pd.to_datetime(data['Time'], format='%Y_Month_%m')
data.set_index('Time', inplace=True)

data.to_csv('Forecasting_Date_Time.csv',index=False)

# Removing 3 outliers - 40k,50k,70k
data2=pd.read_csv('Forecasting_Case_Study_Data_2.csv')
data2 = data2.iloc[:39]
data2.to_csv('Without_Outlier.csv',index=False)
data2['Time'] = pd.to_datetime(data2['Time'], format='%Y_Month_%m')
data2.set_index('Time', inplace=True)

# Normalize the data
scaler = MinMaxScaler()
scaled_data = scaler.fit_transform(data)

scaler2 = MinMaxScaler()
scaled_data2 = scaler2.fit_transform(data2)
# Function to create sequences for LSTM
def create_sequences(data, seq_length):
    X = []
    y = []
    for i in range(len(data)-seq_length):
        X.append(data[i:i+seq_length])
        y.append(data[i+seq_length])
    return np.array(X), np.array(y)

# Define sequence length
sequence_length = 12  # You can adjust this based on your preference

# Create sequences
X, y = create_sequences(scaled_data, sequence_length)

X2, y2 = create_sequences(scaled_data2, sequence_length)

# Split the data into training and testing sets
X_train, X_test = X[:-12], X[-12:]
y_train, y_test = y[:-12], y[-12:]

X_train2, X_test2 = X2[:-12], X2[-12:]
y_train2, y_test2 = y2[:-12], y2[-12:]

# Construct the LSTM model
model = Sequential([
    LSTM(50, activation='relu', input_shape=(X_train.shape[1], X_train.shape[2])),
    Dense(1)
])
model2 = Sequential([
    LSTM(50, activation='relu', input_shape=(X_train2.shape[1], X_train2.shape[2])),
    Dense(1)
])


model.compile(optimizer='adam', loss='mse')
model2.compile(optimizer='adam', loss='mse')

# Train the model
history = model.fit(X_train, y_train, epochs=100, batch_size=12, verbose=1)
history2 = model2.fit(X_train2, y_train2, epochs=100, batch_size=12, verbose=1)

# Forecast future demand
forecast = model.predict(X_test)
forecast2 = model2.predict(X_test2)

forecast = scaler.inverse_transform(forecast)
forecast2 = scaler2.inverse_transform(forecast2)

# Plotting actual vs predicted values
plt.plot(data.index[-12:], data[-12:], label='Actual')
plt.plot(data.index[-12:], forecast, label='Predicted')
plt.xlabel('Time')
plt.ylabel('Units')
plt.title('Actual vs Predicted')
plt.legend()
plt.show()

# Plotting actual vs predicted values for data without outliers
plt.plot(data2.index[-12:], data2[-12:], label='Actual')
plt.plot(data2.index[-12:], forecast2, label='Predicted')
plt.xlabel('Time')
plt.ylabel('Units')
plt.title('Actual vs Predicted')
plt.legend()
plt.show()

forecast_index = pd.date_range(start=data.index[-1] + pd.DateOffset(months=1), periods=len(forecast), freq='M')
forecast_df = pd.DataFrame(forecast, index=forecast_index, columns=['Forecasted'])

# Concatenate the forecast DataFrame with the original data
combined_data = pd.concat([data, forecast_df])

# Plotting actual and predicted values
plt.figure(figsize=(12, 6))
plt.plot(combined_data.index, combined_data['Actuals'], label='Actual')
plt.plot(combined_data.index[-12:], combined_data['Forecasted'][-12:], label='Predicted')
plt.xlabel('Time')
plt.ylabel('Units')
plt.title('Actual vs Predicted next 12 Months')
plt.legend()
plt.show()

forecast_index2 = pd.date_range(start=data2.index[-1] + pd.DateOffset(months=1), periods=len(forecast2), freq='M')
forecast_df2 = pd.DataFrame(forecast2, index=forecast_index2, columns=['Forecasted'])

# Concatenate the forecast DataFrame with the original data
combined_data2 = pd.concat([data2, forecast_df2])

# Plotting actual and predicted values
plt.figure(figsize=(12, 6))
plt.plot(combined_data2.index, combined_data2['Actuals'], label='Actual')
plt.plot(combined_data2.index[-12:], combined_data2['Forecasted'][-12:], label='Predicted')
plt.xlabel('Time')
plt.ylabel('Units')
plt.title('Actual vs Predicted next 12 Months')
plt.legend()
plt.show()

print("Original Dataset")
metrics(data[-12:].values, forecast)
print()
print("Without Outliers")
metrics(data2[-12:].values, forecast2)

"""##Multi-layer LSTM"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.metrics import mean_absolute_error, mean_squared_error

data = pd.read_csv('Forecasting_Case_Study_Data.csv')
data = data.iloc[:42]
from datetime import datetime

# Convert 'Time' to datetime and set it as index
data['Time'] = pd.to_datetime(data['Time'], format='%Y_Month_%m')
data.set_index('Time', inplace=True)

data.to_csv('Forecasting_Date_Time.csv',index=False)

# Removing 3 outliers - 40k,50k,70k
data2=pd.read_csv('Forecasting_Case_Study_Data_2.csv')
data2 = data2.iloc[:39]
data2.to_csv('Without_Outlier.csv',index=False)
data2['Time'] = pd.to_datetime(data2['Time'], format='%Y_Month_%m')
data2.set_index('Time', inplace=True)

# Normalize the data
scaler = MinMaxScaler()
scaled_data = scaler.fit_transform(data)

scaler2 = MinMaxScaler()
scaled_data2 = scaler2.fit_transform(data2)
# Function to create sequences for LSTM
def create_sequences(data, seq_length):
    X = []
    y = []
    for i in range(len(data)-seq_length):
        X.append(data[i:i+seq_length])
        y.append(data[i+seq_length])
    return np.array(X), np.array(y)
# Define sequence length
sequence_length = 12  # You can adjust this based on your preference

# Create sequences
X, y = create_sequences(scaled_data, sequence_length)
X2, y2 = create_sequences(scaled_data2, sequence_length)

# Split the data into training and testing sets
X_train, X_test = X[:-12], X[-12:]
y_train, y_test = y[:-12], y[-12:]

X_train2, X_test2 = X2[:-12], X2[-12:]
y_train2, y_test2 = y2[:-12], y2[-12:]

# Construct the LSTM model
model = Sequential([
    LSTM(128, activation='relu', return_sequences=True, input_shape=(X_train.shape[1], X_train.shape[2])),
    Dropout(0.2),
    LSTM(64, activation='relu', return_sequences=True),
    Dropout(0.2),
    LSTM(32, activation='relu'),
    Dropout(0.2),
    Dense(1)
])

model2 = Sequential([
    LSTM(128, activation='relu', return_sequences=True, input_shape=(X_train2.shape[1], X_train2.shape[2])),
    Dropout(0.2),
    LSTM(64, activation='relu', return_sequences=True),
    Dropout(0.2),
    LSTM(32, activation='relu'),
    Dropout(0.2),
    Dense(1)
])

model.compile(optimizer='adam', loss='mse')
model2.compile(optimizer='adam', loss='mse')

# Train the model
history = model.fit(X_train, y_train, epochs=200, batch_size=12, verbose=1)
history2 = model2.fit(X_train2, y_train2, epochs=200, batch_size=12, verbose=1)

# Forecast future demand
forecast = model.predict(X_test)
forecast2 = model2.predict(X_test2)

# Inverse transform the scaled forecast data
forecast = scaler.inverse_transform(forecast)
forecast2 = scaler2.inverse_transform(forecast2)

# Plotting actual vs predicted values
plt.plot(data.index[-12:], data[-12:], label='Actual')
plt.plot(data.index[-12:], forecast, label='Predicted')
plt.xlabel('Time')
plt.ylabel('Units')
plt.title('Actual vs Predicted')
plt.legend()
plt.show()

# Plotting actual vs predicted values (data without outliers)
plt.plot(data2.index[-12:], data2[-12:], label='Actual')
plt.plot(data2.index[-12:], forecast2, label='Predicted')
plt.xlabel('Time')
plt.ylabel('Units')
plt.title('Actual vs Predicted')
plt.legend()
plt.show()

forecast_index = pd.date_range(start=data.index[-1] + pd.DateOffset(months=1), periods=len(forecast), freq='M')
forecast_df = pd.DataFrame(forecast, index=forecast_index, columns=['Forecasted'])

# Concatenate the forecast DataFrame with the original data
combined_data = pd.concat([data, forecast_df])

# Plotting actual and predicted values
plt.figure(figsize=(12, 6))
plt.plot(combined_data.index, combined_data['Actuals'], label='Actual')
plt.plot(combined_data.index[-12:], combined_data['Forecasted'][-12:], label='Predicted')
plt.xlabel('Time')
plt.ylabel('Units')
plt.title('Actual vs Predicted next 12 Months')
plt.legend()
plt.show()

#without outliers
forecast_index2 = pd.date_range(start=data2.index[-1] + pd.DateOffset(months=1), periods=len(forecast2), freq='M')
forecast_df2 = pd.DataFrame(forecast2, index=forecast_index2, columns=['Forecasted'])

# Concatenate the forecast DataFrame with the original data
combined_data2 = pd.concat([data2, forecast_df2])

# Plotting actual and predicted values
plt.figure(figsize=(12, 6))
plt.plot(combined_data2.index, combined_data2['Actuals'], label='Actual')
plt.plot(combined_data2.index[-12:], combined_data2['Forecasted'][-12:], label='Predicted')
plt.xlabel('Time')
plt.ylabel('Units')
plt.title('Actual vs Predicted next 12 Months')
plt.legend()
plt.show()

print("Original Dataset")
metrics(data[-12:].values, forecast)
print()
print("Without Outliers")
metrics(data2[-12:].values, forecast2)

