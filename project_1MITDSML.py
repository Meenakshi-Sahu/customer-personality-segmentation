# -*- coding: utf-8 -*-

The dataset includes historical data on customer demographics, personality traits, and purchasing behaviors. Key attributes are:  

1. **Customer Information**  
   - **ID:** Unique identifier for each customer.  
   - **Year_Birth:** Customer's year of birth.  
   - **Education:** Education level of the customer.  
   - **Marital_Status:** Marital status of the customer.  
   - **Income:** Yearly household income (in dollars).  
   - **Kidhome:** Number of children in the household.  
   - **Teenhome:** Number of teenagers in the household.  
   - **Dt_Customer:** Date when the customer enrolled with the company.  
   - **Recency:** Number of days since the customer’s last purchase.  
   - **Complain:** Whether the customer complained in the last 2 years (1 for yes, 0 for no).  

2. **Spending Information (Last 2 Years)**  
   - **MntWines:** Amount spent on wine.  
   - **MntFruits:** Amount spent on fruits.  
   - **MntMeatProducts:** Amount spent on meat.  
   - **MntFishProducts:** Amount spent on fish.  
   - **MntSweetProducts:** Amount spent on sweets.  
   - **MntGoldProds:** Amount spent on gold products.  

3. **Purchase and Campaign Interaction**  
   - **NumDealsPurchases:** Number of purchases made using a discount.  
   - **AcceptedCmp1:** Response to the 1st campaign (1 for yes, 0 for no).  
   - **AcceptedCmp2:** Response to the 2nd campaign (1 for yes, 0 for no).  
   - **AcceptedCmp3:** Response to the 3rd campaign (1 for yes, 0 for no).  
   - **AcceptedCmp4:** Response to the 4th campaign (1 for yes, 0 for no).  
   - **AcceptedCmp5:** Response to the 5th campaign (1 for yes, 0 for no).  
   - **Response:** Response to the last campaign (1 for yes, 0 for no).  

4. **Shopping Behavior**  
   - **NumWebPurchases:** Number of purchases made through the company’s website.  
   - **NumCatalogPurchases:** Number of purchases made using catalogs.  
   - **NumStorePurchases:** Number of purchases made directly in stores.  
   - **NumWebVisitsMonth:** Number of visits to the company’s website in the last month.


## **Importing necessary libraries**
"""

# Libraries to help with reading and manipulating data
import pandas as pd
import numpy as np

# libaries to help with data visualization
import matplotlib.pyplot as plt
import seaborn as sns

# Removes the limit for the number of displayed columns
pd.set_option("display.max_columns", None)
# Sets the limit for the number of displayed rows
pd.set_option("display.max_rows", 200)

# to scale the data using z-score
from sklearn.preprocessing import StandardScaler

# to compute distances
from scipy.spatial.distance import cdist, pdist

# to perform k-means clustering and compute silhouette scores
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

# to visualize the elbow curve and silhouette scores
from yellowbrick.cluster import KElbowVisualizer, SilhouetteVisualizer

# to suppress warnings
import warnings

warnings.filterwarnings("ignore")


# loading data into a pandas dataframe
data = pd.read_csv("/content/sample_data/Customer_Personality_Segmentation.csv", sep="\t")

"""## **Data Overview**

#### **Question 1**: What are the data types of all the columns?
"""

data.info()

"""##### **Observations:**

#### **Question 2:** Check the statistical summary of the data. What is the average household income?
"""

data.describe()

"""##### **Observations:**
The statistical summary indicates that the average household income is approximately 52,000. However, there’s a considerable range in values, with incomes spanning from below 20,000 to over 100,000, suggesting that customers belong to diverse income brackets.

#### **Question 3:** Are there any missing values in the data? If yes, treat them using an appropriate method
"""

data.isnull().sum()

data = data.dropna(subset=['Income'])

data['Dt_Customer'] = pd.to_datetime(data['Dt_Customer'], dayfirst=True)

data['Customer_Tenure_Days'] = (data['Dt_Customer'].max() - data['Dt_Customer']).dt.days
data[['Dt_Customer', 'Customer_Tenure_Days']].head()

data.drop(['ID', 'Dt_Customer', 'Z_CostContact', 'Z_Revenue'], axis=1, inplace=True)

data.info()

print(data['Education'].value_counts())
print(data['Marital_Status'].value_counts())

# Replace unusual values with 'Other'
data['Marital_Status'] = data['Marital_Status'].replace(
    ['Alone', 'Absurd', 'YOLO'], 'Other'
)

data['Marital_Status'].value_counts()

data = pd.get_dummies(data, columns=['Education', 'Marital_Status'], drop_first=True)

data.info()

data = data.astype(int)

data.info()

"""##### **Observations:**
Yes, there were some missing values in the dataset, mainly in the Income column. Since income plays an important role in understanding customer behavior, and because filling in missing values might have led to inaccurate results, hence decided to remove those rows entirely instead of imputing them.

Also, while cleaning the data,a few changes were made to ensure everything made sense:

In the Marital_Status column, there were some unusual or unclear entries like "YOLO" or "Absurd". These were either removed or grouped into broader, meaningful categories such as "Single", "Married", and so on.

