import type { DocumentationConfig } from '@/types/Config';

export const documentationConfig: DocumentationConfig = {
  site: {
    title: 'Kelbrum Documentation',
    description:
      'Documentation for Kelbrum - An anime recommendation system designed to recommend anime similar to user-selected anime.',
    projectDescription: 'An anime recommendation system designed to recommend anime similar to user-selected anime.',
    siteUrl: 'https://vikiru.github.io',
    base: '/kelbrum',
    documentationUrl: 'https://vikiru.github.io/kelbrum',
    websiteLastModified: new Date(),
  },
  author: {
    name: 'Visakan Kirubakaran',
    alternateName: 'Vis Kirubakaran',
    firstName: 'Visakan',
    lastName: 'Kirubakaran',
    jobTitle: 'Software Developer',
    portfolioWebsite: 'https://vikiru.vercel.app',
    githubProfile: 'https://github.com/vikiru',
    linkedinProfile: 'https://linkedin.com/in/viskirubakaran',
    universityName: 'Carleton University',
    universityLogo: 'https://carleton.ca/favicon.ico',
    universityUrl: 'https://carleton.ca/',
  },
  project: {
    name: 'Kelbrum',
    githubRepo: 'https://github.com/vikiru/kelbrum',
    liveDemoUrl: 'https://kelbrum-v1.web.app',
    version: '1.0.0',
    startDate: '2024-02-01',
    endDate: '2024-03-08',
    programmingLanguage: 'JavaScript',
    keywords: [
      'anime',
      'recommendation',
      'system',
      'machine-learning',
      'kelbrum',
      'similarity',
      'kmeans',
      'react',
      'tensorflow',
    ],
    license: 'https://opensource.org/licenses/MIT',
  },
  assets: {
    themeColor: '#000',
    logoFileName: 'logo.png',
    faviconFileName: 'favicon.ico',
  },
};
