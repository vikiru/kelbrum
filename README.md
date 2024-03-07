<div align="center" id="logo">
    <img src="logo.png"/>
</div>

<div align='center' id="badges">

<a href="https://vikiru.github.io/kelbrum/">
	<img src="https://img.shields.io/badge/documentation-docs-orange" alt="Documentation"/>
</a>
<a href="">
    <img src="https://img.shields.io/badge/Web-live%20site-blue" alt="kelbrum API hosted via Render"/>
</a>
<br/>
 <a href="https://wakatime.com/@vikiru/projects/ioitawlsqa">
  <img src="https://wakatime.com/badge/user/5e62f99d-3a1e-4fd2-8f37-77919d626a67/project/018d6816-57f1-4009-a823-d00889610f66.svg"
  alt="Wakatime Coding Stats for Kelbrum"/>
 </a>
 <br/>
 <a href="https://github.com/vikiru/kelbrum/blob/main/LICENSE">
  <img src="https://img.shields.io/badge/license-MIT-aqua" alt="MIT License Badge"/>
 </a>
 <a href="https://github.com/prettier/prettier">
  <img src="https://img.shields.io/badge/code_style-prettier-ff69b4.svg?style=flat-square" alt="Code Style - Prettier"/>
 </a>
<br/>
 <a href="https://github.com/vikiru/kelbrum/issues?q=is%3Aissue+is%3Aclosed">
  <img src="https://img.shields.io/github/issues-closed/vikiru/kelbrum" alt="Closed Issues"/>
 </a>
 <a href="https://github.com/vikiru/kelbrum/pulls?q=is%3Apr+is%3Aclosed">
  <img src="https://img.shields.io/github/issues-pr-closed/vikiru/kelbrum?label=closed%20prs" alt="Closed PRs"/>
 </a>
  <a href="https://github.com/vikiru/kelbrum/releases">
  <img src="https://img.shields.io/github/v/release/vikiru/kelbrum" alt="Release"/>
 </a>
<br/>
 <a href="https://github.com/vikiru/kelbrum/actions/workflows/lint.yml">
  <img src="https://github.com/vikiru/kelbrum/actions/workflows/lint.yml/badge.svg" alt="GitHub Lint Action Workflow Status"/>
 </a>
</div>

---

**Kelbrum** is an anime recommendation system designed to suggest anime titles similar to those chosen by users. It employs **K-means++** clustering with a custom distance function, which uses a combination of the **Manhattan** and **Dice** distance. The custom distance function assigns weighted values to each property of an anime such as its `type`, `genres`, `score` to compute the distance between two separate anime.

