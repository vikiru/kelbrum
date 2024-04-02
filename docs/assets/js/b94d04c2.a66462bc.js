'use strict';
(self.webpackChunkkelbrum_docs = self.webpackChunkkelbrum_docs || []).push([
    [99],
    {
        113: (e, n, i) => {
            i.r(n),
                i.d(n, {
                    assets: () => c,
                    contentTitle: () => o,
                    default: () => h,
                    frontMatter: () => s,
                    metadata: () => a,
                    toc: () => d,
                });
            var t = i(4848),
                r = i(8453);
            const s = { title: '\ud83d\udccf Normalizing Data' },
                o = void 0,
                a = {
                    id: 'normalize',
                    title: '\ud83d\udccf Normalizing Data',
                    description: '\ud83d\udccf Normalizing Data for K-means clustering',
                    source: '@site/docs/normalize.md',
                    sourceDirName: '.',
                    slug: '/normalize',
                    permalink: '/kelbrum/normalize',
                    draft: !1,
                    unlisted: !1,
                    tags: [],
                    version: 'current',
                    frontMatter: { title: '\ud83d\udccf Normalizing Data' },
                    sidebar: 'docs',
                    previous: { title: '\ud83e\udde9 Model Overview', permalink: '/kelbrum/model' },
                    next: { title: 'Data Clustering with K-means', permalink: '/kelbrum/kmeans' },
                },
                c = {},
                d = [
                    {
                        value: '\ud83d\udccf Normalizing Data for K-means clustering',
                        id: '-normalizing-data-for-k-means-clustering',
                        level: 2,
                    },
                ];
            function l(e) {
                const n = {
                    a: 'a',
                    code: 'code',
                    h2: 'h2',
                    li: 'li',
                    p: 'p',
                    strong: 'strong',
                    ul: 'ul',
                    ...(0, r.R)(),
                    ...e.components,
                };
                return (0, t.jsxs)(t.Fragment, {
                    children: [
                        (0, t.jsx)(n.h2, {
                            id: '-normalizing-data-for-k-means-clustering',
                            children: '\ud83d\udccf Normalizing Data for K-means clustering',
                        }),
                        '\n',
                        (0, t.jsxs)(n.p, {
                            children: [
                                'Given the strucure of an ',
                                (0, t.jsx)(n.a, { href: '/model', children: 'AnimeEntry' }),
                                ' model, it can be seen that there is a variety of data types present. There is data that can be considered as ',
                                (0, t.jsx)(n.code, { children: 'categorical' }),
                                ', ',
                                (0, t.jsx)(n.code, { children: 'ordinal' }),
                                ', and ',
                                (0, t.jsx)(n.code, { children: 'numerical' }),
                                '.',
                            ],
                        }),
                        '\n',
                        (0, t.jsx)(n.p, {
                            children:
                                'To handle these various data types and ensure that K-means clustering was possible, there was a need to normalize the existing data. Various normalization techniques were implemented and after trial and error, the following were used in the current model:',
                        }),
                        '\n',
                        (0, t.jsxs)(n.ul, {
                            children: [
                                '\n',
                                (0, t.jsxs)(n.li, {
                                    children: [
                                        (0, t.jsx)(n.strong, { children: 'Ordinal Encoding' }),
                                        ' For anime properties such as ',
                                        (0, t.jsx)(n.code, { children: 'type' }),
                                        ', ',
                                        (0, t.jsx)(n.code, { children: 'rating' }),
                                        ', and ',
                                        (0, t.jsx)(n.code, { children: 'demographics' }),
                                        ', originally I was using multi-hot encoding however, I noticed that just the presence/absence of a property was not sufficient as the distance between anime was key. For example, I wanted anime of type ',
                                        (0, t.jsx)(n.code, { children: 'TV' }),
                                        ' and ',
                                        (0, t.jsx)(n.code, { children: 'ONA' }),
                                        ' to be closer in distance compared to ',
                                        (0, t.jsx)(n.code, { children: 'TV' }),
                                        ' and ',
                                        (0, t.jsx)(n.code, { children: 'Movie' }),
                                        '.  To accomplish this, I chose to assign distinct values to each unique value within each of these properties, leveraging my understanding of how related values are associated with each other',
                                    ],
                                }),
                                '\n',
                                (0, t.jsxs)(n.li, {
                                    children: [
                                        (0, t.jsx)(n.strong, { children: 'Multi-Hot Encoding' }),
                                        ': For anime properties such as ',
                                        (0, t.jsx)(n.code, { children: 'genres' }),
                                        ', ',
                                        (0, t.jsx)(n.code, { children: 'demographics' }),
                                        ', ',
                                        (0, t.jsx)(n.code, { children: 'source' }),
                                        ", etc, this was normalized into a binary vector filled with 1's and 0's, indicating the presence or absence of a unique value",
                                    ],
                                }),
                                '\n',
                                (0, t.jsxs)(n.li, {
                                    children: [
                                        (0, t.jsx)(n.strong, { children: 'Min-Max Scaling' }),
                                        ': For anime properties such as ',
                                        (0, t.jsx)(n.code, { children: 'score' }),
                                        ' and ',
                                        (0, t.jsx)(n.code, { children: 'durationMinutes' }),
                                        ', the data was normalized by determining the minimum and maximum values of each property and utilizing the following formula: ',
                                        (0, t.jsx)(n.code, { children: '(value - min) / (max - min)' }),
                                        '**',
                                    ],
                                }),
                                '\n',
                                (0, t.jsxs)(n.li, {
                                    children: [
                                        (0, t.jsx)(n.strong, { children: 'Robust Scaling' }),
                                        ': This method could be applied to numerical attributes like ',
                                        (0, t.jsx)(n.code, { children: 'score' }),
                                        ' and ',
                                        (0, t.jsx)(n.code, { children: 'episodes' }),
                                        ', which would be beneficial given the presence of outliers in the dataset. These outliers include anime with scores or episode counts of 0 or "Unknown" due to insufficient information',
                                    ],
                                }),
                                '\n',
                                (0, t.jsxs)(n.li, {
                                    children: [
                                        (0, t.jsx)(n.strong, { children: 'TF-IDF' }),
                                        ': This was primarily used for the synopsis, utilzing ',
                                        (0, t.jsx)(n.strong, { children: 'natural' }),
                                        ', ',
                                        (0, t.jsx)(n.strong, { children: 'remove-stopwords' }),
                                        ', ',
                                        (0, t.jsx)(n.strong, { children: 'word-list' }),
                                        ', and ',
                                        (0, t.jsx)(n.strong, { children: 'lemmatizer' }),
                                        ' in combination, the goal was to extract top keywords from each anime synopsis and determine their frequency. In the current state, the frequency value is not used as is and instead only the presence/absence represented by a 1 or 0 is used. Originally, I planned to use the top 10 keywords from each anime and compare it with word-list, however, this did result in words I felt were irrelevant to the synopsis. To combat this, I created a list of keywords which started by using the genres, themes, demographics as a base and looking at popular anime in combination with the top 1000 keywords returned using the word-list approach and adding what I felt was relevant. There is definetly a lot of keywords that can be added and further improvements are possible.',
                                    ],
                                }),
                                '\n',
                            ],
                        }),
                        '\n',
                        (0, t.jsx)(n.p, {
                            children:
                                'Other normalization techniques were explored as well during the experimentation phase of the project, such as:',
                        }),
                        '\n',
                        (0, t.jsxs)(n.ul, {
                            children: [
                                '\n',
                                (0, t.jsxs)(n.li, {
                                    children: [
                                        (0, t.jsx)(n.strong, { children: 'Combination Encoding' }),
                                        ': This technique aims to represent each unique value with a distinct integer. For each anime, the values of its properties are combined into a single value. For instance, consider the ',
                                        (0, t.jsx)(n.code, { children: 'genres' }),
                                        ' property of a given anime with values ',
                                        (0, t.jsx)(n.code, { children: "['action', 'comedy', 'romance']" }),
                                        '. Each genre is assigned a unique integer, starting from 0 up to the total count of unique values. These integers are then summed to produce a single value for the genres property of that anime',
                                    ],
                                }),
                                '\n',
                            ],
                        }),
                        '\n',
                        (0, t.jsxs)(n.p, {
                            children: [
                                'To see more information about the normalization process, you can consider checking out the ',
                                (0, t.jsx)(n.a, {
                                    href: 'https://github.com/vikiru/kelbrum/src/recommender/utils/normalize.js',
                                    children: 'source code',
                                }),
                                ' which shows all the normalization functions and additionally, how they are incorporated to create feature tensors using Tensorflow.',
                            ],
                        }),
                    ],
                });
            }
            function h(e = {}) {
                const { wrapper: n } = { ...(0, r.R)(), ...e.components };
                return n ? (0, t.jsx)(n, { ...e, children: (0, t.jsx)(l, { ...e }) }) : l(e);
            }
        },
        8453: (e, n, i) => {
            i.d(n, { R: () => o, x: () => a });
            var t = i(6540);
            const r = {},
                s = t.createContext(r);
            function o(e) {
                const n = t.useContext(s);
                return t.useMemo(
                    function () {
                        return 'function' == typeof e ? e(n) : { ...n, ...e };
                    },
                    [n, e],
                );
            }
            function a(e) {
                let n;
                return (
                    (n = e.disableParentContext
                        ? 'function' == typeof e.components
                            ? e.components(r)
                            : e.components || r
                        : o(e.components)),
                    t.createElement(s.Provider, { value: n }, e.children)
                );
            }
        },
    },
]);
