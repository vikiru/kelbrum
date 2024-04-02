'use strict';
(self.webpackChunkkelbrum_docs = self.webpackChunkkelbrum_docs || []).push([
    [640],
    {
        3225: (e, t, n) => {
            n.r(t),
                n.d(t, {
                    assets: () => l,
                    contentTitle: () => r,
                    default: () => h,
                    frontMatter: () => a,
                    metadata: () => o,
                    toc: () => c,
                });
            var i = n(4848),
                s = n(8453);
            const a = { title: 'Data Clustering with K-means' },
                r = void 0,
                o = {
                    id: 'kmeans',
                    title: 'Data Clustering with K-means',
                    description: 'Data Clustering with K-means',
                    source: '@site/docs/kmeans.md',
                    sourceDirName: '.',
                    slug: '/kmeans',
                    permalink: '/kelbrum/kmeans',
                    draft: !1,
                    unlisted: !1,
                    tags: [],
                    version: 'current',
                    frontMatter: { title: 'Data Clustering with K-means' },
                    sidebar: 'docs',
                    previous: { title: '\ud83d\udccf Normalizing Data', permalink: '/kelbrum/normalize' },
                    next: { title: '\u2728 Acknowledgments', permalink: '/kelbrum/acknowledgments' },
                },
                l = {},
                c = [
                    { value: 'Data Clustering with K-means', id: 'data-clustering-with-k-means', level: 2 },
                    { value: 'Identifying Clustering Algorithms', id: 'identifying-clustering-algorithms', level: 3 },
                    { value: 'Choosing the Right Tools', id: 'choosing-the-right-tools', level: 3 },
                    { value: 'Understanding Distance Functions', id: 'understanding-distance-functions', level: 3 },
                    {
                        value: 'Evaluating Clustering Effectiveness',
                        id: 'evaluating-clustering-effectiveness',
                        level: 3,
                    },
                    {
                        value: 'Best Distance Functions for the Dataset',
                        id: 'best-distance-functions-for-the-dataset',
                        level: 3,
                    },
                    { value: 'Customizing the Distance Function', id: 'customizing-the-distance-function', level: 3 },
                    { value: 'Future Experimentation', id: 'future-experimentation', level: 3 },
                ];
            function d(e) {
                const t = {
                    a: 'a',
                    code: 'code',
                    h2: 'h2',
                    h3: 'h3',
                    li: 'li',
                    p: 'p',
                    strong: 'strong',
                    ul: 'ul',
                    ...(0, s.R)(),
                    ...e.components,
                };
                return (0, i.jsxs)(i.Fragment, {
                    children: [
                        (0, i.jsx)(t.h2, {
                            id: 'data-clustering-with-k-means',
                            children: 'Data Clustering with K-means',
                        }),
                        '\n',
                        (0, i.jsx)(t.h3, {
                            id: 'identifying-clustering-algorithms',
                            children: 'Identifying Clustering Algorithms',
                        }),
                        '\n',
                        (0, i.jsxs)(t.p, {
                            children: [
                                'Once the data was ',
                                (0, i.jsx)(t.a, { href: '/normalize', children: 'normalized' }),
                                ', the next step was to figure out how to group the data based on their similarity. Upon researching this topic, I found out that there were several algorithms to achieve this such as:',
                            ],
                        }),
                        '\n',
                        (0, i.jsxs)(t.ul, {
                            children: [
                                '\n',
                                (0, i.jsx)(t.li, {
                                    children: (0, i.jsx)(t.strong, { children: 'K-means clustering' }),
                                }),
                                '\n',
                                (0, i.jsx)(t.li, {
                                    children: (0, i.jsx)(t.strong, { children: 'K-mediods clustering' }),
                                }),
                                '\n',
                                (0, i.jsx)(t.li, {
                                    children: (0, i.jsx)(t.strong, { children: 'K-nearest neighbors' }),
                                }),
                                '\n',
                                (0, i.jsx)(t.li, {
                                    children: (0, i.jsx)(t.strong, { children: 'Hierarchal clustering' }),
                                }),
                                '\n',
                                (0, i.jsx)(t.li, { children: (0, i.jsx)(t.strong, { children: 'DBSCAN' }) }),
                                '\n',
                            ],
                        }),
                        '\n',
                        (0, i.jsx)(t.p, {
                            children:
                                'There were several other algorithms as well, however, I decided to use K-means clustering as I felt it was easier to understand and applicable for my use case.',
                        }),
                        '\n',
                        (0, i.jsx)(t.h3, { id: 'choosing-the-right-tools', children: 'Choosing the Right Tools' }),
                        '\n',
                        (0, i.jsxs)(t.p, {
                            children: [
                                'To cluster the data, several k-means clustering npm packages were looked at and finally, I finalized on using ',
                                (0, i.jsx)(t.a, { href: 'https://github.com/mljs/kmeans', children: 'ml-kmeans' }),
                                ' combining it with ',
                                (0, i.jsx)(t.a, { href: 'https://github.com/mljs/distance', children: 'ml-distance' }),
                                ' and ',
                                (0, i.jsx)(t.a, {
                                    href: 'https://github.com/simple-statistics/simple-statistics',
                                    children: 'simple-statistics',
                                }),
                                '. Addtionally, to perform TF-IDF analysis on anime synopses, ',
                                (0, i.jsx)(t.a, {
                                    href: 'https://github.com/NaturalNode/natural',
                                    children: 'natural',
                                }),
                                ' was used alongside ',
                                (0, i.jsx)(t.a, {
                                    href: 'https://github.com/WorldBrain/remove-stopwords',
                                    children: 'remove-stopwords',
                                }),
                                ', ',
                                (0, i.jsx)(t.a, {
                                    href: 'https://github.com/sindresorhus/word-list',
                                    children: 'word-list',
                                }),
                                ', and ',
                                (0, i.jsx)(t.a, {
                                    href: 'https://github.com/FinNLP/lemmatizer',
                                    children: 'lemmatizer',
                                }),
                                '.',
                            ],
                        }),
                        '\n',
                        (0, i.jsxs)(t.p, {
                            children: [
                                (0, i.jsx)(t.strong, { children: 'ml-distance' }),
                                ' offered various distance and similarity calculations and ',
                                (0, i.jsx)(t.strong, { children: 'ml-kmeans' }),
                                ' allowed for the use of custom distance functions so this worked out really well for me.',
                            ],
                        }),
                        '\n',
                        (0, i.jsx)(t.h3, {
                            id: 'understanding-distance-functions',
                            children: 'Understanding Distance Functions',
                        }),
                        '\n',
                        (0, i.jsxs)(t.p, {
                            children: [
                                'I tried to learn about some common distance functions used to cluster data such as euclidean, cosine, squared euclidean, manhattan, hamming, etc and through trial and error I experimented with all of the functions provided by ',
                                (0, i.jsx)(t.strong, { children: 'ml-distance' }),
                                '. Through my experiments, which involved applying various normalization techniques to anime properties and experimenting with different feature combinations, I discovered that the ',
                                (0, i.jsx)(t.strong, { children: 'curse of dimensionality' }),
                                ' significantly impacted my results as the number of features in my feature tensors increased.',
                            ],
                        }),
                        '\n',
                        (0, i.jsxs)(t.p, {
                            children: [
                                'To combat the ',
                                (0, i.jsx)(t.strong, { children: 'curse of dimensionality' }),
                                ', I decided to use various normalization techniques, combinations of features and different weightings to these features. Additionally, I did try to reduce the number of features I used as originally, I wanted to see how the effect of all features together would be and it proved to be computationally expensive to compute for higher k values and harder to cluster effectively.',
                            ],
                        }),
                        '\n',
                        (0, i.jsx)(t.h3, {
                            id: 'evaluating-clustering-effectiveness',
                            children: 'Evaluating Clustering Effectiveness',
                        }),
                        '\n',
                        (0, i.jsx)(t.p, {
                            children:
                                'I was able to assess the effectiveness of clustering by identifying several metrics that indicate the efficiency of clustering, including:',
                        }),
                        '\n',
                        (0, i.jsxs)(t.ul, {
                            children: [
                                '\n',
                                (0, i.jsx)(t.li, {
                                    children: (0, i.jsx)(t.strong, {
                                        children: 'Within Cluster Sum of Squares (WCSS)',
                                    }),
                                }),
                                '\n',
                                (0, i.jsx)(t.li, { children: (0, i.jsx)(t.strong, { children: 'Elbow Method' }) }),
                                '\n',
                                (0, i.jsx)(t.li, { children: (0, i.jsx)(t.strong, { children: 'Silhouette Score' }) }),
                                '\n',
                            ],
                        }),
                        '\n',
                        (0, i.jsxs)(t.p, {
                            children: [
                                'While other metrics were available, my primary focus was on the Within Cluster Sum of Squares (WCSS) and the silhouette score when feasible. Fortunately, calculating the WCSS was straightforward with the assistance of ',
                                (0, i.jsx)(t.strong, { children: 'ml-kmeans' }),
                                ', and the silhouette score was computed using ',
                                (0, i.jsx)(t.strong, { children: 'simple-statistics' }),
                                '. However, the computation of the silhouette score became increasingly computationally intensive as the value of k increased, due to the large size of the feature tensors, leading me to prioritize the WCSS. My objective was to achieve the lowest WCSS and the highest silhouette score possible.',
                            ],
                        }),
                        '\n',
                        (0, i.jsx)(t.h3, {
                            id: 'best-distance-functions-for-the-dataset',
                            children: 'Best Distance Functions for the Dataset',
                        }),
                        '\n',
                        (0, i.jsx)(t.p, {
                            children:
                                'From my experiments, I learned that given my data set, the following functions worked out the best:',
                        }),
                        '\n',
                        (0, i.jsxs)(t.ul, {
                            children: [
                                '\n',
                                (0, i.jsx)(t.li, {
                                    children: (0, i.jsx)(t.strong, { children: 'Manhattan Distance' }),
                                }),
                                '\n',
                                (0, i.jsx)(t.li, { children: (0, i.jsx)(t.strong, { children: 'Dice Similarity' }) }),
                                '\n',
                                (0, i.jsx)(t.li, { children: (0, i.jsx)(t.strong, { children: 'Jaccard Index' }) }),
                                '\n',
                                (0, i.jsx)(t.li, { children: (0, i.jsx)(t.strong, { children: "Gower's Distance" }) }),
                                '\n',
                                (0, i.jsx)(t.li, { children: (0, i.jsx)(t.strong, { children: 'Cosine Similarity' }) }),
                                '\n',
                                (0, i.jsx)(t.li, {
                                    children: (0, i.jsx)(t.strong, { children: 'S\xf8rensen\u2013Dice coefficient' }),
                                }),
                                '\n',
                                (0, i.jsx)(t.li, { children: (0, i.jsx)(t.strong, { children: 'Tanimoto Index' }) }),
                                '\n',
                            ],
                        }),
                        '\n',
                        (0, i.jsx)(t.h3, {
                            id: 'customizing-the-distance-function',
                            children: 'Customizing the Distance Function',
                        }),
                        '\n',
                        (0, i.jsx)(t.p, {
                            children:
                                "After additional experimentation, I attempted to develop a custom distance function by employing varying weights and combinations of distance measures for both categorical and numerical attributes. Initially, cosine similarity was employed, as it proved effective. After cosine similarity, I ended up using gower's distance and that seemed to work out well purely based on the wcss values however, I learned later that this was due to the total number of values as the gower distance performed poorly as the number of values in the concatenated tensors for each anime increased, especially due to the amount of binary vectors.",
                        }),
                        '\n',
                        (0, i.jsx)(t.p, {
                            children:
                                'To develop the current weighted distance function, I compared anime that were known to be similar, utilizing various distance measures with both the concatenated tensors as a whole and each individual feature tensor. This approach helped identify which properties most significantly increased the distance between each anime. At the same time, I was experimenting with different normalization techniques and feature tensor combinations. Eventually, I added weights which required a considerable amount of trial and error to achieve the current satisfactory level of recommendations as I had to experiment with different weightings for each property and different distance measures for each.',
                        }),
                        '\n',
                        (0, i.jsxs)(t.p, {
                            children: [
                                'In the end, the manhattan distance was used for properties such as ',
                                (0, i.jsx)(t.code, { children: 'type' }),
                                ', ',
                                (0, i.jsx)(t.code, { children: 'rating' }),
                                ', and ',
                                (0, i.jsx)(t.code, { children: 'demographics' }),
                                ' where there was a numerical value and a need to seperate anime such as anime of type ',
                                (0, i.jsx)(t.code, { children: 'TV' }),
                                ' vs. ',
                                (0, i.jsx)(t.code, { children: 'Movie' }),
                                '. The dice distance was used for all other properties such as ',
                                (0, i.jsx)(t.code, { children: 'genres' }),
                                ', ',
                                (0, i.jsx)(t.code, { children: 'themes' }),
                                ', ',
                                (0, i.jsx)(t.code, { children: 'synopsis' }),
                                ', etc.',
                            ],
                        }),
                        '\n',
                        (0, i.jsx)(t.h3, { id: 'future-experimentation', children: 'Future Experimentation' }),
                        '\n',
                        (0, i.jsxs)(t.p, {
                            children: [
                                'The K-means model currently uses a low k-value, ',
                                (0, i.jsx)(t.code, { children: 'k = 10' }),
                                " which means that there are only 10 clusters and given the dataset size, that amounts to a significant amount of anime per cluster. Further experimentation is required to investigate larger k-values, which can better balance the system's objectives and enhance the quality of recommendations. Moreover, the weights applied and the properties contain potential for further enhancement. Ideally, aiming for a larger number of clusters would enable a more accurate representation of the unique features of each anime grouping.",
                            ],
                        }),
                    ],
                });
            }
            function h(e = {}) {
                const { wrapper: t } = { ...(0, s.R)(), ...e.components };
                return t ? (0, i.jsx)(t, { ...e, children: (0, i.jsx)(d, { ...e }) }) : d(e);
            }
        },
        8453: (e, t, n) => {
            n.d(t, { R: () => r, x: () => o });
            var i = n(6540);
            const s = {},
                a = i.createContext(s);
            function r(e) {
                const t = i.useContext(a);
                return i.useMemo(
                    function () {
                        return 'function' == typeof e ? e(t) : { ...t, ...e };
                    },
                    [t, e],
                );
            }
            function o(e) {
                let t;
                return (
                    (t = e.disableParentContext
                        ? 'function' == typeof e.components
                            ? e.components(s)
                            : e.components || s
                        : r(e.components)),
                    i.createElement(a.Provider, { value: t }, e.children)
                );
            }
        },
    },
]);
