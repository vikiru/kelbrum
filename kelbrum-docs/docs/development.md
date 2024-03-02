---
title: 🔧 Development Overview
---

## 🔧 Development Overview

To develop a project like this, several different steps were neccessary alongside many hours of trial and error.

### Finding a suitable database

To achieve this, I browsed through Kaggle to find datasets with the information that I would need for this situation, ideally just the anime information would have been enough. I originally used this [dataset](https://www.kaggle.com/datasets/nikhil1e9/myanimelist-anime-and-manga/data) however, I ended up transitioning to the current [dataset](https://www.kaggle.com/datasets/dbdmobile/myanimelist-dataset) as it provided more detailed information and addtionally, I could see the license information for the dataset.

### Determining how to use dataset

My first thought was to figure out how to use machine learning frameworks such as Tensorflow or PyTorch and create a model based on the dataset using those. This would have involved a similar kind of process to what I achieved in the end, normalizing the data and creating feature tensors, however, I would have needed `labels` to test the models ability to predict. I could have used the `score` property of an anime however, there are several outliers in the thousands with values of 0 or 'Unknown' for various properties including `score` and additionally, this did not suit my use case. I later learned that what I was originally trying to achieve was something known as **supervised learning** and then I learned that there was something known as unsupervised learning which did not need labels of any kind, this seemed like what I needed. From here, I had to determine the type of filtering to use within the recommendation system, I learned there were two main types, content-based and collaborative filtering followed by a hybrid approach which would combine both of the methods. Given the dataset, I did have the capability to perform both types of filtering, however, the size of the user interaction data was `1 GB` and I did attempt to try to use it however, the issue is that there are over 200, 000 users within that data and over 15, 000 anime within the dataset which means utilizing this in a user-interaction matrix would have been computationally expensive. That is when I decided to just use content-based filtering.

### Normalizing the Data

Once I determined that I would use content-based filtering, I had to research various normalizing techniques for the various types of data that existed within my data and use this to create feature tensors through Tensorflow, further explained [here](/normalize).

### Clustering the Data

Since the objective of my project was to recommend anime that was similar to user-selected anime, I had to figure out a way to group anime based on their properties. This led me to research various existing clustering algorithms where I finalized on using **k-means** clustering. To effectively cluster anime, I had to also determine a distance function which would be used to tell how similar two distinct anime were based on their properies, in the end, **Gower's Distance** was used. This process is further explained [here](/kmeans).

### Designing the UI

Once all the previous steps were completed, the final step was to design a simple and easy to use UI that was as visually appealing as possible, to achieve this goal I utilized [React](https://react.dev/) and [React Router](https://reactrouter.com/) in combination with [TailwindCSS](https://tailwindcss.com/) and [DaisyUI](https://daisyui.com/) alongside various npm packages such as [MiniSearch](https://github.com/lucaong/minisearch), [lodash](https://github.com/lodash/lodash), [tailwind-scrollbar](https://github.com/adoxography/tailwind-scrollbar), and [React Infinite Scroller](https://github.com/danbovey/react-infinite-scroller).
