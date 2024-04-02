'use strict';
(self.webpackChunkkelbrum_docs = self.webpackChunkkelbrum_docs || []).push([
    [471],
    {
        8275: (e, n, r) => {
            r.r(n),
                r.d(n, {
                    assets: () => c,
                    contentTitle: () => o,
                    default: () => h,
                    frontMatter: () => t,
                    metadata: () => d,
                    toc: () => a,
                });
            var i = r(4848),
                s = r(8453);
            const t = { title: '\ud83e\udde9 Model Overview' },
                o = void 0,
                d = {
                    id: 'model',
                    title: '\ud83e\udde9 Model Overview',
                    description: '\ud83e\udde9 Model Overview',
                    source: '@site/docs/model.md',
                    sourceDirName: '.',
                    slug: '/model',
                    permalink: '/kelbrum/model',
                    draft: !1,
                    unlisted: !1,
                    tags: [],
                    version: 'current',
                    frontMatter: { title: '\ud83e\udde9 Model Overview' },
                    sidebar: 'docs',
                    previous: { title: '\ud83d\udee0\ufe0f Tech Stack', permalink: '/kelbrum/stack' },
                    next: { title: '\ud83d\udccf Normalizing Data', permalink: '/kelbrum/normalize' },
                },
                c = {},
                a = [{ value: '\ud83e\udde9 Model Overview', id: '-model-overview', level: 2 }];
            function l(e) {
                const n = {
                    a: 'a',
                    code: 'code',
                    h2: 'h2',
                    li: 'li',
                    p: 'p',
                    pre: 'pre',
                    strong: 'strong',
                    ul: 'ul',
                    ...(0, s.R)(),
                    ...e.components,
                };
                return (0, i.jsxs)(i.Fragment, {
                    children: [
                        (0, i.jsx)(n.h2, { id: '-model-overview', children: '\ud83e\udde9 Model Overview' }),
                        '\n',
                        (0, i.jsxs)(n.p, {
                            children: [
                                (0, i.jsx)(n.a, {
                                    href: 'https://github.com/vikiru/recommender/models/AnimeEntry.js',
                                    children: 'AnimeEntry',
                                }),
                                ': This is the main model which is meant to represent a distinct anime entry, including\r\nproperties such as its ',
                                (0, i.jsx)(n.code, { children: 'title' }),
                                ', ',
                                (0, i.jsx)(n.code, { children: 'type' }),
                                ', ',
                                (0, i.jsx)(n.code, { children: 'genres' }),
                                ', ',
                                (0, i.jsx)(n.code, { children: 'studios' }),
                                ', ',
                                (0, i.jsx)(n.code, { children: 'score' }),
                                ', ',
                                (0, i.jsx)(n.code, { children: 'pageURL' }),
                                ', etc.',
                            ],
                        }),
                        '\n',
                        (0, i.jsx)(n.p, {
                            children:
                                'This is the primary and at present, the only model used within this project. Every entry within the original dataset is read row by row and processed into this model.',
                        }),
                        '\n',
                        (0, i.jsxs)(n.p, {
                            children: [
                                'An example of an ',
                                (0, i.jsx)(n.strong, { children: 'AnimeEntry' }),
                                ' model can be seen below:',
                            ],
                        }),
                        '\n',
                        (0, i.jsx)(n.pre, {
                            children: (0, i.jsx)(n.code, {
                                className: 'language-json',
                                children:
                                    ' "id": 5183,\r\n "malID": 11061,\r\n "title": "Hunter x Hunter (2011)",\r\n "englishName": "Hunter x Hunter",\r\n "otherName": "HUNTER\xd7HUNTER\uff08\u30cf\u30f3\u30bf\u30fc\xd7\u30cf\u30f3\u30bf\u30fc\uff09",\r\n "titles": [\r\n    "Hunter x Hunter",\r\n    "HxH",\r\n    "HUNTER\xd7HUNTER\uff08\u30cf\u30f3\u30bf\u30fc\xd7\u30cf\u30f3\u30bf\u30fc\uff09",\r\n    "Hunter X Hunter: Cazadores de Tesoros"\r\n ],\r\n "score": 9.04,\r\n "genres": [\r\n    "Action",\r\n    "Adventure",\r\n    "Fantasy"\r\n ],\r\n "themes": [],\r\n "demographics": [\r\n    "Shounen"\r\n ],\r\n "synopsis": "Hunters devote themselves to accomplishing hazardous tasks, all from traversing the world\'s uncharted territories to locating rare items and monsters. Before becoming a Hunter, one must pass the Hunter Examination\u2014a high-risk selection process in which most applicants end up handicapped or worse, deceased.\\n\\nAmbitious participants who challenge the notorious exam carry their own reason. What drives 12-year-old Gon Freecss is finding Ging, his father and a Hunter himself. Believing that he will meet his father by becoming a Hunter, Gon takes the first step to walk the same path.\\n\\nDuring the Hunter Examination, Gon befriends the medical student Leorio Paladiknight, the vindictive Kurapika, and ex-assassin Killua Zoldyck. While their motives vastly differ from each other, they band together for a common goal and begin to venture into a perilous world.",\r\n "type": "TV",\r\n "episodes": 148,\r\n "aired": "Oct 2, 2011 to Sep 24, 2014",\r\n "premiered": "fall 2011",\r\n "season": "fall",\r\n "year": 2011,\r\n "status": "Finished Airing",\r\n "producers": [\r\n    "Nippon Television Network",\r\n    "Shueisha",\r\n    "VAP"\r\n ],\r\n "licensors": [\r\n    "VIZ Media"\r\n ],\r\n "studios": [\r\n    "Madhouse"\r\n ],\r\n "source": "Manga",\r\n "durationText": "23 min per ep",\r\n "durationMinutes": 23,\r\n "rating": "PG-13",\r\n "rank": 10,\r\n "popularity": 10,\r\n "favourites": 200265,\r\n "scoredBy": 1651790,\r\n "members": 2656870,\r\n "imageURL": "https://cdn.myanimelist.net/images/anime/1337/99013.jpg",\r\n "trailerURL": "Unknown",\r\n "pageURL": "https://myanimelist.net/anime/11061/Hunter x Hunter (2011)",\n',
                            }),
                        }),
                        '\n',
                        (0, i.jsx)(n.p, {
                            children:
                                'For the purposes of the recommendation system, not all properties are applicable. Through the development process, the following properties were used:',
                        }),
                        '\n',
                        (0, i.jsxs)(n.ul, {
                            children: [
                                '\n',
                                (0, i.jsx)(n.li, { children: (0, i.jsx)(n.code, { children: 'score' }) }),
                                '\n',
                                (0, i.jsx)(n.li, { children: (0, i.jsx)(n.code, { children: 'genres' }) }),
                                '\n',
                                (0, i.jsx)(n.li, { children: (0, i.jsx)(n.code, { children: 'themes' }) }),
                                '\n',
                                (0, i.jsx)(n.li, { children: (0, i.jsx)(n.code, { children: 'demographics' }) }),
                                '\n',
                                (0, i.jsx)(n.li, { children: (0, i.jsx)(n.code, { children: 'type' }) }),
                                '\n',
                                (0, i.jsx)(n.li, { children: (0, i.jsx)(n.code, { children: 'source' }) }),
                                '\n',
                                (0, i.jsx)(n.li, { children: (0, i.jsx)(n.code, { children: 'durationMinutes' }) }),
                                '\n',
                                (0, i.jsx)(n.li, { children: (0, i.jsx)(n.code, { children: 'rating' }) }),
                                '\n',
                                (0, i.jsx)(n.li, { children: (0, i.jsx)(n.code, { children: 'synopsis' }) }),
                                '\n',
                                (0, i.jsx)(n.li, { children: (0, i.jsx)(n.code, { children: 'year' }) }),
                                '\n',
                            ],
                        }),
                        '\n',
                        (0, i.jsxs)(n.p, {
                            children: [
                                'There is definetly room for improvement especially through the incorporation of more properties such as the ',
                                (0, i.jsx)(n.code, { children: 'studios' }),
                                ', ',
                                (0, i.jsx)(n.code, { children: 'favourites' }),
                                ', ',
                                (0, i.jsx)(n.code, { children: 'members' }),
                                ', ',
                                (0, i.jsx)(n.code, { children: 'rank' }),
                                ', ',
                                (0, i.jsx)(n.code, { children: 'popularity' }),
                                ', and ',
                                (0, i.jsx)(n.code, { children: 'episodes' }),
                                '. To further improve the recommendations, ',
                                (0, i.jsx)(n.code, { children: 'genres' }),
                                ', ',
                                (0, i.jsx)(n.code, { children: 'themes' }),
                                ' should use a form of ordinal encoding similar to ',
                                (0, i.jsx)(n.code, { children: 'type' }),
                                ', ',
                                (0, i.jsx)(n.code, { children: 'demographics' }),
                                ', and ',
                                (0, i.jsx)(n.code, { children: 'rating' }),
                                ' assigning unique numerical values to each possible value and trying to group similar properties like ',
                                (0, i.jsx)(n.code, { children: 'action' }),
                                ' and ',
                                (0, i.jsx)(n.code, { children: 'adventure' }),
                                ' closer together than for example, ',
                                (0, i.jsx)(n.code, { children: 'action' }),
                                ' and ',
                                (0, i.jsx)(n.code, { children: 'comedy' }),
                                '. It would also be nice to have additional unexplored properties such as ',
                                (0, i.jsx)(n.code, { children: 'countryOfOrigin' }),
                                ' which can be used to group similar anime based on where the source originated from.',
                            ],
                        }),
                    ],
                });
            }
            function h(e = {}) {
                const { wrapper: n } = { ...(0, s.R)(), ...e.components };
                return n ? (0, i.jsx)(n, { ...e, children: (0, i.jsx)(l, { ...e }) }) : l(e);
            }
        },
        8453: (e, n, r) => {
            r.d(n, { R: () => o, x: () => d });
            var i = r(6540);
            const s = {},
                t = i.createContext(s);
            function o(e) {
                const n = i.useContext(t);
                return i.useMemo(
                    function () {
                        return 'function' == typeof e ? e(n) : { ...n, ...e };
                    },
                    [n, e],
                );
            }
            function d(e) {
                let n;
                return (
                    (n = e.disableParentContext
                        ? 'function' == typeof e.components
                            ? e.components(s)
                            : e.components || s
                        : o(e.components)),
                    i.createElement(t.Provider, { value: n }, e.children)
                );
            }
        },
    },
]);
