/** @type {import('tailwindcss').Config} */
/* eslint-disable max-len */
const colors = require('tailwindcss/colors');

const config = {
    content: ['./src/**/*.{js,ts,jsx,tsx}'],
    daisyui: {
        themes: [
            {
                lightTheme: {
                    primary: '#FFFFFF',
                    secondary: '#000000',
                    accent: '#FF5733',
                    neutral: '#333333',
                    'base-100': '#F5F5F5',
                    info: '#007BFF',
                    success: '#28A745',
                    warning: '#FFA500',
                    error: '#DC3545',
                },
                darkTheme: {
                    primary: '#000000',
                    secondary: '#FFFFFF',
                    accent: '#CCCCCC',
                    neutral: '#333333',
                    'base-100': '#F5F5F5',
                    info: '#0000FF',
                    success: '#008000',
                    warning: '#FFA500',
                    error: '#FF0000',
                },
            },
        ],
        darkTheme: 'dark',
        base: true,
        styled: true,
        utils: true,
        prefix: '',
        logs: true,
        themeRoot: ':root',
    },
    theme: {
        extend: {
            screens: {
                xs: '300px',
                '3xl': '1920px',
                '4xl': '2560px',
                '5xl': '3840px',
            },
            fontFamily: {
                logo: ['Cinzel Decorative', 'serif'],
            },
        },
    },
    plugins: [require('daisyui'), require('tailwind-scrollbar')],
};

export default config;
