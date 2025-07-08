/** @type {import('tailwindcss').Config} */
/* eslint-disable max-len */
const _colors = require('tailwindcss/colors');

const config = {
    content: ['./src/**/*.{js,ts,jsx,tsx}'],
    daisyui: {
        base: true,
        darkTheme: 'dark',
        logs: true,
        prefix: '',
        styled: true,
        themeRoot: ':root',
        themes: [
            {
                darkTheme: {
                    accent: '#CCCCCC',
                    'base-100': '#F5F5F5',
                    error: '#FF0000',
                    info: '#0000FF',
                    neutral: '#333333',
                    primary: '#000000',
                    secondary: '#FFFFFF',
                    success: '#008000',
                    warning: '#FFA500',
                },
                lightTheme: {
                    accent: '#FF5733',
                    'base-100': '#F5F5F5',
                    error: '#DC3545',
                    info: '#007BFF',
                    neutral: '#333333',
                    primary: '#FFFFFF',
                    secondary: '#000000',
                    success: '#28A745',
                    warning: '#FFA500',
                },
            },
        ],
        utils: true,
    },
    plugins: [require('daisyui'), require('tailwind-scrollbar')],
    theme: {
        extend: {
            fontFamily: {
                logo: ['Cinzel Decorative', 'serif'],
            },
            screens: {
                '3xl': '1920px',
                '4xl': '2560px',
                '5xl': '3840px',
                xs: '300px',
            },
        },
    },
};

export default config;