The Education column already had values like "Graduation", "PhD", and "Master", which were consistent, so we kept them as they were, treating them as categorical data.

#### **Question 4**: Are there any duplicates in the data?
"""

data.duplicated().sum()

"""##### **Observations:**
Initially, when checking the raw dataset including all columns (like ID), there were no duplicate rows. However, after cleaning the data — such as dropping unnecessary columns and transforming some values — we ran the check again and found 182 duplicate entries.

## **Exploratory Data Analysis**

### Univariate Analysis

#### **Question 5:** Explore all the variables and provide observations on their distributions. (histograms and boxplots)
"""

cont_cols = list(data.columns)
for col in cont_cols:
    print(col)
    print('Skew :', round(data[col].skew(), 2))
    plt.figure(figsize=(15, 4))
    plt.subplot(1, 2, 1)
    data[col].hist(bins=10, grid=False)
    plt.ylabel('count')
    plt.title(f'Distribution of {col}')

    plt.subplot(1, 2, 2)
    sns.boxplot(x=data[col])
    plt.title(f'Boxplot of {col}')
    plt.show()

"""##### **Observations:**
Observation:
From the histograms and boxplots:

Income is right-skewed with a few high-income outliers.

Year_Birth shows a concentration around 1970–1990.

Product-related spendings (e.g., MntWines, MntFruits) have many low values with some higher extremes, indicating a skewed distribution.

Features like NumDealsPurchases and NumStorePurchases are categorical-like with limited unique values, often between 0–5.

### Bivariate Analysis

#### **Question 6:** Perform multivariate analysis to explore the relationsips between the variables.
"""

plt.figure(figsize=(14, 10))

sns.heatmap(
    data.corr(),
    annot=True,
    fmt='.2f',linewidths=0.5,annot_kws={"size": 8} )

"""##### **Observations:**
Positive correlations:

There’s a strong positive correlation between the various product spending features like MntWines, MntFruits, MntMeatProducts, MntFishProducts, and MntSweetProducts. This suggests that customers who spend more in one category tend to spend more in others too — likely indicating a higher overall spending behavior.

NumCatalogPurchases, NumStorePurchases, and NumWebPurchases also show moderate to strong positive correlations, suggesting overlap in purchasing channels.

Income has a moderate positive correlation with product-related variables and some campaign acceptances, suggesting higher-income customers are more responsive and spend more.

Education and marital status dummies show very weak correlations, meaning they do not strongly influence most of the numerical features.

## **K-means Clustering**
"""

#Initialize the scaler
scaler = StandardScaler()

# Fit and transform the data
scaled_data = scaler.fit_transform(data)

# (Optional) Convert back to DataFrame for readability
scaled_df = pd.DataFrame(scaled_data, columns=data.columns)

"""#### **Question 7** : Select the appropriate number of clusters using the elbow Plot. What do you think is the appropriate number of clusters?"""

from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

wcss = []

# Try cluster numbers from 1 to 10
for k in range(1, 11):
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(scaled_df)
    wcss.append(kmeans.inertia_)

# Plot elbow curve
plt.figure(figsize=(8, 5))
plt.plot(range(1, 11), wcss, marker='o')
plt.title('Elbow Method')
plt.xlabel('Number of clusters (k)')
plt.ylabel('WCSS (Inertia)')
plt.grid(True)
plt.show()

"""```
```

##### **Observations:**
The Elbow Plot shows a distinct bend at k = 3, suggesting that 3 clusters may be a good choice as it balances within-cluster compactness with model simplicity.

#### **Question 8** : finalize appropriate number of clusters by checking the silhoutte score as well. Is the answer different from the elbow plot?
"""

for k in range(2, 11):
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = kmeans.fit_predict(scaled_df)
    sil_score = silhouette_score(scaled_df, labels)
    print(f"Silhouette Score for k = {k}: {sil_score:.4f}")

"""##### **Observations:**
Silhouette scores were calculated for k=2 to k=10. The highest silhouette score was observed for k = 2 (0.1844). Although k=3 looked promising in the elbow method, the score indicates that k=2 provides better-defined clusters.

#### **Question 9**: Do a final fit with the appropriate number of clusters. How much total time does it take for the model to fit the data?
"""

from sklearn.cluster import KMeans
import time

# Start timer
start_time = time.time()

# Final KMeans fit
kmeans = KMeans(n_clusters=2, random_state=42)
data['Cluster'] = kmeans.fit_predict(scaled_df)

# End timer
end_time = time.time()
fit_time = end_time - start_time

print(f"⏱️ Model fit time: {fit_time:.2f} seconds")

"""##### **Observations:**
The final model was fitted using k = 2, which took only 0.01 seconds, demonstrating that the K-Means algorithm is computationally efficient on this dataset.

## **Cluster Profiling and Comparison**

#### **Question 10**: Perform cluster profiling using boxplots for the K-Means algorithm. Analyze key characteristics of each cluster and provide detailed observations.
"""

data['Cluster'] = kmeans.labels_

