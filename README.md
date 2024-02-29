<h2 align="center"> Kelbrum </h2>

**Kelbrum** is an anime recommendation engine designed to suggest anime titles that are similar to those chosen by users. It employs K-means++ clustering in combination with a custom distance function, which uses Gower's distance. The custom distance function assigns weighted values to each property of an anime such as its `title`, `genres`, `score` to accurately compute the distance between two seperate anime.

This project was bootstraped using [Vite.js](https://vitejs.dev/), along with [DaisyUI](https://daisyui.com/), [TailwindCSS](https://tailwindcss.com/), [React](https://react.dev/), and [React Router](https://reactrouter.com/).

> [!IMPORTANT]
> The data used within this project was possible thanks to the following:
>
> 1. [Original Kaggle Dataset](https://www.kaggle.com/datasets/dbdmobile/myanimelist-dataset) - The anime dataset was read and proccessed into a custom JavaScript class known as [AnimeEntry](./reccomender/models/AnimeEntry.js).
> 2. [JikanAPI](https://github.com/jikan-me/jikan-rest) - Missing information such as `pageURL`, `imageURL`, `trailerURL` and other existing properties which may have needed updates were updated by making several API requests to JikanAPI, which contains anime information obtained from [MyAnimeList](https://myanimelist.net/).

## 📖 Table of Contents

-   [📖 Table of Contents](#-table-of-contents)
-   [🛠️ Tech Stack](#️-tech-stack)
-   [📝 Prerequisites](#-prerequisites)
-   [⚡ Setup Instructions](#-setup-instructions)
-   [📜 Available Scripts](#-available-scripts)
-   [✨ Acknowledgments](#-acknowledgments)
-   [©️ License](#️-license)

## 🛠️ Tech Stack

Backend:

-   [Node.js](https://nodejs.org/en)
-   [Tensorflow.js](https://github.com/tensorflow/tfjs)
-   [simple-statistics](https://github.com/simple-statistics/simple-statistics)
-   [ml-distance](https://github.com/mljs/distance)
-   [ml-kmeans](https://github.com/mljs/kmeans)

Frontend:

-   [React](https://react.dev/)
-   [React Router](https://reactrouter.com/)
-   [Vite](https://vitejs.dev/)
-   [DaisyUI](https://daisyui.com/)
-   [TailwindCSS](https://tailwindcss.com/)

Dev Tools:

-   [ESLint](https://eslint.org/)
-   [Prettier](https://prettier.io/)
-   [WakaTime](https://wakatime.com/)

## 📝 Prerequisites

Ensure that the following dependencies are installed onto your machine by following the [Setup Instructions](#-setup-instructions).

-   [Node.js](https://nodejs.org/en/download)

## ⚡ Setup Instructions

1. Clone this repository to your local machine.

```bash
git clone https://github.com/vikiru/kelbrum.git
cd kelbrum
```

2. Download and install all required dependencies.

```bash
npm install
```

## 📜 Available Scripts

1. Start the app in the development environment.

```bash
npm run dev
```

2. Build the project files and optimize for production.

```bash
npm run build
```

3. Start the app with files optimized for production.

```bash
npm run preview
```

4. Lint all files and check if there are any issues, with [ESLint](https://eslint.org/).

```bash
npm run lint
```

5. Fix all ESLint issues then format the files with [Prettier](https://prettier.io/).

```bash
npm run prettier
```

## ✨ Acknowledgments

-   [csv-parse](https://github.com/adaltas/node-csv)
-   [MiniSearch](https://github.com/lucaong/minisearch)
-   [PapaParse](https://www.papaparse.com/)
-   [React Infinite Scroller](https://github.com/danbovey/react-infinite-scroller)
-   [SimpleIcons](https://simpleicons.org/)
-   [tailwind-scrollbar](https://github.com/adoxography/tailwind-scrollbar)
-   [Tensorflow.js](https://www.tensorflow.org/js)
-   [Tensorflow.js Documentation](https://js.tensorflow.org/api/latest/)
-   [Machine Learning Crash Course by Google](https://developers.google.com/machine-learning/crash-course/)
    -   [Clustering Algorithms](https://developers.google.com/machine-learning/clustering/clustering-algorithms)
    -   [Normalization](https://developers.google.com/machine-learning/data-prep/transform/normalization)
    -   [Machine Learning Glossary](https://developers.google.com/machine-learning/glossary)
    -   [Transforming Categorical Data](https://developers.google.com/machine-learning/data-prep/transform/transform-categorical)
-   [Docusaurus](https://docusaurus.io/)
-   [GitHub Pages](https://pages.github.com/)
-   [Shields Badges](https://github.com/badges/shields)
-   [regex101](https://regex101.com/)
-   [Favicon Generator](https://favicon.io/favicon-generator/)

Various web articles for research and learning, such as:

-   [17 types of similarity and dissimilarity measures used in data science](https://towardsdatascience.com/17-types-of-similarity-and-dissimilarity-measures-used-in-data-science-3eb914d2681)
-   [Gower's Distance](https://medium.com/analytics-vidhya/gowers-distance-899f9c4bd553)
-   [Introduction to similarity metrics](https://medium.com/analytics-vidhya/introduction-to-similarity-metrics-a882361c9be4)
-   [Types of recommendation systems & their use cases](https://medium.com/mlearning-ai/what-are-the-types-of-recommendation-systems-3487cbafa7c9)
-   [What is unsupervised learning?](https://www.ibm.com/topics/unsupervised-learning)

Additionally, this project would not be possible without the following sources of information:

-   [Original Kaggle Dataset](https://www.kaggle.com/datasets/dbdmobile/myanimelist-dataset)
-   [JikanAPI](https://github.com/jikan-me/jikan-rest)
-   [MyAnimeList](https://myanimelist.net/)

All external images and text used within this app belong to their respective owners.

## ©️ License

The contents of this repository are licensed under the terms and conditions of the [MIT](https://choosealicense.com/licenses/mit/) license.

[MIT](./LICENSE) © 2024-present Visakan Kirubakaran.
