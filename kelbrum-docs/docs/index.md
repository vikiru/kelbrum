---
title: 📖 Introduction
---

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

## Overview

**Kelbrum** is an anime recommendation system designed to suggest anime titles similar to those chosen by users. It employs **K-means++** clustering with a custom distance function, which uses a combination of the **Manhattan** and **Dice** distance. The custom distance function assigns weighted values to each property of an anime such as its `title`, `genres`, `score` to compute the distance between two separate anime.

The frontend of the project was initially set up using [Vite.js](https://vitejs.dev/) for development purposes, but has since transitioned to utilize [Create React App](https://create-react-app.dev/), in conjunction with [React](https://react.dev/), [React Router](https://reactrouter.com/), [TailwindCSS](https://tailwindcss.com/) and [DaisyUI](https://daisyui.com/).

The backend of this project, aka the 'heart' of the project was built utilizing [Tensorflow.js](https://www.tensorflow.org/js/) in combination with external libraries such as [ml-kmeans](https://github.com/mljs/kmeans), [ml-distance](https://github.com/mljs/distance), and [simple-statistics](https://github.com/simple-statistics/simple-statistics). Additionally, to perform TF-IDF analysis on anime synopses, [natural](https://github.com/NaturalNode/natural) was used alongside [remove-stopwords](https://github.com/WorldBrain/remove-stopwords), [word-list](https://github.com/sindresorhus/word-list), and [lemmatizer](https://github.com/FinNLP/lemmatizer).

Upon combining these two parts, the project comes together in the form, that is, **Kelbrum**.

:::info

This project was made possible thanks to the following sources of anime image and text information:

1.  [Original Kaggle Dataset](https://www.kaggle.com/datasets/dbdmobile/myanimelist-dataset) - The anime dataset was read and proccessed into a custom JavaScript class known as [AnimeEntry](https://github.com/vikiru/kelbrum/src/recommender/models/AnimeEntry.js).
2.  [JikanAPI](https://github.com/jikan-me/jikan-rest) - Missing information such as `pageURL`, `imageURL`, `trailerURL` and other existing properties which may have needed updates were updated by making several API requests to JikanAPI. JikanAPI contains anime information obtained from [MyAnimeList](https://myanimelist.net/).

All external images and text used within this app belong to their respective owners.

:::

## ©️ License

The contents of this repository are licensed under the terms and conditions of the [MIT](https://choosealicense.com/licenses/mit/) license.

[MIT](https://github.com/vikiru/kelbrum/LICENSE.md) © 2024-present Visakan Kirubakaran.
