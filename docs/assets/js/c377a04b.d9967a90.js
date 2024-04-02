'use strict';
(self.webpackChunkkelbrum_docs = self.webpackChunkkelbrum_docs || []).push([
    [742],
    {
        4838: (e, s, t) => {
            t.r(s),
                t.d(s, {
                    assets: () => c,
                    contentTitle: () => a,
                    default: () => d,
                    frontMatter: () => n,
                    metadata: () => o,
                    toc: () => l,
                });
            var i = t(4848),
                r = t(8453);
            const n = { title: '\ud83d\udcd6 Introduction' },
                a = void 0,
                o = {
                    id: 'index',
                    title: '\ud83d\udcd6 Introduction',
                    description:
                        '<img src="https://wakatime.com/badge/user/5e62f99d-3a1e-4fd2-8f37-77919d626a67/project/018e1a22-364b-4b87-a797-b55b694a169d.svg"',
                    source: '@site/docs/index.md',
                    sourceDirName: '.',
                    slug: '/',
                    permalink: '/kelbrum/',
                    draft: !1,
                    unlisted: !1,
                    tags: [],
                    version: 'current',
                    frontMatter: { title: '\ud83d\udcd6 Introduction' },
                    sidebar: 'docs',
                    next: { title: '\ud83d\udcdd Prerequisites', permalink: '/kelbrum/prerequisites' },
                },
                c = {},
                l = [
                    { value: 'Overview', id: 'overview', level: 2 },
                    { value: '\xa9\ufe0f License', id: '\ufe0f-license', level: 2 },
                ];
            function h(e) {
                const s = {
                    a: 'a',
                    admonition: 'admonition',
                    code: 'code',
                    h2: 'h2',
                    hr: 'hr',
                    li: 'li',
                    ol: 'ol',
                    p: 'p',
                    strong: 'strong',
                    ...(0, r.R)(),
                    ...e.components,
                };
                return (0, i.jsxs)(i.Fragment, {
                    children: [
                        (0, i.jsx)('div', {
                            align: 'center',
                            id: 'logo',
                            children: (0, i.jsx)('img', { src: 'logo.png' }),
                        }),
                        '\n',
                        (0, i.jsxs)('p', {
                            align: 'center',
                            id: 'badges',
                            children: [
                                (0, i.jsx)('a', {
                                    href: 'https://vikiru.github.io/kelbrum/',
                                    children: (0, i.jsx)('img', {
                                        src: 'https://img.shields.io/badge/documentation-docs-orange',
                                        alt: 'Documentation',
                                    }),
                                }),
                                (0, i.jsx)('a', {
                                    href: 'https://kelbrum-v1.web.app',
                                    children: (0, i.jsx)('img', {
                                        src: 'https://img.shields.io/badge/Web-live%20site-blue',
                                        alt: 'Kelbrum live site hosted via Firebase',
                                    }),
                                }),
                                (0, i.jsx)('a', {
                                    href: 'https://wakatime.com/@vikiru/projects/umhctwxtly',
                                    children: (0, i.jsx)('img', {
                                        src: 'https://wakatime.com/badge/user/5e62f99d-3a1e-4fd2-8f37-77919d626a67/project/018e1a22-364b-4b87-a797-b55b694a169d.svg',
                                        alt: 'Wakatime Coding Stats for Kelbrum',
                                    }),
                                }),
                                (0, i.jsx)('a', {
                                    href: 'https://github.com/vikiru/kelbrum/blob/main/LICENSE',
                                    children: (0, i.jsx)('img', {
                                        src: 'https://img.shields.io/badge/license-MIT-aqua',
                                        alt: 'MIT License Badge',
                                    }),
                                }),
                                (0, i.jsx)('a', {
                                    href: 'https://github.com/prettier/prettier',
                                    children: (0, i.jsx)('img', {
                                        src: 'https://img.shields.io/badge/code_style-prettier-ff69b4.svg?style=flat-square',
                                        alt: 'Code Style - Prettier',
                                    }),
                                }),
                                (0, i.jsx)('br', {}),
                                (0, i.jsx)('a', {
                                    href: 'https://github.com/vikiru/kelbrum/releases',
                                    children: (0, i.jsx)('img', {
                                        src: 'https://img.shields.io/github/v/release/vikiru/kelbrum',
                                        alt: 'Release',
                                    }),
                                }),
                                (0, i.jsx)('a', {
                                    href: 'https://github.com/vikiru/kelbrum/issues?q=is%3Aissue+is%3Aclosed',
                                    children: (0, i.jsx)('img', {
                                        src: 'https://img.shields.io/github/issues-closed/vikiru/kelbrum',
                                        alt: 'Closed Issues',
                                    }),
                                }),
                                (0, i.jsx)('a', {
                                    href: 'https://github.com/vikiru/kelbrum/pulls?q=is%3Apr+is%3Aclosed',
                                    children: (0, i.jsx)('img', {
                                        src: 'https://img.shields.io/github/issues-pr-closed/vikiru/kelbrum?label=closed%20prs',
                                        alt: 'Closed PRs',
                                    }),
                                }),
                                (0, i.jsx)('a', {
                                    href: 'https://github.com/vikiru/kelbrum/actions/workflows/lint.yml',
                                    children: (0, i.jsx)('img', {
                                        src: 'https://github.com/vikiru/kelbrum/actions/workflows/lint.yml/badge.svg',
                                        alt: 'GitHub Lint Action Workflow Status',
                                    }),
                                }),
                            ],
                        }),
                        '\n',
                        (0, i.jsx)(s.hr, {}),
                        '\n',
                        (0, i.jsx)(s.h2, { id: 'overview', children: 'Overview' }),
                        '\n',
                        (0, i.jsxs)(s.p, {
                            children: [
                                (0, i.jsx)(s.strong, { children: 'Kelbrum' }),
                                ' is an anime recommendation system designed to suggest anime titles similar to those chosen by users. It employs ',
                                (0, i.jsx)(s.strong, { children: 'K-means++' }),
                                ' clustering with a custom distance function, which uses a combination of the ',
                                (0, i.jsx)(s.strong, { children: 'Manhattan' }),
                                ' and ',
                                (0, i.jsx)(s.strong, { children: 'Dice' }),
                                ' distance. The custom distance function assigns weighted values to each property of an anime such as its ',
                                (0, i.jsx)(s.code, { children: 'type' }),
                                ', ',
                                (0, i.jsx)(s.code, { children: 'genres' }),
                                ', ',
                                (0, i.jsx)(s.code, { children: 'score' }),
                                ' to compute the distance between two separate anime.',
                            ],
                        }),
                        '\n',
                        (0, i.jsxs)(s.p, {
                            children: [
                                'The frontend of the project was initially set up using ',
                                (0, i.jsx)(s.a, { href: 'https://vitejs.dev/', children: 'Vite.js' }),
                                ' for development purposes, but has since transitioned to utilize ',
                                (0, i.jsx)(s.a, {
                                    href: 'https://create-react-app.dev/',
                                    children: 'Create React App',
                                }),
                                ', in conjunction with ',
                                (0, i.jsx)(s.a, { href: 'https://react.dev/', children: 'React' }),
                                ', ',
                                (0, i.jsx)(s.a, { href: 'https://reactrouter.com/', children: 'React Router' }),
                                ', ',
                                (0, i.jsx)(s.a, { href: 'https://tailwindcss.com/', children: 'TailwindCSS' }),
                                ' and ',
                                (0, i.jsx)(s.a, { href: 'https://daisyui.com/', children: 'DaisyUI' }),
                                '.',
                            ],
                        }),
                        '\n',
                        (0, i.jsxs)(s.p, {
                            children: [
                                "The backend of this project, aka the 'heart' of the project was built utilizing ",
                                (0, i.jsx)(s.a, { href: 'https://www.tensorflow.org/js/', children: 'Tensorflow.js' }),
                                ' in combination with external libraries such as ',
                                (0, i.jsx)(s.a, { href: 'https://github.com/mljs/kmeans', children: 'ml-kmeans' }),
                                ', ',
                                (0, i.jsx)(s.a, { href: 'https://github.com/mljs/distance', children: 'ml-distance' }),
                                ', and ',
                                (0, i.jsx)(s.a, {
                                    href: 'https://github.com/simple-statistics/simple-statistics',
                                    children: 'simple-statistics',
                                }),
                                '. Additionally, to perform TF-IDF analysis on anime synopses, ',
                                (0, i.jsx)(s.a, {
                                    href: 'https://github.com/NaturalNode/natural',
                                    children: 'natural',
                                }),
                                ' was used alongside ',
                                (0, i.jsx)(s.a, {
                                    href: 'https://github.com/WorldBrain/remove-stopwords',
                                    children: 'remove-stopwords',
                                }),
                                ', ',
                                (0, i.jsx)(s.a, {
                                    href: 'https://github.com/sindresorhus/word-list',
                                    children: 'word-list',
                                }),
                                ', and ',
                                (0, i.jsx)(s.a, {
                                    href: 'https://github.com/FinNLP/lemmatizer',
                                    children: 'lemmatizer',
                                }),
                                '.',
                            ],
                        }),
                        '\n',
                        (0, i.jsxs)(s.p, {
                            children: [
                                'Upon combining these two parts, the project comes together in the form, that is, ',
                                (0, i.jsx)(s.strong, { children: 'Kelbrum' }),
                                '.',
                            ],
                        }),
                        '\n',
                        (0, i.jsxs)(s.admonition, {
                            type: 'info',
                            children: [
                                (0, i.jsx)(s.p, {
                                    children:
                                        'This project was made possible thanks to the following sources of anime image and text information:',
                                }),
                                (0, i.jsxs)(s.ol, {
                                    children: [
                                        '\n',
                                        (0, i.jsxs)(s.li, {
                                            children: [
                                                (0, i.jsx)(s.a, {
                                                    href: 'https://www.kaggle.com/datasets/dbdmobile/myanimelist-dataset',
                                                    children: 'Original Kaggle Dataset',
                                                }),
                                                ' - The anime dataset was read and proccessed into a custom JavaScript class known as ',
                                                (0, i.jsx)(s.a, {
                                                    href: 'https://github.com/vikiru/kelbrum/blob/main/src/recommender/models/AnimeEntry.js',
                                                    children: 'AnimeEntry',
                                                }),
                                                '.',
                                            ],
                                        }),
                                        '\n',
                                        (0, i.jsxs)(s.li, {
                                            children: [
                                                (0, i.jsx)(s.a, {
                                                    href: 'https://github.com/jikan-me/jikan-rest',
                                                    children: 'JikanAPI',
                                                }),
                                                ' - Missing information such as ',
                                                (0, i.jsx)(s.code, { children: 'pageURL' }),
                                                ', ',
                                                (0, i.jsx)(s.code, { children: 'imageURL' }),
                                                ', ',
                                                (0, i.jsx)(s.code, { children: 'trailerURL' }),
                                                ' and other existing properties which may have needed updates were updated by making several API requests to JikanAPI. JikanAPI contains anime information obtained from ',
                                                (0, i.jsx)(s.a, {
                                                    href: 'https://myanimelist.net/',
                                                    children: 'MyAnimeList',
                                                }),
                                                '.',
                                            ],
                                        }),
                                        '\n',
                                    ],
                                }),
                                (0, i.jsx)(s.p, {
                                    children:
                                        'All external images and text used within this app belong to their respective owners.',
                                }),
                            ],
                        }),
                        '\n',
                        (0, i.jsx)(s.h2, { id: '\ufe0f-license', children: '\xa9\ufe0f License' }),
                        '\n',
                        (0, i.jsxs)(s.p, {
                            children: [
                                'The contents of this repository are licensed under the terms and conditions of the ',
                                (0, i.jsx)(s.a, { href: 'https://choosealicense.com/licenses/mit/', children: 'MIT' }),
                                ' license.',
                            ],
                        }),
                        '\n',
                        (0, i.jsxs)(s.p, {
                            children: [
                                (0, i.jsx)(s.a, {
                                    href: 'https://github.com/vikiru/kelbrum/LICENSE.md',
                                    children: 'MIT',
                                }),
                                ' \xa9 2024-present Visakan Kirubakaran.',
                            ],
                        }),
                    ],
                });
            }
            function d(e = {}) {
                const { wrapper: s } = { ...(0, r.R)(), ...e.components };
                return s ? (0, i.jsx)(s, { ...e, children: (0, i.jsx)(h, { ...e }) }) : h(e);
            }
        },
        8453: (e, s, t) => {
            t.d(s, { R: () => a, x: () => o });
            var i = t(6540);
            const r = {},
                n = i.createContext(r);
            function a(e) {
                const s = i.useContext(n);
                return i.useMemo(
                    function () {
                        return 'function' == typeof e ? e(s) : { ...s, ...e };
                    },
                    [s, e],
                );
            }
            function o(e) {
                let s;
                return (
                    (s = e.disableParentContext
                        ? 'function' == typeof e.components
                            ? e.components(r)
                            : e.components || r
                        : a(e.components)),
                    i.createElement(n.Provider, { value: s }, e.children)
                );
            }
        },
    },
]);
