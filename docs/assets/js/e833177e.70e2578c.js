'use strict';
(self.webpackChunkkelbrum_docs = self.webpackChunkkelbrum_docs || []).push([
    [734],
    {
        7862: (e, t, n) => {
            n.r(t),
                n.d(t, {
                    assets: () => c,
                    contentTitle: () => l,
                    default: () => p,
                    frontMatter: () => i,
                    metadata: () => a,
                    toc: () => o,
                });
            var s = n(4848),
                r = n(8453);
            const i = { title: '\ud83d\udcdc Available Scripts' },
                l = void 0,
                a = {
                    id: 'scripts',
                    title: '\ud83d\udcdc Available Scripts',
                    description: '\ud83d\udcdc Available Scripts',
                    source: '@site/docs/scripts.md',
                    sourceDirName: '.',
                    slug: '/scripts',
                    permalink: '/kelbrum/scripts',
                    draft: !1,
                    unlisted: !1,
                    tags: [],
                    version: 'current',
                    frontMatter: { title: '\ud83d\udcdc Available Scripts' },
                    sidebar: 'docs',
                    previous: { title: '\u26a1 Setup', permalink: '/kelbrum/setup' },
                    next: { title: '\ud83c\udf1f Features', permalink: '/kelbrum/features' },
                },
                c = {},
                o = [{ value: '\ud83d\udcdc Available Scripts', id: '-available-scripts', level: 2 }];
            function d(e) {
                const t = {
                    a: 'a',
                    code: 'code',
                    h2: 'h2',
                    li: 'li',
                    ol: 'ol',
                    pre: 'pre',
                    ...(0, r.R)(),
                    ...e.components,
                };
                return (0, s.jsxs)(s.Fragment, {
                    children: [
                        (0, s.jsx)(t.h2, { id: '-available-scripts', children: '\ud83d\udcdc Available Scripts' }),
                        '\n',
                        (0, s.jsxs)(t.ol, {
                            children: [
                                '\n',
                                (0, s.jsx)(t.li, { children: 'Start the app in the development environment.' }),
                                '\n',
                            ],
                        }),
                        '\n',
                        (0, s.jsx)(t.pre, {
                            children: (0, s.jsx)(t.code, { className: 'language-bash', children: 'npm start\n' }),
                        }),
                        '\n',
                        (0, s.jsxs)(t.ol, {
                            start: '2',
                            children: [
                                '\n',
                                (0, s.jsx)(t.li, { children: 'Build the project files and optimize for production.' }),
                                '\n',
                            ],
                        }),
                        '\n',
                        (0, s.jsx)(t.pre, {
                            children: (0, s.jsx)(t.code, { className: 'language-bash', children: 'npm run build\n' }),
                        }),
                        '\n',
                        (0, s.jsxs)(t.ol, {
                            start: '3',
                            children: [
                                '\n',
                                (0, s.jsxs)(t.li, {
                                    children: [
                                        'Lint all files and check if there are any issues, with ',
                                        (0, s.jsx)(t.a, { href: 'https://eslint.org/', children: 'ESLint' }),
                                        '.',
                                    ],
                                }),
                                '\n',
                            ],
                        }),
                        '\n',
                        (0, s.jsx)(t.pre, {
                            children: (0, s.jsx)(t.code, { className: 'language-bash', children: 'npm run lint\n' }),
                        }),
                        '\n',
                        (0, s.jsxs)(t.ol, {
                            start: '4',
                            children: [
                                '\n',
                                (0, s.jsxs)(t.li, {
                                    children: [
                                        'Fix all ESLint issues then format the files with ',
                                        (0, s.jsx)(t.a, { href: 'https://prettier.io/', children: 'Prettier' }),
                                        '.',
                                    ],
                                }),
                                '\n',
                            ],
                        }),
                        '\n',
                        (0, s.jsx)(t.pre, {
                            children: (0, s.jsx)(t.code, {
                                className: 'language-bash',
                                children: 'npm run prettier\n',
                            }),
                        }),
                    ],
                });
            }
            function p(e = {}) {
                const { wrapper: t } = { ...(0, r.R)(), ...e.components };
                return t ? (0, s.jsx)(t, { ...e, children: (0, s.jsx)(d, { ...e }) }) : d(e);
            }
        },
        8453: (e, t, n) => {
            n.d(t, { R: () => l, x: () => a });
            var s = n(6540);
            const r = {},
                i = s.createContext(r);
            function l(e) {
                const t = s.useContext(i);
                return s.useMemo(
                    function () {
                        return 'function' == typeof e ? e(t) : { ...t, ...e };
                    },
                    [t, e],
                );
            }
            function a(e) {
                let t;
                return (
                    (t = e.disableParentContext
                        ? 'function' == typeof e.components
                            ? e.components(r)
                            : e.components || r
                        : l(e.components)),
                    s.createElement(i.Provider, { value: t }, e.children)
                );
            }
        },
    },
]);
