'use strict';
(self.webpackChunkkelbrum_docs = self.webpackChunkkelbrum_docs || []).push([
    [889],
    {
        3026: (e, n, s) => {
            s.r(n),
                s.d(n, {
                    assets: () => a,
                    contentTitle: () => c,
                    default: () => d,
                    frontMatter: () => r,
                    metadata: () => l,
                    toc: () => h,
                });
            var t = s(4848),
                i = s(8453);
            const r = { title: '\ud83d\udee0\ufe0f Tech Stack' },
                c = void 0,
                l = {
                    id: 'stack',
                    title: '\ud83d\udee0\ufe0f Tech Stack',
                    description: '\ud83d\udee0\ufe0f Tech Stack',
                    source: '@site/docs/stack.md',
                    sourceDirName: '.',
                    slug: '/stack',
                    permalink: '/kelbrum/stack',
                    draft: !1,
                    unlisted: !1,
                    tags: [],
                    version: 'current',
                    frontMatter: { title: '\ud83d\udee0\ufe0f Tech Stack' },
                    sidebar: 'docs',
                    previous: { title: '\ud83d\udd27 Development Overview', permalink: '/kelbrum/development' },
                    next: { title: '\ud83e\udde9 Model Overview', permalink: '/kelbrum/model' },
                },
                a = {},
                h = [{ value: '\ud83d\udee0\ufe0f Tech Stack', id: '\ufe0f-tech-stack', level: 2 }];
            function o(e) {
                const n = { a: 'a', h2: 'h2', li: 'li', p: 'p', ul: 'ul', ...(0, i.R)(), ...e.components };
                return (0, t.jsxs)(t.Fragment, {
                    children: [
                        (0, t.jsx)(n.h2, { id: '\ufe0f-tech-stack', children: '\ud83d\udee0\ufe0f Tech Stack' }),
                        '\n',
                        (0, t.jsx)(n.p, { children: 'Backend:' }),
                        '\n',
                        (0, t.jsxs)(n.ul, {
                            children: [
                                '\n',
                                (0, t.jsx)(n.li, {
                                    children: (0, t.jsx)(n.a, { href: 'https://nodejs.org/en', children: 'Node.js' }),
                                }),
                                '\n',
                                (0, t.jsx)(n.li, {
                                    children: (0, t.jsx)(n.a, {
                                        href: 'https://github.com/tensorflow/tfjs',
                                        children: 'Tensorflow.js',
                                    }),
                                }),
                                '\n',
                                (0, t.jsx)(n.li, {
                                    children: (0, t.jsx)(n.a, {
                                        href: 'https://github.com/NaturalNode/natural',
                                        children: 'natural',
                                    }),
                                }),
                                '\n',
                                (0, t.jsx)(n.li, {
                                    children: (0, t.jsx)(n.a, {
                                        href: 'https://github.com/simple-statistics/simple-statistics',
                                        children: 'simple-statistics',
                                    }),
                                }),
                                '\n',
                                (0, t.jsx)(n.li, {
                                    children: (0, t.jsx)(n.a, {
                                        href: 'https://github.com/mljs/distance',
                                        children: 'ml-distance',
                                    }),
                                }),
                                '\n',
                                (0, t.jsx)(n.li, {
                                    children: (0, t.jsx)(n.a, {
                                        href: 'https://github.com/mljs/kmeans',
                                        children: 'ml-kmeans',
                                    }),
                                }),
                                '\n',
                            ],
                        }),
                        '\n',
                        (0, t.jsx)(n.p, { children: 'Frontend:' }),
                        '\n',
                        (0, t.jsxs)(n.ul, {
                            children: [
                                '\n',
                                (0, t.jsx)(n.li, {
                                    children: (0, t.jsx)(n.a, { href: 'https://react.dev/', children: 'React' }),
                                }),
                                '\n',
                                (0, t.jsx)(n.li, {
                                    children: (0, t.jsx)(n.a, {
                                        href: 'https://reactrouter.com/',
                                        children: 'React Router',
                                    }),
                                }),
                                '\n',
                                (0, t.jsx)(n.li, {
                                    children: (0, t.jsx)(n.a, { href: 'https://daisyui.com/', children: 'DaisyUI' }),
                                }),
                                '\n',
                                (0, t.jsx)(n.li, {
                                    children: (0, t.jsx)(n.a, {
                                        href: 'https://tailwindcss.com/',
                                        children: 'TailwindCSS',
                                    }),
                                }),
                                '\n',
                            ],
                        }),
                        '\n',
                        (0, t.jsx)(n.p, { children: 'Hosting:' }),
                        '\n',
                        (0, t.jsxs)(n.ul, {
                            children: [
                                '\n',
                                (0, t.jsxs)(n.li, {
                                    children: [
                                        (0, t.jsx)(n.a, { href: 'https://firebase.google.com/', children: 'Firebase' }),
                                        '\n',
                                        (0, t.jsxs)(n.ul, {
                                            children: [
                                                '\n',
                                                (0, t.jsxs)(n.li, {
                                                    children: [
                                                        'Analytics using ',
                                                        (0, t.jsx)(n.a, {
                                                            href: 'https://marketingplatform.google.com/about/analytics/',
                                                            children: 'Google Analytics',
                                                        }),
                                                        ' (Based on recommended Firebase config)',
                                                    ],
                                                }),
                                                '\n',
                                            ],
                                        }),
                                        '\n',
                                    ],
                                }),
                                '\n',
                            ],
                        }),
                        '\n',
                        (0, t.jsx)(n.p, { children: 'Documentation:' }),
                        '\n',
                        (0, t.jsxs)(n.ul, {
                            children: [
                                '\n',
                                (0, t.jsxs)(n.li, {
                                    children: [
                                        'Docs are built using ',
                                        (0, t.jsx)(n.a, { href: 'https://docusaurus.io/', children: 'Docusaurus' }),
                                        '\n',
                                        (0, t.jsxs)(n.ul, {
                                            children: [
                                                '\n',
                                                (0, t.jsxs)(n.li, {
                                                    children: [
                                                        'Search functionality provided by: ',
                                                        (0, t.jsx)(n.a, {
                                                            href: 'https://github.com/praveenn77/docusaurus-lunr-search',
                                                            children: 'docusaurus-lunr-search',
                                                        }),
                                                    ],
                                                }),
                                                '\n',
                                                (0, t.jsxs)(n.li, {
                                                    children: [
                                                        'Analytics using ',
                                                        (0, t.jsx)(n.a, {
                                                            href: 'https://marketingplatform.google.com/about/analytics/',
                                                            children: 'Google Analytics',
                                                        }),
                                                    ],
                                                }),
                                                '\n',
                                            ],
                                        }),
                                        '\n',
                                    ],
                                }),
                                '\n',
                                (0, t.jsxs)(n.li, {
                                    children: [
                                        'Documentation site hosted via ',
                                        (0, t.jsx)(n.a, {
                                            href: 'https://pages.github.com/',
                                            children: 'GitHub Pages',
                                        }),
                                    ],
                                }),
                                '\n',
                            ],
                        }),
                        '\n',
                        (0, t.jsx)(n.p, { children: 'Dev Tools:' }),
                        '\n',
                        (0, t.jsxs)(n.ul, {
                            children: [
                                '\n',
                                (0, t.jsx)(n.li, {
                                    children: (0, t.jsx)(n.a, { href: 'https://eslint.org/', children: 'ESLint' }),
                                }),
                                '\n',
                                (0, t.jsx)(n.li, {
                                    children: (0, t.jsx)(n.a, { href: 'https://prettier.io/', children: 'Prettier' }),
                                }),
                                '\n',
                                (0, t.jsx)(n.li, {
                                    children: (0, t.jsx)(n.a, { href: 'https://wakatime.com/', children: 'WakaTime' }),
                                }),
                                '\n',
                            ],
                        }),
                    ],
                });
            }
            function d(e = {}) {
                const { wrapper: n } = { ...(0, i.R)(), ...e.components };
                return n ? (0, t.jsx)(n, { ...e, children: (0, t.jsx)(o, { ...e }) }) : o(e);
            }
        },
        8453: (e, n, s) => {
            s.d(n, { R: () => c, x: () => l });
            var t = s(6540);
            const i = {},
                r = t.createContext(i);
            function c(e) {
                const n = t.useContext(r);
                return t.useMemo(
                    function () {
                        return 'function' == typeof e ? e(n) : { ...n, ...e };
                    },
                    [n, e],
                );
            }
            function l(e) {
                let n;
                return (
                    (n = e.disableParentContext
                        ? 'function' == typeof e.components
                            ? e.components(i)
                            : e.components || i
                        : c(e.components)),
                    t.createElement(r.Provider, { value: n }, e.children)
                );
            }
        },
    },
]);
