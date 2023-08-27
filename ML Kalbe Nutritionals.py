# -*- coding: utf-8 -*-
"""ML Kalbe Nutrititionals.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Qy7YhN52HbkBD32p0EDKmrz_jVCfWbI8

# Import Library
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

from sklearn import preprocessing
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
import pmdarima as pm
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_samples, silhouette_score
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error, mean_squared_error
from yellowbrick.cluster import KElbowVisualizer

import warnings
warnings.filterwarnings('ignore')

"""# Import Data"""

df_customer = pd.read_csv('Customer.csv', sep= ';')
df_product = pd.read_csv('Product.csv', sep= ';')
df_store = pd.read_csv('Store.csv', sep= ';')
df_transaction = pd.read_csv('Transaction.csv', sep= ';')

"""# Data Preparation"""

df_transaction.info()

df_customer.info()

df_product.info()

df_store.info()

df1 = pd.merge(df_transaction, df_customer, on='CustomerID', how='inner')
df2 = pd.merge(df1, df_store, on = 'StoreID', how = 'inner')
df_merged = pd.merge(df2, df_product, on = 'ProductID', how = 'inner')
df_merged.head()

df_merged.info()

"""The columns Price_x and Price_y have the same values in each column, because base on the same data from Product data so one of them can be dropped."""

df_merged.drop(columns ='Price_y', inplace = True)

df_merged.isna().sum()

df_merged.duplicated().sum()

#fill missing values with Unknown
df_merged['Marital Status'].fillna('Unknown', inplace=True)

df_merged.isna().sum()

df_merged.info()

df_merged.Date

"""### Change Data Type of Irrelevant Data Types"""

df_merged['Date'] = pd.to_datetime(df_merged['Date'])
df_merged['Longitude'] = df_merged['Longitude'].apply(lambda x: x.replace(',','.')).astype(float)
df_merged['Latitude'] = df_merged['Latitude'].apply(lambda x: x.replace(',','.')).astype(float)

df_merged.head()

df_merged.info()

"""# Time Series Regression Analysis"""

df_reg = df_merged.groupby('Date').agg({'Qty':'sum'})
df_reg

# Visualize Data
df_reg.plot(figsize=(12,6))

#Split Data Train & Data Test
print(df_reg.shape)
test_size = round(df_reg.shape[0] * 0.15)
train=df_reg.iloc[:-1*(test_size)]
test=df_reg.iloc[-1*(test_size):]
print(train.shape,test.shape)

plt.figure(figsize=(12,5))
sns.lineplot(data=train, x=train.index, y=train['Qty'])
sns.lineplot(data=test, x=test.index, y=test['Qty'])
plt.show()

"""## Data Stationary Check"""

from statsmodels.tsa.stattools import adfuller
def adf_test(dataset):
     dftest = adfuller(dataset, autolag = 'AIC')
     print("1. ADF : ",dftest[0])
     print("2. P-Value : ", dftest[1])
     print("3. Num Of Lags : ", dftest[2])
     print("4. Num Of Observations Used For ADF Regression:",      dftest[3])
     print("5. Critical Values :")
     for key, val in dftest[4].items():
         print("\t",key, ": ", val)
adf_test(df_reg)

"""#### P-Value < 0.05 shows that the data is stationary and can be used in time series analysis with ARIMA"""

# ACF and PACF plots to determine p and q values
fig, ax = plt.subplots(1, 2, figsize=(12, 4))
plot_acf(df_reg.diff().dropna(), lags=40, ax=ax[0])
plot_pacf(df_reg.diff().dropna(), lags=40, ax=ax[1])
plt.show()

"""#### The Autocorrelation graph (ACF) shows that the p order is 2 because the first and second lag is significantly out of the significant limit, <br> meanwhile the Partial Autocorrelation graph (PCF) shows that the q order is 3 due to the significant correlation of the first until third lag.

## Modelling

### Auto-fit ARIMA
"""

#auto-fit ARIMA
auto_arima = pm.auto_arima(train, stepwise=False, seasonal=False)
auto_arima

"""### Hyperparameter Tuning"""

from itertools import product
#Make list for p, d, dan q
p = range(0, 4)  # 0-3
d = range(0, 4)  # 0-3
q = range(0, 4)  # 0-3
#Using the product function from itertools to create combinations of p, d, and q.
pdq = list(product(p, d, q))
print(pdq)

from statsmodels.tsa.arima.model import ARIMA

aic_scores = []

for param in pdq:
    model = ARIMA(df_reg, order=param)
    model_fit = model.fit()
    aic_scores.append({'par': param, 'aic': model_fit.aic})

best_aic = min(aic_scores, key=lambda x: x['aic'])
print(best_aic)

#Hyperparameter tuning
model_hyper = ARIMA(train, order=best_aic['par'])
model_fit_hyper = model_hyper.fit()

"""###  Manual Hyperparameter Tuning"""

#Trial and error tuning
model_manual = ARIMA(train, order=(40,2,2))
model_fit_manual = model_manual.fit()

"""### Plot Forecasting"""

#plot forecasting
forecast_manual = model_fit_manual.forecast(len(test))
forecast_hyper = model_fit_hyper.forecast(len(test))
forecast_auto = auto_arima.predict(len(test))

df_plot = df_reg.iloc[-100:]

df_plot['forecast_manual'] = [None]*(len(df_plot)-len(forecast_manual)) + list(forecast_manual)
df_plot['forecast_hyper'] = [None]*(len(df_plot)-len(forecast_hyper)) + list(forecast_hyper)
df_plot['forecast_auto'] = [None]*(len(df_plot)-len(forecast_auto)) + list(forecast_auto)

df_plot.plot()
plt.show()

"""### Metrics Evaluation"""

