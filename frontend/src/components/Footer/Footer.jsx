import React, { useState } from 'react';
import { Link } from 'react-router-dom';

function Footer() {
    return (
        <div>
            <footer className="footer grid bg-neutral p-10 text-neutral-content lg:grid-cols-2">
                <nav>
                    <h6 className="footer-title text-xl">Discover</h6>
                    <Link to="/search" target="_blank" rel="noopener noreferrer" className="link-hover link text-lg">
                        Search for an anime
                    </Link>
                    <Link to="/anime/top" target="_blank" rel="noopener noreferrer" className="link-hover link text-lg">
                        View top 100 anime
                    </Link>
                </nav>
                <nav>
                    <h6 className="footer-title text-xl">Information</h6>

                    <Link
                        to="/anime/genres"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="link-hover link text-lg"
                    >
                        View all genres
                    </Link>
                    <Link
                        to="/anime/licensors"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="link-hover link text-lg"
                    >
                        View all licensors
                    </Link>
                    <Link
                        to="/anime/studios"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="link-hover link text-lg"
                    >
                        View all studios
                    </Link>
                    <Link
                        to="/anime/producers"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="link-hover link text-lg"
                    >
                        View all producers
                    </Link>
                    <Link
                        to="/anime/seasons"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="link-hover link text-lg"
                    >
                        View all seasons
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
                    &copy; {new Date().getFullYear()} Placeholder Name, built by vikiru. All images and text belong to
                    their rightful owners.
                    <span>Built with React, TailwindCSS, and DaisyUI.</span>
                </div>
            </footer>
        </div>
    );
}

export default Footer;
