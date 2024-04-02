'use strict';
(self.webpackChunkkelbrum_docs = self.webpackChunkkelbrum_docs || []).push([
    [809],
    {
        7181: (e, t, r) => {
            r.r(t),
                r.d(t, {
                    assets: () => l,
                    contentTitle: () => o,
                    default: () => a,
                    frontMatter: () => i,
                    metadata: () => u,
                    toc: () => c,
                });
            var s = r(4848),
                n = r(8453);
            const i = { id: 'prerequisites', title: '\ud83d\udcdd Prerequisites' },
                o = void 0,
                u = {
                    id: 'prerequisites',
                    title: '\ud83d\udcdd Prerequisites',
                    description: '\ud83d\udcdd Prerequisites',
                    source: '@site/docs/prerequisites.md',
                    sourceDirName: '.',
                    slug: '/prerequisites',
                    permalink: '/kelbrum/prerequisites',
                    draft: !1,
                    unlisted: !1,
                    tags: [],
                    version: 'current',
                    frontMatter: { id: 'prerequisites', title: '\ud83d\udcdd Prerequisites' },
                    sidebar: 'docs',
                    previous: { title: '\ud83d\udcd6 Introduction', permalink: '/kelbrum/' },
                    next: { title: '\u26a1 Setup', permalink: '/kelbrum/setup' },
                },
                l = {},
                c = [{ value: '\ud83d\udcdd Prerequisites', id: '-prerequisites', level: 2 }];
            function d(e) {
                const t = { a: 'a', h2: 'h2', li: 'li', p: 'p', ul: 'ul', ...(0, n.R)(), ...e.components };
                return (0, s.jsxs)(s.Fragment, {
                    children: [
                        (0, s.jsx)(t.h2, { id: '-prerequisites', children: '\ud83d\udcdd Prerequisites' }),
                        '\n',
                        (0, s.jsxs)(t.p, {
                            children: [
                                'Ensure that the following dependencies are installed onto your machine by following the ',
                                (0, s.jsx)(t.a, { href: '/setup', children: 'Setup Instructions' }),
                                '.',
                            ],
                        }),
                        '\n',
                        (0, s.jsxs)(t.ul, {
                            children: [
                                '\n',
                                (0, s.jsx)(t.li, {
                                    children: (0, s.jsx)(t.a, {
                                        href: 'https://nodejs.org/en/download',
                                        children: 'Node.js',
                                    }),
                                }),
                                '\n',
                            ],
                        }),
                    ],
                });
            }
            function a(e = {}) {
                const { wrapper: t } = { ...(0, n.R)(), ...e.components };
                return t ? (0, s.jsx)(t, { ...e, children: (0, s.jsx)(d, { ...e }) }) : d(e);
            }
        },
        8453: (e, t, r) => {
            r.d(t, { R: () => o, x: () => u });
            var s = r(6540);
            const n = {},
                i = s.createContext(n);
            function o(e) {
                const t = s.useContext(i);
                return s.useMemo(
                    function () {
                        return 'function' == typeof e ? e(t) : { ...t, ...e };
                    },
                    [t, e],
                );
            }
            function u(e) {
                let t;
                return (
                    (t = e.disableParentContext
                        ? 'function' == typeof e.components
                            ? e.components(n)
                            : e.components || n
                        : o(e.components)),
                    s.createElement(i.Provider, { value: t }, e.children)
                );
            }
        },
    },
]);
