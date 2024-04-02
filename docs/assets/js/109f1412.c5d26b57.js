'use strict';
(self.webpackChunkkelbrum_docs = self.webpackChunkkelbrum_docs || []).push([
    [703],
    {
        2012: (e, t, n) => {
            n.r(t),
                n.d(t, {
                    assets: () => l,
                    contentTitle: () => r,
                    default: () => h,
                    frontMatter: () => a,
                    metadata: () => s,
                    toc: () => c,
                });
            var o = n(4848),
                i = n(8453);
            const a = { title: '\ud83d\udd25 Motivation' },
                r = void 0,
                s = {
                    id: 'motivation',
                    title: '\ud83d\udd25 Motivation',
                    description: '\ud83d\udd25 Motivation',
                    source: '@site/docs/motivation.md',
                    sourceDirName: '.',
                    slug: '/motivation',
                    permalink: '/kelbrum/motivation',
                    draft: !1,
                    unlisted: !1,
                    tags: [],
                    version: 'current',
                    frontMatter: { title: '\ud83d\udd25 Motivation' },
                    sidebar: 'docs',
                    previous: { title: '\ud83c\udf1f Features', permalink: '/kelbrum/features' },
                    next: { title: '\ud83d\udd27 Development Overview', permalink: '/kelbrum/development' },
                },
                l = {},
                c = [{ value: '\ud83d\udd25 Motivation', id: '-motivation', level: 2 }];
            function u(e) {
                const t = { h2: 'h2', p: 'p', ...(0, i.R)(), ...e.components };
                return (0, o.jsxs)(o.Fragment, {
                    children: [
                        (0, o.jsx)(t.h2, { id: '-motivation', children: '\ud83d\udd25 Motivation' }),
                        '\n',
                        (0, o.jsx)(t.p, {
                            children:
                                'As someone who understands the challenge of discovering a new series to watch after completing another, I have always envisioned creating a tool akin to an AI which would be able to understand a users preferences given their past favourites or genre preferences as input and return series that they may like based on their similarity to the input data.',
                        }),
                        '\n',
                        (0, o.jsx)(t.p, {
                            children:
                                'My objective with this project was to develop a tool designed to alleviate the challenge of finding new content to watch, aiming to introduce users to recommendations that align with their tastes while also exploring new or previously unknown options. Through this project, I wanted to take a step towards learning about machine learning and recommendation systems while also improving my frontend capabilities by using a new UI library alongside TailwindCSS.',
                        }),
                        '\n',
                        (0, o.jsx)(t.p, {
                            children:
                                "The project, while not flawless in its current iteration, presents numerous opportunities for enhancement, particularly in the recommendation algorithm and the app's user interface. There are several features that I would like to implement in the future such as a hybrid recommendation system that combines collaborative filtering with the existing content-based filtering method, extending the functionality of the model to handle other content types such as manga, manhwa, and manhua, among other features.",
                        }),
                    ],
                });
            }
            function h(e = {}) {
                const { wrapper: t } = { ...(0, i.R)(), ...e.components };
                return t ? (0, o.jsx)(t, { ...e, children: (0, o.jsx)(u, { ...e }) }) : u(e);
            }
        },
        8453: (e, t, n) => {
            n.d(t, { R: () => r, x: () => s });
            var o = n(6540);
            const i = {},
                a = o.createContext(i);
            function r(e) {
                const t = o.useContext(a);
                return o.useMemo(
                    function () {
                        return 'function' == typeof e ? e(t) : { ...t, ...e };
                    },
                    [t, e],
                );
            }
            function s(e) {
                let t;
                return (
                    (t = e.disableParentContext
                        ? 'function' == typeof e.components
                            ? e.components(i)
                            : e.components || i
                        : r(e.components)),
                    o.createElement(a.Provider, { value: t }, e.children)
                );
            }
        },
    },
]);
