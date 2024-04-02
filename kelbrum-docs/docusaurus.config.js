// @ts-check
// `@type` JSDoc annotations allow editor autocompletion and type checking
// (when paired with `@ts-check`).
// There are various equivalent ways to declare your Docusaurus config.
// See: https://docusaurus.io/docs/api/docusaurus-config
import path from 'path';
import { themes as prismThemes } from 'prism-react-renderer';

const lightTheme = prismThemes.github;
const darkTheme = prismThemes.dracula;

/** @type {import('@docusaurus/types').Config} */
const config = {
    title: 'Kelbrum',

    tagline: 'An anime recommendation system designed to recommend anime that is similar to user-selected anime.',
    favicon: 'favicon.ico',
    staticDirectories: ['public', 'static'],
    trailingSlash: true,

    // Set the production url of your site here
    url: 'https://vikiru.github.io',
    // Set the /<baseUrl>/ pathname under which your site is served
    // For GitHub pages deployment, it is often '/<projectName>/'
    baseUrl: '/kelbrum',

    // GitHub pages deployment config.
    // If you aren't using GitHub pages, you don't need these.
    organizationName: 'vikiru', // Usually your GitHub org/user name.
    projectName: 'kelbrum', // Usually your repo name.

    onBrokenLinks: 'warn',
    onBrokenMarkdownLinks: 'warn',

    // Even if you don't use internationalization, you can use this field to set
    // useful metadata like html lang. For example, if your site is Chinese, you
    // may want to replace "en" with "zh-Hans".
    i18n: {
        defaultLocale: 'en',
        locales: ['en'],
    },

    plugins: [require.resolve('docusaurus-lunr-search')],

    presets: [
        [
            'classic',
            /** @type {import('@docusaurus/preset-classic').Options} */
            ({
                docs: {
                    routeBasePath: '/',
                    sidebarPath: require.resolve('./sidebars.js'),
                    breadcrumbs: true,
                },
                gtag: {
                    trackingID: 'G-HX9JEL4XJY',
                    anonymizeIP: true,
                },
                blog: false,
                theme: {
                    customCss: './src/css/custom.css',
                },
                sitemap: {
                    priority: 0.5,
                    ignorePatterns: [],
                    filename: 'sitemap.xml',
                },
            }),
        ],
    ],

    themeConfig:
        /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
        ({
            metadata: [
                {
                    name: 'author',
                    content: 'Visakan Kirubakaran',
                },
                {
                    name: 'keywords',
                    content:
                        'Kelbrum, anime, recommendation, engine, system, machine learning, tensorflow, similarity, kmeans, react, react router, tailwindcss, daisyui',
                },
                {
                    name: 'description',
                    content:
                        'Kelbrum is an anime recommendation system designed to recommend anime that is similar to user-selected anime.',
                },
            ],
            navbar: {
                hideOnScroll: true,
                title: 'Kelbrum',
                items: [
                    {
                        position: 'left',
                        label: 'Features',
                        href: '/features',
                    },
                    {
                        position: 'left',
                        label: 'Motivation',
                        href: '/motivation',
                    },
                ],
            },
            docs: {
                sidebar: {
                    hideable: true,
                    autoCollapseCategories: true,
                },
            },
            footer: {
                style: 'dark',
                links: [
                    {
                        title: 'Getting Started',
                        items: [
                            {
                                label: 'Home',
                                to: '/',
                            },
                            {
                                label: 'Prerequisites',
                                to: '/prerequisites',
                            },
                            {
                                label: 'Setup',
                                to: '/setup',
                            },
                            {
                                label: 'Scripts',
                                to: '/scripts',
                            },
                        ],
                    },
                    {
                        title: 'Development',
                        items: [
                            {
                                label: 'Motivation',
                                to: '/motivation',
                            },
                            {
                                label: 'Development Overview',
                                to: '/development',
                            },
                            {
                                label: 'Tech Stack',
                                to: '/stack',
                            },
                            {
                                label: 'Model Overview',
                                to: '/model',
                            },
                            {
                                label: 'Normalizing Data',
                                to: '/normalize',
                            },
                            {
                                label: 'Data Clustering',
                                to: '/kmeans',
                            },
                        ],
                    },
                    {
                        title: 'Conclusion',
                        items: [
                            {
                                label: 'Acknowledgments',
                                to: '/acknowledgments',
                            },
                            {
                                label: 'GitHub',
                                href: 'https://github.com/vikiru/kelbrum',
                            },
                        ],
                    },
                ],
                copyright: `Copyright © ${new Date().getFullYear()} Kelbrum, Visakan Kirubakaran. Built with Docusaurus.`,
            },
            prism: {
                theme: lightTheme,
                darkTheme,
            },
        }),
};

export default config;
