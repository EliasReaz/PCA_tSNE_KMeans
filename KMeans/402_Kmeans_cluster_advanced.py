# import libraries
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pprint import pprint

from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

import warnings
warnings.filterwarnings("ignore")

# import data
df_tran = pd.read_excel("grocery_database.xlsx", sheet_name="transactions")
df_prod = pd.read_excel("grocery_database.xlsx", sheet_name="product_areas")
print("shape of df_prod: ", df_prod.shape)
pprint(df_prod.head())
print("-----")
print("shape of df_tran: ", df_tran.shape)
pprint(df_tran.head())

## merge df_prod and df_tran

df2 = pd.merge(left=df_tran, right=df_prod, how="inner", on="product_area_id")
print("shape of merged df2: ", df2.shape)
pprint(df2.head())

# drop non-food
df3 = df2[df2["product_area_name"] != "Non-Food"]
print("shape of df3: ", df3.shape)
pprint(df3.head(5))
print(df3["product_area_name"].unique())

# sns.boxplot(data=df3, x="product_area_name", y="sales_cost")
# plt.xlabel("product type")
# plt.ylabel("sale_cost")
# plt.show()

# print(df3.nunique())

## see the total cost per customer per product
total_sales_prod = df3.groupby(["customer_id", "product_area_name"]).agg(total_sales = \
    pd.NamedAgg(column="sales_cost", aggfunc="sum"))

print(total_sales_prod)

## pivot_table to see customer-wise total cost by product area

data_for_cluster = pd.pivot_table(df3, index="customer_id", \
    columns="product_area_name", values="sales_cost", aggfunc="sum", fill_value=0, margins=True, margins_name="total_sales").rename_axis(None, axis=1)
print(data_for_cluster.head())

# turn sales into percent of sales
data_for_cluster = data_for_cluster.div(data_for_cluster["total_sales"], axis=0)
print(data_for_cluster.head())
# drop total column
data_for_cluster = data_for_cluster.drop(columns="total_sales", axis=1)
print(data_for_cluster.head())

## check for missing values
print(data_for_cluster.isna().sum())


# normalize data
scale_norm = MinMaxScaler()

data_for_clustering_scaled = pd.DataFrame(scale_norm.fit_transform(data_for_cluster), columns=data_for_cluster.columns)

print(data_for_clustering_scaled.head())

###########################################
## use wCSS to find a good value of K
###########################################

k_values = list(range(1,10))

wcss_list = []

for k in k_values:
    kmeans = KMeans(n_clusters=k, random_state=42, max_iter=1000)
    kmeans.fit(data_for_clustering_scaled)
    wcss_list.append(kmeans.inertia_)

plt.plot(k_values, wcss_list)
plt.title("Within cluster sum of square - by k")
plt.xlabel("k")
plt.ylabel("wcss score")
plt.tight_layout()
plt.show()

###########################################
## instantiate and fit
###########################################
kmeans = KMeans(n_clusters=3, random_state=42)
kmeans.fit(data_for_clustering_scaled)


###########################################
## Use cluster information
###########################################
data_for_cluster["cluster"] = kmeans.labels_

print(data_for_cluster.head())

###########################################
# check cluster size
##########################################
data_for_cluster["cluster"].value_counts()

##############################################
# check for profile
###############################################

mean_sales_percnt = data_for_cluster.groupby("cluster").agg(dairy=pd.NamedAgg(column="Dairy", aggfunc="mean"),
                                     fruit=pd.NamedAgg(column="Fruit", aggfunc="mean"),
                                     meat=pd.NamedAgg(column="Meat", aggfunc="mean"),
                                     vegetables=pd.NamedAgg(column="Vegetables", aggfunc="mean"))

print(mean_sales_percnt.head())

colors = ['cyan', 'lightgreen', 'red', 'green'] ## Colors for the bars
mean_sales_percnt.plot(kind='bar', stacked=True, color=colors) ## Plot
plt.ticklabel_format(style='plain', useOffset=False, axis='y') ## No offset
plt.gca().set_ylabel("percent of sales") ## 
plt.xticks([0,1,2], ["Casual", "Vegetarian", "Vegan"], rotation=0)
plt.legend(bbox_to_anchor=(1.0, 1.05))
plt.tight_layout()
# plt.savefig("ABC_grocery_customer_segmentation.jpg")
plt.show()