The frontend of the project was initially set up using [Vite.js](https://vitejs.dev/) for development purposes, but has since transitioned to utilize [Create React App](https://create-react-app.dev/), in conjunction with [React](https://react.dev/), [React Router](https://reactrouter.com/), [TailwindCSS](https://tailwindcss.com/) and [DaisyUI](https://daisyui.com/).

The backend of this project, aka the 'heart' of the project was built utilizing [Tensorflow.js](https://www.tensorflow.org/js/) in combination with external libraries such as [ml-kmeans](https://github.com/mljs/kmeans), [ml-distance](https://github.com/mljs/distance), and [simple-statistics](https://github.com/simple-statistics/simple-statistics). Additionally, to perform TF-IDF analysis on anime synopses, [natural](https://github.com/NaturalNode/natural) was used alongside [remove-stopwords](https://github.com/WorldBrain/remove-stopwords), [word-list](https://github.com/sindresorhus/word-list), and [lemmatizer](https://github.com/FinNLP/lemmatizer).

Upon combining these two parts, the project comes together in the form, that is, **Kelbrum**.

> [!IMPORTANT]
> The data used within this project was possible thanks to the following:
>
> 1. [Original Kaggle Dataset](https://www.kaggle.com/datasets/dbdmobile/myanimelist-dataset) - The anime dataset was read and processed into a custom JavaScript class known as [AnimeEntry](./recommender/models/AnimeEntry.js).
> 2. [JikanAPI](https://github.com/jikan-me/jikan-rest) - Missing information such as `pageURL`, `imageURL`, `trailerURL` and other existing properties which may have needed updates were updated by making several API requests to JikanAPI, which contains anime information obtained from [MyAnimeList](https://myanimelist.net/).
>
> All external images and text used within this app belong to their respective owners.

## 📖 Table of Contents

- [📖 Table of Contents](#-table-of-contents)
- [🌟 Features](#-features)
- [🛠️ Tech Stack](#️-tech-stack)
- [📝 Prerequisites](#-prerequisites)
- [⚡ Setup Instructions](#-setup-instructions)
- [📜 Available Scripts](#-available-scripts)
- [✨ Acknowledgments](#-acknowledgments)
- [©️ License](#️-license)

## 🌟 Features

-   The ability to search for any anime within the existing dataset via a search bar
-   A homepage featuring a hero section that encourages users to search for an anime and displays 10 anime randomly selected that meet a minimum average score, providing users with immediate recommendations
-   The ability to view all anime grouped together based on properties such as `genres`, `studios`, `seasons`, etc
-   The ability to view the top 100 anime within the existing set of anime, based on average score
-   A dedicated anime details page that enables users to view detailed information about an anime and receive recommendations based on similarity
-   The ability to view 10 unique random anime recommendations and view up to 200 recommendations per anime (not all anime will have that many recommendations)
-   The ability to grow and accommodate other content types such as `manga`, `manhwa`, and `manhua`
-   The capability to prioritize anime properties based on assigned weights and adjust the recommendation algorithm at any time using the provided K-means JSON file and feature tensors

## 🛠️ Tech Stack

Backend:

-   [Node.js](https://nodejs.org/en)
-   [Tensorflow.js](https://github.com/tensorflow/tfjs)
-   [natural](https://github.com/NaturalNode/natural)
-   [simple-statistics](https://github.com/simple-statistics/simple-statistics)
-   [ml-distance](https://github.com/mljs/distance)
-   [ml-kmeans](https://github.com/mljs/kmeans)

Frontend:

-   [React](https://react.dev/)
-   [React Router](https://reactrouter.com/)
-   [DaisyUI](https://daisyui.com/)
-   [TailwindCSS](https://tailwindcss.com/)

Hosting:

-   [Firebase](https://firebase.google.com/)
    -   Analytics using [Google Analytics](https://marketingplatform.google.com/about/analytics/) (Based on recommended Firebase config)

Documentation:

-   Docs are built using [Docusaurus](https://docusaurus.io/)
    -   Search functionality provided by: [docusaurus-lunr-search](https://github.com/praveenn77/docusaurus-lunr-search)
    -   Analytics using [Google Analytics](https://marketingplatform.google.com/about/analytics/)
-   Documentation site hosted via [GitHub Pages](https://pages.github.com/)

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
npm start
```

2. Build the project files and optimize for production.

```bash
npm run build
```

3. Lint all files and check if there are any issues, with [ESLint](https://eslint.org/).

```bash
npm run lint
```

4. Fix all ESLint issues then format the files with [Prettier](https://prettier.io/).

```bash
npm run prettier
```

## ✨ Acknowledgments

-   [csv-parse](https://github.com/adaltas/node-csv)
-   [PapaParse](https://www.papaparse.com/)
-   [lodash](https://github.com/lodash/lodash)
-   [lemmatizer](https://github.com/FinNLP/lemmatizer)
-   [MiniSearch](https://github.com/lucaong/minisearch)
-   [React Infinite Scroller](https://github.com/danbovey/react-infinite-scroller)
-   [react-slick](https://github.com/akiran/react-slick)
-   [remove-stopwords](https://github.com/WorldBrain/remove-stopwords)
-   [slick-carousel](https://github.com/kenwheeler/slick/)
-   [tailwind-scrollbar](https://github.com/adoxography/tailwind-scrollbar)
-   [word-list](https://github.com/sindresorhus/word-list)
-   [SimpleIcons](https://simpleicons.org/)
-   [Tensorflow.js](https://www.tensorflow.org/js)
-   [Tensorflow.js Documentation](https://js.tensorflow.org/api/latest/)
-   [Machine Learning Crash Course by Google](https://developers.google.com/machine-learning/crash-course/)
    -   [Clustering Algorithms](https://developers.google.com/machine-learning/clustering/clustering-algorithms)
    -   [Normalization](https://developers.google.com/machine-learning/data-prep/transform/normalization)
    -   [Machine Learning Glossary](https://developers.google.com/machine-learning/glossary)
    -   [Transforming Categorical Data](https://developers.google.com/machine-learning/data-prep/transform/transform-categorical)
-   [Firebase](https://firebase.google.com/)
-   [Docusaurus](https://docusaurus.io/)
-   [GitHub Pages](https://pages.github.com/)
-   [Shields Badges](https://github.com/badges/shields)
-   [regex101](https://regex101.com/)
-   [Favicon Generator](https://favicon.io/favicon-generator/)

Various web articles for research and learning, such as:

-   [17 types of similarity and dissimilarity measures used in data science](https://towardsdatascience.com/17-types-of-similarity-and-dissimilarity-measures-used-in-data-science-3eb914d2681)
-   [A Guide to Content-Based Filtering In Recommender Systems](https://www.turing.com/kb/content-based-filtering-in-recommender-systems)
-   [Gower's Distance](https://medium.com/analytics-vidhya/gowers-distance-899f9c4bd553)
-   [Introduction to similarity metrics](https://medium.com/analytics-vidhya/introduction-to-similarity-metrics-a882361c9be4)
-   [Types of recommendation systems & their use cases](https://medium.com/mlearning-ai/what-are-the-types-of-recommendation-systems-3487cbafa7c9)
-   [Supervised vs. Unsupervised Learning: What’s the Difference?](https://www.ibm.com/blog/supervised-vs-unsupervised-learning/)
-   [What is unsupervised learning?](https://www.ibm.com/topics/unsupervised-learning)

Additionally, this project would not be possible without the following sources of information:

-   [Original Kaggle Dataset](https://www.kaggle.com/datasets/dbdmobile/myanimelist-dataset)
-   [JikanAPI](https://github.com/jikan-me/jikan-rest)
-   [MyAnimeList](https://myanimelist.net/)

All external images and text used within this app belong to their respective owners.

## ©️ License

The contents of this repository are licensed under the terms and conditions of the [MIT](https://choosealicense.com/licenses/mit/) license.

[MIT](./LICENSE) © 2024-present Visakan Kirubakaran.
