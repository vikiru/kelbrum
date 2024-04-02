'use strict';
(self.webpackChunkkelbrum_docs = self.webpackChunkkelbrum_docs || []).push([
    [214],
    {
        1111: (e, t, n) => {
            n.r(t),
                n.d(t, {
                    assets: () => c,
                    contentTitle: () => o,
                    default: () => d,
                    frontMatter: () => i,
                    metadata: () => l,
                    toc: () => u,
                });
            var s = n(4848),
                r = n(8453);
            const i = { title: '\u26a1 Setup' },
                o = void 0,
                l = {
                    id: 'setup',
                    title: '\u26a1 Setup',
                    description: '\u26a1 Setup Instructions',
                    source: '@site/docs/setup.md',
                    sourceDirName: '.',
                    slug: '/setup',
                    permalink: '/kelbrum/setup',
                    draft: !1,
                    unlisted: !1,
                    tags: [],
                    version: 'current',
                    frontMatter: { title: '\u26a1 Setup' },
                    sidebar: 'docs',
                    previous: { title: '\ud83d\udcdd Prerequisites', permalink: '/kelbrum/prerequisites' },
                    next: { title: '\ud83d\udcdc Available Scripts', permalink: '/kelbrum/scripts' },
                },
                c = {},
                u = [{ value: '\u26a1 Setup Instructions', id: '-setup-instructions', level: 2 }];
            function a(e) {
                const t = { code: 'code', h2: 'h2', li: 'li', ol: 'ol', pre: 'pre', ...(0, r.R)(), ...e.components };
                return (0, s.jsxs)(s.Fragment, {
                    children: [
                        (0, s.jsx)(t.h2, { id: '-setup-instructions', children: '\u26a1 Setup Instructions' }),
                        '\n',
                        (0, s.jsxs)(t.ol, {
                            children: [
                                '\n',
                                (0, s.jsx)(t.li, { children: 'Clone this repository to your local machine.' }),
                                '\n',
                            ],
                        }),
                        '\n',
                        (0, s.jsx)(t.pre, {
                            children: (0, s.jsx)(t.code, {
                                className: 'language-bash',
                                children: 'git clone https://github.com/vikiru/kelbrum.git\r\ncd kelbrum\n',
                            }),
                        }),
                        '\n',
                        (0, s.jsxs)(t.ol, {
                            start: '2',
                            children: [
                                '\n',
                                (0, s.jsx)(t.li, { children: 'Download and install all required dependencies.' }),
                                '\n',
                            ],
                        }),
                        '\n',
                        (0, s.jsx)(t.pre, {
                            children: (0, s.jsx)(t.code, { className: 'language-bash', children: 'npm install\n' }),
                        }),
                    ],
                });
            }
            function d(e = {}) {
                const { wrapper: t } = { ...(0, r.R)(), ...e.components };
                return t ? (0, s.jsx)(t, { ...e, children: (0, s.jsx)(a, { ...e }) }) : a(e);
            }
        },
        8453: (e, t, n) => {
            n.d(t, { R: () => o, x: () => l });
            var s = n(6540);
            const r = {},
                i = s.createContext(r);
            function o(e) {
                const t = s.useContext(i);
                return s.useMemo(
                    function () {
                        return 'function' == typeof e ? e(t) : { ...t, ...e };
                    },
                    [t, e],
                );
            }
            function l(e) {
                let t;
                return (
                    (t = e.disableParentContext
                        ? 'function' == typeof e.components
                            ? e.components(r)
                            : e.components || r
                        : o(e.components)),
                    s.createElement(i.Provider, { value: t }, e.children)
                );
            }
        },
    },
]);
