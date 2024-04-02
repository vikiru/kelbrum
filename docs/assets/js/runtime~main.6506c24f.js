(() => {
    'use strict';
    var e,
        r,
        t,
        a,
        o,
        n = {},
        f = {};
    function d(e) {
        var r = f[e];
        if (void 0 !== r) return r.exports;
        var t = (f[e] = { id: e, loaded: !1, exports: {} });
        return n[e].call(t.exports, t, t.exports, d), (t.loaded = !0), t.exports;
    }
    (d.m = n),
        (d.c = f),
        (e = []),
        (d.O = (r, t, a, o) => {
            if (!t) {
                var n = 1 / 0;
                for (u = 0; u < e.length; u++) {
                    (t = e[u][0]), (a = e[u][1]), (o = e[u][2]);
                    for (var f = !0, i = 0; i < t.length; i++)
                        (!1 & o || n >= o) && Object.keys(d.O).every((e) => d.O[e](t[i]))
                            ? t.splice(i--, 1)
                            : ((f = !1), o < n && (n = o));
                    if (f) {
                        e.splice(u--, 1);
                        var c = a();
                        void 0 !== c && (r = c);
                    }
                }
                return r;
            }
            o = o || 0;
            for (var u = e.length; u > 0 && e[u - 1][2] > o; u--) e[u] = e[u - 1];
            e[u] = [t, a, o];
        }),
        (d.n = (e) => {
            var r = e && e.__esModule ? () => e.default : () => e;
            return d.d(r, { a: r }), r;
        }),
        (t = Object.getPrototypeOf ? (e) => Object.getPrototypeOf(e) : (e) => e.__proto__),
        (d.t = function (e, a) {
            if ((1 & a && (e = this(e)), 8 & a)) return e;
            if ('object' == typeof e && e) {
                if (4 & a && e.__esModule) return e;
                if (16 & a && 'function' == typeof e.then) return e;
            }
            var o = Object.create(null);
            d.r(o);
            var n = {};
            r = r || [null, t({}), t([]), t(t)];
            for (var f = 2 & a && e; 'object' == typeof f && !~r.indexOf(f); f = t(f))
                Object.getOwnPropertyNames(f).forEach((r) => (n[r] = () => e[r]));
            return (n.default = () => e), d.d(o, n), o;
        }),
        (d.d = (e, r) => {
            for (var t in r) d.o(r, t) && !d.o(e, t) && Object.defineProperty(e, t, { enumerable: !0, get: r[t] });
        }),
        (d.f = {}),
        (d.e = (e) => Promise.all(Object.keys(d.f).reduce((r, t) => (d.f[t](e, r), r), []))),
        (d.u = (e) =>
            'assets/js/' +
            ({
                2: '72976fdb',
                48: 'a94703ab',
                98: 'a7bd4aaa',
                99: 'b94d04c2',
                214: '3847b3ea',
                401: '17896441',
                423: '8f030830',
                471: 'ece7a24a',
                571: '8270e422',
                581: '935f2afb',
                640: '163bfe4b',
                647: '5e95c892',
                672: '1a25ec0b',
                703: '109f1412',
                734: 'e833177e',
                742: 'c377a04b',
                809: 'af0b156e',
                889: '745ddde7',
            }[e] || e) +
            '.' +
            {
                2: '92a4e5dd',
                48: 'fbbbd047',
                98: 'c111e8c3',
                99: 'f61f8dc4',
                214: 'c32d5964',
                237: '7c0b999c',
                278: '979b43a2',
                401: 'abff9e00',
                423: '4f6653c2',
                471: 'b9016f5d',
                571: 'bfc689e6',
                577: 'b53c2d9d',
                581: '7eef070d',
                591: '11f62878',
                640: 'e9dfc1e2',
                647: '18800d58',
                672: 'c24f20c2',
                703: 'c5d26b57',
                734: '70e2578c',
                742: 'd9967a90',
                809: '1f5c86f1',
                889: 'b493041c',
            }[e] +
            '.js'),
        (d.miniCssF = (e) => {}),
        (d.g = (function () {
            if ('object' == typeof globalThis) return globalThis;
            try {
                return this || new Function('return this')();
            } catch (e) {
                if ('object' == typeof window) return window;
            }
        })()),
        (d.o = (e, r) => Object.prototype.hasOwnProperty.call(e, r)),
        (a = {}),
        (o = 'kelbrum-docs:'),
        (d.l = (e, r, t, n) => {
            if (a[e]) a[e].push(r);
            else {
                var f, i;
                if (void 0 !== t)
                    for (var c = document.getElementsByTagName('script'), u = 0; u < c.length; u++) {
                        var b = c[u];
                        if (b.getAttribute('src') == e || b.getAttribute('data-webpack') == o + t) {
                            f = b;
                            break;
                        }
                    }
                f ||
                    ((i = !0),
                    ((f = document.createElement('script')).charset = 'utf-8'),
                    (f.timeout = 120),
                    d.nc && f.setAttribute('nonce', d.nc),
                    f.setAttribute('data-webpack', o + t),
                    (f.src = e)),
                    (a[e] = [r]);
                var l = (r, t) => {
                        (f.onerror = f.onload = null), clearTimeout(s);
                        var o = a[e];
                        if ((delete a[e], f.parentNode && f.parentNode.removeChild(f), o && o.forEach((e) => e(t)), r))
                            return r(t);
                    },
                    s = setTimeout(l.bind(null, void 0, { type: 'timeout', target: f }), 12e4);
                (f.onerror = l.bind(null, f.onerror)),
                    (f.onload = l.bind(null, f.onload)),
                    i && document.head.appendChild(f);
            }
        }),
        (d.r = (e) => {
            'undefined' != typeof Symbol &&
                Symbol.toStringTag &&
                Object.defineProperty(e, Symbol.toStringTag, { value: 'Module' }),
                Object.defineProperty(e, '__esModule', { value: !0 });
        }),
        (d.p = '/kelbrum/'),
        (d.gca = function (e) {
            return (
                (e =
                    {
                        17896441: '401',
                        '72976fdb': '2',
                        a94703ab: '48',
                        a7bd4aaa: '98',
                        b94d04c2: '99',
                        '3847b3ea': '214',
                        '8f030830': '423',
                        ece7a24a: '471',
                        '8270e422': '571',
                        '935f2afb': '581',
                        '163bfe4b': '640',
                        '5e95c892': '647',
                        '1a25ec0b': '672',
                        '109f1412': '703',
                        e833177e: '734',
                        c377a04b: '742',
                        af0b156e: '809',
                        '745ddde7': '889',
                    }[e] || e),
                d.p + d.u(e)
            );
        }),
        (() => {
            var e = { 354: 0, 869: 0 };
            (d.f.j = (r, t) => {
                var a = d.o(e, r) ? e[r] : void 0;
                if (0 !== a)
                    if (a) t.push(a[2]);
                    else if (/^(354|869)$/.test(r)) e[r] = 0;
                    else {
                        var o = new Promise((t, o) => (a = e[r] = [t, o]));
                        t.push((a[2] = o));
                        var n = d.p + d.u(r),
                            f = new Error();
                        d.l(
                            n,
                            (t) => {
                                if (d.o(e, r) && (0 !== (a = e[r]) && (e[r] = void 0), a)) {
                                    var o = t && ('load' === t.type ? 'missing' : t.type),
                                        n = t && t.target && t.target.src;
                                    (f.message = 'Loading chunk ' + r + ' failed.\n(' + o + ': ' + n + ')'),
                                        (f.name = 'ChunkLoadError'),
                                        (f.type = o),
                                        (f.request = n),
                                        a[1](f);
                                }
                            },
                            'chunk-' + r,
                            r,
                        );
                    }
            }),
                (d.O.j = (r) => 0 === e[r]);
            var r = (r, t) => {
                    var a,
                        o,
                        n = t[0],
                        f = t[1],
                        i = t[2],
                        c = 0;
                    if (n.some((r) => 0 !== e[r])) {
                        for (a in f) d.o(f, a) && (d.m[a] = f[a]);
                        if (i) var u = i(d);
                    }
                    for (r && r(t); c < n.length; c++) (o = n[c]), d.o(e, o) && e[o] && e[o][0](), (e[o] = 0);
                    return d.O(u);
                },
                t = (self.webpackChunkkelbrum_docs = self.webpackChunkkelbrum_docs || []);
            t.forEach(r.bind(null, 0)), (t.push = r.bind(null, t.push.bind(t)));
        })();
})();
