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

To cluster the data, several k-means clustering npm packages were looked at and finally, I finalized on using [ml-kmeans](https://github.com/mljs/kmeans) combining it with [ml-distance](https://github.com/mljs/distance) and [simple-statistics](https://github.com/simple-statistics/simple-statistics). Addtionally, to perform TF-IDF analysis on anime synopses, [natural](https://github.com/NaturalNode/natural) was used alongside [remove-stopwords](https://github.com/WorldBrain/remove-stopwords), [word-list](https://github.com/sindresorhus/word-list), and [lemmatizer](https://github.com/FinNLP/lemmatizer).

**ml-distance** offered various distance and similarity calculations and **ml-kmeans** allowed for the use of custom distance functions so this worked out really well for me.

### Understanding Distance Functions

I tried to learn about some common distance functions used to cluster data such as euclidean, cosine, squared euclidean, manhattan, hamming, etc and through trial and error I experimented with all of the functions provided by **ml-distance**. Through my experiments, which involved applying various normalization techniques to anime properties and experimenting with different feature combinations, I discovered that the **curse of dimensionality** significantly impacted my results as the number of features in my feature tensors increased.

To combat the **curse of dimensionality**, I decided to use various normalization techniques, combinations of features and different weightings to these features. Additionally, I did try to reduce the number of features I used as originally, I wanted to see how the effect of all features together would be and it proved to be computationally expensive to compute for higher k values and harder to cluster effectively.

### Evaluating Clustering Effectiveness

I was able to assess the effectiveness of clustering by identifying several metrics that indicate the efficiency of clustering, including:

-   **Within Cluster Sum of Squares (WCSS)**
-   **Elbow Method**
-   **Silhouette Score**

While other metrics were available, my primary focus was on the Within Cluster Sum of Squares (WCSS) and the silhouette score when feasible. Fortunately, calculating the WCSS was straightforward with the assistance of **ml-kmeans**, and the silhouette score was computed using **simple-statistics**. However, the computation of the silhouette score became increasingly computationally intensive as the value of k increased, due to the large size of the feature tensors, leading me to prioritize the WCSS. My objective was to achieve the lowest WCSS and the highest silhouette score possible.

### Best Distance Functions for the Dataset

From my experiments, I learned that given my data set, the following functions worked out the best:

- **Manhattan Distance**
-   **Dice Similarity**
-   **Jaccard Index**
-   **Gower's Distance**
-   **Cosine Similarity**
-   **Sørensen–Dice coefficient**
-   **Tanimoto Index**

### Customizing the Distance Function

After additional experimentation, I attempted to develop a custom distance function by employing varying weights and combinations of distance measures for both categorical and numerical attributes. Initially, cosine similarity was employed, as it proved effective. After cosine similarity, I ended up using gower's distance and that seemed to work out well purely based on the wcss values however, I learned later that this was due to the total number of values as the gower distance performed poorly as the number of values in the concatenated tensors for each anime increased, especially due to the amount of binary vectors.

To develop the current weighted distance function, I compared anime that were known to be similar, utilizing various distance measures with both the concatenated tensors as a whole and each individual feature tensor. This approach helped identify which properties most significantly increased the distance between each anime. At the same time, I was experimenting with different normalization techniques and feature tensor combinations. Eventually, I added weights which required a considerable amount of trial and error to achieve the current satisfactory level of recommendations as I had to experiment with different weightings for each property and different distance measures for each.

In the end, the manhattan distance was used for properties such as `type`, `rating`, and `demographics` where there was a numerical value and a need to seperate anime such as anime of type `TV` vs. `Movie`. The dice distance was used for all other properties such as `genres`, `themes`, `synopsis`, etc.

### Future Experimentation

The K-means model currently uses a low k-value, `k = 10` which means that there are only 10 clusters and given the dataset size, that amounts to a significant amount of anime per cluster. Further experimentation is required to investigate larger k-values, which can better balance the system's objectives and enhance the quality of recommendations. Moreover, the weights applied and the properties contain potential for further enhancement. Ideally, aiming for a larger number of clusters would enable a more accurate representation of the unique features of each anime grouping.
