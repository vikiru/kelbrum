'use strict';
(self.webpackChunkkelbrum_docs = self.webpackChunkkelbrum_docs || []).push([
    [672],
    {
        2363: (e, t, n) => {
            n.r(t),
                n.d(t, {
                    assets: () => c,
                    contentTitle: () => r,
                    default: () => m,
                    frontMatter: () => s,
                    metadata: () => o,
                    toc: () => d,
                });
            var i = n(4848),
                a = n(8453);
            const s = { title: '\ud83c\udf1f Features' },
                r = void 0,
                o = {
                    id: 'features',
                    title: '\ud83c\udf1f Features',
                    description: '\ud83c\udf1f Features',
                    source: '@site/docs/features.md',
                    sourceDirName: '.',
                    slug: '/features',
                    permalink: '/kelbrum/features',
                    draft: !1,
                    unlisted: !1,
                    tags: [],
                    version: 'current',
                    frontMatter: { title: '\ud83c\udf1f Features' },
                    sidebar: 'docs',
                    previous: { title: '\ud83d\udcdc Available Scripts', permalink: '/kelbrum/scripts' },
                    next: { title: '\ud83d\udd25 Motivation', permalink: '/kelbrum/motivation' },
                },
                c = {},
                d = [{ value: '\ud83c\udf1f Features', id: '-features', level: 2 }];
            function l(e) {
                const t = { code: 'code', h2: 'h2', li: 'li', ul: 'ul', ...(0, a.R)(), ...e.components };
                return (0, i.jsxs)(i.Fragment, {
                    children: [
                        (0, i.jsx)(t.h2, { id: '-features', children: '\ud83c\udf1f Features' }),
                        '\n',
                        (0, i.jsxs)(t.ul, {
                            children: [
                                '\n',
                                (0, i.jsx)(t.li, {
                                    children:
                                        'The ability to search for any anime within the existing dataset via a search bar',
                                }),
                                '\n',
                                (0, i.jsx)(t.li, {
                                    children:
                                        'A homepage featuring a hero section that encourages users to search for an anime and displays 10 anime randomly selected that meet a minimum average score, providing users with immediate recommendations',
                                }),
                                '\n',
                                (0, i.jsxs)(t.li, {
                                    children: [
                                        'The ability to view all anime grouped together based on properties such as ',
                                        (0, i.jsx)(t.code, { children: 'genres' }),
                                        ', ',
                                        (0, i.jsx)(t.code, { children: 'studios' }),
                                        ', ',
                                        (0, i.jsx)(t.code, { children: 'seasons' }),
                                        ', etc',
                                    ],
                                }),
                                '\n',
                                (0, i.jsx)(t.li, {
                                    children:
                                        'The ability to view the top 100 anime within the existing set of anime, based on average score',
                                }),
                                '\n',
                                (0, i.jsx)(t.li, {
                                    children:
                                        'A dedicated anime details page that enables users to view detailed information about an anime and receive recommendations based on similarity',
                                }),
                                '\n',
                                (0, i.jsx)(t.li, {
                                    children:
                                        'The ability to view 10 unique random anime recommendations and view up to 200 recommendations per anime (not all anime will have that many recommendations)',
                                }),
                                '\n',
                                (0, i.jsxs)(t.li, {
                                    children: [
                                        'The ability to grow and accommodate other content types such as ',
                                        (0, i.jsx)(t.code, { children: 'manga' }),
                                        ', ',
                                        (0, i.jsx)(t.code, { children: 'manhwa' }),
                                        ', and ',
                                        (0, i.jsx)(t.code, { children: 'manhua' }),
                                    ],
                                }),
                                '\n',
                                (0, i.jsx)(t.li, {
                                    children:
                                        'The capability to prioritize anime properties based on assigned weights and adjust the recommendation algorithm at any time using the provided K-means JSON file and feature tensors',
                                }),
                                '\n',
                            ],
                        }),
                    ],
                });
            }
            function m(e = {}) {
                const { wrapper: t } = { ...(0, a.R)(), ...e.components };
                return t ? (0, i.jsx)(t, { ...e, children: (0, i.jsx)(l, { ...e }) }) : l(e);
            }
        },
        8453: (e, t, n) => {
            n.d(t, { R: () => r, x: () => o });
            var i = n(6540);
            const a = {},
                s = i.createContext(a);
            function r(e) {
                const t = i.useContext(s);
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
                            ? e.components(a)
                            : e.components || a
                        : r(e.components)),
                    i.createElement(s.Provider, { value: t }, e.children)
                );
            }
        },
    },
]);
