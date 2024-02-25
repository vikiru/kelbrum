import React, { useState } from 'react';
import { Link } from 'react-router-dom';

function Footer() {
    return (
        <div>
            <footer className="footer bg-neutral p-10 text-neutral-content">
                <nav>
                    <h6 className="footer-title text-xl">Features</h6>
                    <Link
                        to="/topAnime"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="link-hover link text-lg capitalize"
                    >
                        View the top 100 Anime
                    </Link>
                    <Link
                        to="/search"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="link-hover link text-lg capitalize"
                    >
                        Search Anime
                    </Link>
                    <Link
                        to="/recommendations"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="link-hover link text-lg capitalize"
                    >
                        Get anime recommendations
                    </Link>
                </nav>
                <nav>
                    <h6 className="footer-title text-xl">About</h6>
                    <a
                        className="link-hover link text-lg"
                        href="https://github.com/vikiru/"
                        target="_blank"
                        rel="noopener noreferrer"
                    >
                        Acknowledgements
                    </a>
                    <a
                        className="link-hover link text-lg"
                        href="https://github.com/vikiru/"
                        target="_blank"
                        rel="noopener noreferrer"
                    >
                        Documentation
                    </a>
                    <a
                        className="link-hover link text-lg"
                        href="https://github.com/vikiru/"
                        target="_blank"
                        rel="noopener noreferrer"
                    >
                        GitHub
                    </a>
                </nav>
            </footer>
            <footer className="footer footer-center border-t border-base-300 bg-neutral px-10 py-4 text-base-content">
                <div className="text-center text-lg text-neutral-content">
                    &copy; {new Date().getFullYear()} Placeholder Name
                    <span>All images and text belong to their rightful owners.</span>
                </div>
            </footer>
        </div>
    );
}

export default Footer;
