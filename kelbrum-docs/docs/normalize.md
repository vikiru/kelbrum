---
title: 📏 Normalizing Data
---

## 📏 Normalizing Data for K-means clustering

Given the strucure of an [AnimeEntry](/model) model, it can be seen that there is a variety of data types present. There is data that can be considered as `categorical`, `ordinal`, and `numerical`.

To handle these various data types and ensure that K-means clustering was possible, there was a need to normalize the existing data. Various normalization techniques were implemented and after trial and error, the following were used in the current model:

- **Ordinal Encoding** For anime properties such as `type`, `rating`, and `demographics`, originally I was using multi-hot encoding however, I noticed that just the presence/absence of a property was not sufficient as the distance between anime was key. For example, I wanted anime of type `TV` and `ONA` to be closer in distance compared to `TV` and `Movie`.  To accomplish this, I chose to assign distinct values to each unique value within each of these properties, leveraging my understanding of how related values are associated with each other
-   **Multi-Hot Encoding**: For anime properties such as `genres`, `demographics`, `source`, etc, this was normalized into a binary vector filled with 1's and 0's, indicating the presence or absence of a unique value
-   **Min-Max Scaling**: For anime properties such as `score` and `durationMinutes`, the data was normalized by determining the minimum and maximum values of each property and utilizing the following formula: `(value - min) / (max - min)`

Other normalization techniques were explored as well during the experimentation phase of the project, such as:

-   **Robust Scaling**: This method could be applied to numerical attributes like `score` and `episodes`, which would be beneficial given the presence of outliers in the dataset. These outliers include anime with scores or episode counts of 0 or "Unknown" due to insufficient information
-   **Ordinal Encoding**: This technique is suitable for properties with a natural order, such as `rank` and `popularity`
-   **Combination Encoding**: This technique aims to represent each unique value with a distinct integer. For each anime, the values of its properties are combined into a single value. For instance, consider the `genres` property of a given anime with values `['action', 'comedy', 'romance']`. Each genre is assigned a unique integer, starting from 0 up to the total count of unique values. These integers are then summed to produce a single value for the genres property of that anime

To see more information about the normalization process, you can consider checking out the [source code](https://github.com/vikiru/kelbrum/src/recommender/utils/normalize.js) which shows all the normalization functions and additionally, how they are incorporated to create feature tensors using Tensorflow.
