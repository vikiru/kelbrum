/**
 * Creating a sidebar enables you to:
 *
 * - Create an ordered group of docs
 * - Render a sidebar for each doc of that group
 * - Provide next/previous navigation
 *
 * The sidebars can be generated from the filesystem, or explicitly defined here.
 *
 * Create as many sidebars as you want.
 */

// @ts-check

/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
const sidebars = {
    // By default, Docusaurus generates a sidebar from the docs folder structure
    docs: [
        {
            type: 'category',
            label: 'Getting Started',
            items: ['index', 'prerequisites', 'setup', 'scripts', 'features'],
        },
        {
            type: 'category',
            label: 'Development',
            items: ['motivation', 'development', 'stack', 'model', 'normalize', 'kmeans'],
        },
        {
            type: 'category',
            label: 'Conclusion',
            items: ['acknowledgments'],
        },
    ],
};

export default sidebars;
