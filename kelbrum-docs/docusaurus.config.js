// @ts-check
// `@type` JSDoc annotations allow editor autocompletion and type checking
// (when paired with `@ts-check`).
// There are various equivalent ways to declare your Docusaurus config.
// See: https://docusaurus.io/docs/api/docusaurus-config

import { themes as prismThemes } from 'prism-react-renderer';
import path from 'path';

const lightTheme = prismThemes.github;
const darkTheme = prismThemes.dracula;

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'Kelbrum',
  tagline: 'An anime recommendation system designed to recommend anime that is similar to user-selected anime.',
  favicon: 'public/favicon-dark.ico',

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
        {name: 'keywords', content: 'Kelbrum, anime, recommendation, engine, system, machine-learning, tensorflow, similarity, kmeans, react, react router, tailwindcss, daisyui'}
        {name: 'description', content: 'Kelbrum is an anime recommendation system designed to recommend anime that is similar to user-selected anime.'}
      ],      
      // Replace with your project's social card
      //image: '',
      navbar: {
        title: 'Kelbrum',
        logo: {
          alt: 'Kelbrum Logo',
          src: 'logo.png',
        },
        items: [
          {
            type: 'docSidebar',
            sidebarId: 'tutorialSidebar',
            position: 'left',
            label: 'Tutorial',
          },
          {to: '/blog', label: 'Blog', position: 'left'},
          {
            href: 'https://github.com/facebook/docusaurus',
            label: 'GitHub',
            position: 'right',
          },
        ],
      },
      footer: {
        style: 'dark',
        links: [
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
