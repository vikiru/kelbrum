---
title: Data Clustering with K-means
---

## Data Clustering with K-means

### Identifying Clustering Algorithms

Once the data was [normalized](/normalize), the next step was to figure out how to group the data based on their similarity. Upon researching this topic, I found out that there were several algorithms to achieve this such as:

-   **K-means clustering**
-   **K-mediods clustering**
-   **K-nearest neighbors**
-   **Hierarchal clustering**
-   **DBSCAN**

There were several other algorithms as well, however, I decided to use K-means clustering as I felt it was easier to understand and applicable for my use case.

### Choosing the Right Tools

To cluster the data, several k-means clustering npm packages were looked at and finally, I finalized on using [ml-kmeans](https://github.com/mljs/kmeans) combining it with [ml-distance](https://github.com/mljs/distance) and [simple-statistics](https://github.com/simple-statistics/simple-statistics).

**ml-distance** offered various distance and similarity calculations and **ml-kmeans** allowed for the use of custom distance functions so this worked out really well for me.

### Understanding Distance Functions

I tried to learn about some common distance functions used to cluster data such as euclidean, cosine, squared euclidean, manhattan, hamming, etc and through trial and error I experimented with all of the functions provided by **ml-distance**. Through my experiments, which involved applying various normalization techniques to anime properties and experimenting with different feature combinations, I discovered that the **curse of dimensionality** significantly impacted my results as the number of features in my feature tensors increased.

### Evaluating Clustering Effectiveness

I was able to tell this as I learned that there were a few metrics which can tell how effective clustering is, such as the following:

-   **Within Cluster Sum of Squares (WCSS)**
-   **Elbow Method**
-   **Silhouette Score**

While other metrics were available, my primary focus was on the Within Cluster Sum of Squares (WCSS) and the Silhouette Score when feasible. Fortunately, calculating the WCSS was straightforward with the assistance of **ml-kmeans**, and the Silhouette Score was computed using **simple-statistics**. However, the computation of the Silhouette Score became increasingly computationally intensive as the value of k increased, due to the large size of the feature tensors, leading me to prioritize the WCSS. My objective was to achieve the lowest WCSS and the highest Silhouette Score possible.

### Best Distance Functions for the Dataset

From my experiments, I learned that given my data set, the following functions worked out the best:

-   **Gower's Distance**
-   **Cosine Similarity**
-   **Dice Similarity**
-   **Sørensen–Dice coefficient**
-   **Jaccard Index**
-   **Tanimoto Index**

### Customizing the Distance Function

After additional experimentation, I attempted to develop a custom distance function by employing varying weights and combinations of distance measures for both categorical and numerical attributes. Initially, Cosine Similarity was employed, as it proved effective. Subsequently, I explored Gower's distance, which emerged as the most effective among the distance functions tested. Further improvements can definitely be made to the custom distance function perhaps, adjusting the weights for categorical and numerical data or combining other functions with the Gower's distance.

### Future Experimentation

Additionally, at this present time, the K-means model uses `k = 10` which means that there are only 10 clusters and given the size of the dataset with over ~15000 anime, there is potential for a large number of anime within each cluster. Further experimentation is necessary and ideally my goal would be to have a larger number of clusters and truly capture the distinct features of each anime grouping.