#Manual parameter tuning metrics

mae = mean_absolute_error(test, forecast_manual)
mape = mean_absolute_percentage_error(test, forecast_manual)
rmse = np.sqrt(mean_squared_error(test, forecast_manual))

print(f'mae - manual: {round(mae,4)}')
print(f'mape - manual: {round(mape,4)}')
print(f'rmse - manual: {round(rmse,4)}')

#Hyperparameter tuning metrics

mae = mean_absolute_error(test, forecast_hyper)
mape = mean_absolute_percentage_error(test, forecast_hyper)
rmse = np.sqrt(mean_squared_error(test, forecast_hyper))

print(f'mae - hyper: {round(mae,4)}')
print(f'mape - hyper: {round(mape,4)}')
print(f'rmse - hyper: {round(rmse,4)}')

#Auto-fit ARIMA metrics

mae = mean_absolute_error(test, forecast_auto)
mape = mean_absolute_percentage_error(test, forecast_auto)
rmse = np.sqrt(mean_squared_error(test, forecast_auto))

print(f'mae - auto: {round(mae,4)}')
print(f'mape - auto: {round(mape,4)}')
print(f'rmse - auto: {round(rmse,4)}')

"""### Manual Hyperparameter Tuning with order (40,2,2) shows the best evaluation metrics.

## Forecast Quantity Sales with The Best Parameter
"""

#Apply model to forecast data
model = ARIMA(df_reg, order=(40, 2, 2))
model_fit = model.fit()
forecast = model_fit.forecast(steps=31)

df_reg

forecast

#Plot forecasting
plt.figure(figsize=(12,5))
plt.plot(df_reg)
plt.plot(forecast,color='orange')
plt.title('Quantity Sales Forecasting')
plt.show()

forecast.describe()

"""### From the forecast, the average quantity sales in January 2023 is 44.489815 or up rounded to around 44 pcs/day.

# Clustering
"""

df_merged.head()

df_preclust = df_merged.groupby('CustomerID').agg({'TransactionID':'count',
                                                   'Qty':'sum',
                                                   'TotalAmount':'sum'}).reset_index()
df_preclust

df_preclust.info()

df_cluster = df_preclust.drop(columns = ['CustomerID'])
df_cluster.head()

df_cluster.info()

df_cluster.isna().sum()

#dataset standardization
X = df_cluster.values
X_std = StandardScaler().fit_transform(X)
df_std = pd.DataFrame(data=X_std,columns=df_cluster.columns)
df_std.isna().sum()

#Normalizing a dataset with MinMaxScaler
X_norm = MinMaxScaler().fit_transform(X)
X_norm

#Normalizing dataset with sklearn preprocessing
X_norm2 = preprocessing.normalize(df_cluster)
X_norm2

X_std

df_std

wcss= []
for n in range (1,11):
    model1 = KMeans(n_clusters=n, init='k-means++', n_init = 10, max_iter=100, tol =0.0001, random_state = 100)
    model1.fit(X_std)
    wcss.append(model1.inertia_)
print(wcss)

plt.figure(figsize=(10,8))
plt.plot(list(range(1,11)), wcss, color = 'blue', marker = 'o', linewidth=2, markersize=12, markerfacecolor= 'm',
         markeredgecolor= 'm')
plt.title('WCSS vs Number of Cluster', fontsize = 15)
plt.xlabel('Number of Cluster')
plt.ylabel('WCSS')
plt.xticks(list(range(1,11)))
plt.show()

#Elbow Method with yellowbrick library
visualizer = KElbowVisualizer(model1, k=(2,10))
visualizer.fit(X_std)
visualizer.show()

K = range(2,8)
fits=[]
score=[]

for k in K:
    model = KMeans(n_clusters = k, random_state = 0, n_init= 'auto').fit(X_std)
    fits.append(model)
    score.append(silhouette_score(X_std, model.labels_, metric='euclidean'))

sns.lineplot(x = K, y = score)

"""The best cluster (k) is found at 4 clusters"""

# Kmeans n_cluster = 4
#Clustering Kmeans
kmeans_4 = KMeans(n_clusters=4,init='k-means++',max_iter=300,n_init=10,random_state=100)
kmeans_4.fit(X_std)

df_cluster['cluster'] = kmeans_4.labels_
df_cluster.head()

plt.figure(figsize=(6,6))
sns.pairplot(data=df_cluster,hue='cluster',palette='Set1')
plt.show()

df_cluster['CustomerID'] = df_preclust['CustomerID']
df_cluster_mean = df_cluster.groupby('cluster').agg({'CustomerID':'count','TransactionID':'mean','Qty':'mean','TotalAmount':'mean'})
df_cluster_mean.sort_values('CustomerID', ascending = False)

"""### Summary
* Cluster 3 <br>
    - The cluster with the highest number of customers.
    - Customer characteristics rank third in every metric (transaction, quantity, total amount).
<br> **Recommendations**:
        - Build good relationships with customers.
        - Conduct surveys to further understand the interests of the majority customers.
* Cluster 2 <br>
    - Customer characteristics ranking second highest in every metric.
<br> **Recommendations**:
        - Offer regular promotions to boost transactions.
        - Implement upselling strategies for high-priced products.
* Cluster 1 <br>
    - Customers with the lowest values in each metric.
<br> **Recommendations**:
        - Offer significant discount prices to increase customer transactions.
        - Provide promotions for transactions with higher quantities.
        - Conduct surveys to explore potential product improvements.
* Cluster 0 <br>
    - The cluster with the lowest number of customers.
    - Customers with the highest values in each metric.
<br> **Recommendations**:
        - Implement loyalty programs to maintain transactions.
        - Conduct customer satisfaction surveys.
        - Employ upselling strategies for higher-priced products.

"""