# Group by cluster and calculate mean & median
mean = data.groupby('Cluster').mean(numeric_only=True)
median = data.groupby('Cluster').median(numeric_only=True)

# Combine
df_kmeans = pd.concat([mean, median], axis=0)

# Dynamically rename rows based on number of clusters
num_clusters = data['Cluster'].nunique()
df_kmeans.index = (
    [f'Cluster_{i} Mean' for i in range(num_clusters)] +
    [f'Cluster_{i} Median' for i in range(num_clusters)]
)

# Transpose for better display
df_kmeans.T.head(10)

import matplotlib.pyplot as plt
import seaborn as sns

# Add Cluster column to the scaled DataFrame as well
scaled_df['Cluster'] = data['Cluster']

# Select important features for profiling
selected_features = [
    'Income', 'Recency', 'Customer_Tenure_Days',
    'MntWines', 'MntFruits', 'MntMeatProducts',
    'MntFishProducts', 'MntSweetProducts', 'MntGoldProds'
]

# Plot boxplots
plt.figure(figsize=(20, 30))
for i, col in enumerate(selected_features):
    plt.subplot(5, 2, i + 1)
    sns.boxplot(data=scaled_df, x='Cluster', y=col)
    plt.title(f'{col} by Cluster')
plt.tight_layout()
plt.show()

"""##### **Observations:**

Boxplots show:

Cluster 0: Lower income, fewer online visits, and less spending on premium products.

Cluster 1: Higher income, greater spending on all product categories, and more online interactions.
This suggests that Cluster 1 contains high-value customers, while Cluster 0 represents more modest spenders.

#### **Question 11**: Perform cluster profiling on the data using a barplot for the K-Means algorithm. Provide insights and key observations for each cluster based on the visual analysis.
"""

# Select features to visualize cluster differences
features_to_plot = [
    'Income', 'Recency', 'Customer_Tenure_Days',
    'MntWines', 'MntMeatProducts', 'MntFruits',
    'MntFishProducts', 'MntSweetProducts', 'MntGoldProds'
]

# Get mean values per cluster
cluster_means = data.groupby('Cluster')[features_to_plot].mean()

important_features = [
    'Income', 'Recency', 'Customer_Tenure_Days',
    'MntWines', 'MntMeatProducts', 'MntFruits',
    'NumWebPurchases', 'NumCatalogPurchases'
]

data[important_features + ['Cluster']].groupby('Cluster').mean().T.plot(
    kind='bar', figsize=(16, 6)
)
plt.title('Cluster Profiling: Key Feature Means by Cluster')
plt.ylabel('Mean (Original Scale)')
plt.xticks(rotation=45)
plt.grid(axis='y')
plt.tight_layout()
plt.show()

"""##### **Observations:**
Barplots (based on standardized features) reveal:

Cluster 1 exhibits higher-than-average z-scores across almost all variables (e.g., Income, MntWines, WebPurchases), suggesting affluent, engaged customers.

Cluster 0 tends to have negative z-scores, indicating lower values across most features, including income, response rates, and product purchases.

## **Business Recommedations**

#### **Question 12**: Based on the cluster insights, what business recommendations can be provided?

##### **SOLUTION**

Based on our K-Means clustering with k=2,identified two distinct customer segments, each showing unique behaviors and preferences. Understanding these differences allows us to design more effective and personalized strategies.

-> Cluster 0 appears to represent a more price-conscious segment. These customers typically have lower incomes, make fewer purchases, and haven’t engaged with the store in a while — as indicated by their higher recency values. They also tend to live in larger households with more kids at home. Their responses to past marketing campaigns have been quite low, and they’re less active on online platforms, suggesting a preference for offline engagement. Additionally, they seem newer to the brand, with shorter customer tenure.

-> Cluster 1, on the other hand, includes the brand’s most valuable customers. They have higher incomes, shop frequently — especially for premium items like wines, meats, and even gold products — and they engage more recently and more often. These customers show strong loyalty, indicated by longer tenure and high response rates to marketing campaigns. They are also digitally inclined, making more online and catalog purchases, which signals comfort with tech and convenience-driven shopping.


strategies to be implemented:

->Personalized Marketing: For Cluster 1, we should continue with premium product promotions and loyalty rewards. Exclusive deals and early access to new collections would keep them engaged. In contrast, Cluster 0 would respond better to budget-friendly bundles and first-time discount offers.

->Retention Efforts: For high-value Cluster 1 customers, introducing tiered loyalty programs or subscriptions could deepen their relationship with the brand. Cluster 0 may benefit from reactivation campaigns, such as “Welcome back” discounts to encourage return visits.

->Inventory & Layout Optimization: In locations dominated by Cluster 1, stores should focus on stocking high-end goods and making the in-store experience quick and premium. Meanwhile, stores with more Cluster 0 customers should highlight value-driven products, family-oriented promotions, and clearly labeled deals.

->Customer Value Maximization: Cluster 1 customers are clearly high in lifetime value. Proactively monitoring their behavior can help us predict and prevent churn. Although Cluster 0 shows lower current value, they hold potential. With the right incentives and tailored campaigns, they can be nurtured into more engaged, valuable customers.
"""
