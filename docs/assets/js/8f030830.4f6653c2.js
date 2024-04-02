'use strict';
(self.webpackChunkkelbrum_docs = self.webpackChunkkelbrum_docs || []).push([
    [423],
    {
        7659: (e, t, i) => {
            i.r(t),
                i.d(t, {
                    assets: () => d,
                    contentTitle: () => r,
                    default: () => c,
                    frontMatter: () => s,
                    metadata: () => o,
                    toc: () => h,
                });
            var n = i(4848),
                a = i(8453);
            const s = { title: '\ud83d\udd27 Development Overview' },
                r = void 0,
                o = {
                    id: 'development',
                    title: '\ud83d\udd27 Development Overview',
                    description: '\ud83d\udd27 Development Overview',
                    source: '@site/docs/development.md',
                    sourceDirName: '.',
                    slug: '/development',
                    permalink: '/kelbrum/development',
                    draft: !1,
                    unlisted: !1,
                    tags: [],
                    version: 'current',
                    frontMatter: { title: '\ud83d\udd27 Development Overview' },
                    sidebar: 'docs',
                    previous: { title: '\ud83d\udd25 Motivation', permalink: '/kelbrum/motivation' },
                    next: { title: '\ud83d\udee0\ufe0f Tech Stack', permalink: '/kelbrum/stack' },
                },
                d = {},
                h = [
                    { value: '\ud83d\udd27 Development Overview', id: '-development-overview', level: 2 },
                    { value: 'Finding a suitable database', id: 'finding-a-suitable-database', level: 3 },
                    { value: 'Determining how to use dataset', id: 'determining-how-to-use-dataset', level: 3 },
                    { value: 'Normalizing the Data', id: 'normalizing-the-data', level: 3 },
                    { value: 'Clustering the Data', id: 'clustering-the-data', level: 3 },
                    { value: 'Designing the UI', id: 'designing-the-ui', level: 3 },
                ];
            function l(e) {
                const t = {
                    a: 'a',
                    code: 'code',
                    h2: 'h2',
                    h3: 'h3',
                    p: 'p',
                    strong: 'strong',
                    ...(0, a.R)(),
                    ...e.components,
                };
                return (0, n.jsxs)(n.Fragment, {
                    children: [
                        (0, n.jsx)(t.h2, {
                            id: '-development-overview',
                            children: '\ud83d\udd27 Development Overview',
                        }),
                        '\n',
                        (0, n.jsx)(t.p, {
                            children:
                                'To develop a project like this, several different steps were neccessary alongside many hours of trial and error.',
                        }),
                        '\n',
                        (0, n.jsx)(t.h3, {
                            id: 'finding-a-suitable-database',
                            children: 'Finding a suitable database',
                        }),
                        '\n',
                        (0, n.jsxs)(t.p, {
                            children: [
                                'To achieve this, I browsed through Kaggle to find datasets with the information that I would need for this situation, ideally just the anime information would have been enough. I originally used this ',
                                (0, n.jsx)(t.a, {
                                    href: 'https://www.kaggle.com/datasets/nikhil1e9/myanimelist-anime-and-manga/data',
                                    children: 'dataset',
                                }),
                                ' however, I ended up transitioning to the current ',
                                (0, n.jsx)(t.a, {
                                    href: 'https://www.kaggle.com/datasets/dbdmobile/myanimelist-dataset',
                                    children: 'dataset',
                                }),
                                ' as it provided more detailed information and addtionally, I could see the license information for the dataset.',
                            ],
                        }),
                        '\n',
                        (0, n.jsx)(t.h3, {
                            id: 'determining-how-to-use-dataset',
                            children: 'Determining how to use dataset',
                        }),
                        '\n',
                        (0, n.jsxs)(t.p, {
                            children: [
                                'My first thought was to figure out how to use machine learning frameworks such as Tensorflow or PyTorch and create a model based on the dataset using those. This would have involved a similar kind of process to what I achieved in the end, normalizing the data and creating feature tensors, however, I would have needed ',
                                (0, n.jsx)(t.code, { children: 'labels' }),
                                ' to test the models ability to predict. I could have used the ',
                                (0, n.jsx)(t.code, { children: 'score' }),
                                " property of an anime however, there are several outliers in the thousands with values of 0 or 'Unknown' for various properties including ",
                                (0, n.jsx)(t.code, { children: 'score' }),
                                ' and additionally, this did not suit my use case. I later learned that what I was originally trying to achieve was something known as ',
                                (0, n.jsx)(t.strong, { children: 'supervised learning' }),
                                ' and then I learned that there was something known as ',
                                (0, n.jsx)(t.strong, { children: 'unsupervised learning' }),
                                ' which did not need labels of any kind, this seemed like what I needed.',
                            ],
                        }),
                        '\n',
                        (0, n.jsxs)(t.p, {
                            children: [
                                'From here, I had to determine the type of filtering to use within the recommendation system, I learned there were two main types, content-based and collaborative filtering followed by a hybrid approach which would combine both of the methods. Given the dataset, I did have the capability to perform both types of filtering, however, the size of the user interaction data was ',
                                (0, n.jsx)(t.code, { children: '1 GB' }),
                                ' and I did attempt to try to use it however, the issue is that there are over 200,000 users within that data and over 15,000 anime within the dataset which means utilizing this in a user-interaction matrix would have been computationally expensive. That is when I decided to just use content-based filtering.',
                            ],
                        }),
                        '\n',
                        (0, n.jsx)(t.h3, { id: 'normalizing-the-data', children: 'Normalizing the Data' }),
                        '\n',
                        (0, n.jsxs)(t.p, {
                            children: [
                                'Once I determined that I would use content-based filtering, I had to research various normalizing techniques for the various types of data that existed within my data and use this to create feature tensors through Tensorflow, further explained ',
                                (0, n.jsx)(t.a, { href: '/normalize', children: 'here' }),
                                '.',
                            ],
                        }),
                        '\n',
                        (0, n.jsx)(t.h3, { id: 'clustering-the-data', children: 'Clustering the Data' }),
                        '\n',
                        (0, n.jsxs)(t.p, {
                            children: [
                                'Since the objective of my project was to recommend anime that was similar to user-selected anime, I had to figure out a way to group anime based on their properties. This led me to research various existing clustering algorithms where I finalized on using ',
                                (0, n.jsx)(t.strong, { children: 'k-means' }),
                                ' clustering. To effectively cluster anime, I had to also determine a distance function which would be used to tell how similar two distinct anime were based on their properies, in the end, a combination of the ',
                                (0, n.jsx)(t.strong, { children: 'Manhattan' }),
                                ' and ',
                                (0, n.jsx)(t.strong, { children: 'Dice' }),
                                ' distance was used. This process is further explained ',
                                (0, n.jsx)(t.a, { href: '/kmeans', children: 'here' }),
                                '.',
                            ],
                        }),
                        '\n',
                        (0, n.jsx)(t.h3, { id: 'designing-the-ui', children: 'Designing the UI' }),
                        '\n',
                        (0, n.jsxs)(t.p, {
                            children: [
                                'Once all the previous steps were completed, the final step was to design a simple and easy to use UI that was as visually appealing as possible, to achieve this goal I utilized ',
                                (0, n.jsx)(t.a, { href: 'https://react.dev/', children: 'React' }),
                                ' and ',
                                (0, n.jsx)(t.a, { href: 'https://reactrouter.com/', children: 'React Router' }),
                                ' in combination with ',
                                (0, n.jsx)(t.a, { href: 'https://tailwindcss.com/', children: 'TailwindCSS' }),
                                ' and ',
                                (0, n.jsx)(t.a, { href: 'https://daisyui.com/', children: 'DaisyUI' }),
                                ' alongside various npm packages such as ',
                                (0, n.jsx)(t.a, {
                                    href: 'https://github.com/lucaong/minisearch',
                                    children: 'MiniSearch',
                                }),
                                ', ',
                                (0, n.jsx)(t.a, { href: 'https://github.com/lodash/lodash', children: 'lodash' }),
                                ', ',
                                (0, n.jsx)(t.a, {
                                    href: 'https://github.com/adoxography/tailwind-scrollbar',
                                    children: 'tailwind-scrollbar',
                                }),
                                ', ',
                                (0, n.jsx)(t.a, {
                                    href: 'https://github.com/danbovey/react-infinite-scroller',
                                    children: 'React Infinite Scroller',
                                }),
                                ', ',
                                (0, n.jsx)(t.a, {
                                    href: 'https://github.com/akiran/react-slick',
                                    children: 'react-slick',
                                }),
                                ', and ',
                                (0, n.jsx)(t.a, {
                                    href: 'https://github.com/kenwheeler/slick/',
                                    children: 'slick-carousel',
                                }),
                                '.',
                            ],
                        }),
                    ],
                });
            }
            function c(e = {}) {
                const { wrapper: t } = { ...(0, a.R)(), ...e.components };
                return t ? (0, n.jsx)(t, { ...e, children: (0, n.jsx)(l, { ...e }) }) : l(e);
            }
        },
        8453: (e, t, i) => {
            i.d(t, { R: () => r, x: () => o });
            var n = i(6540);
            const a = {},
                s = n.createContext(a);
            function r(e) {
                const t = n.useContext(s);
                return n.useMemo(
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
                            ? e.components(a)
                            : e.components || a
                        : r(e.components)),
                    n.createElement(s.Provider, { value: t }, e.children)
                );
            }
        },
    },
]);
