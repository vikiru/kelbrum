import React, { useState } from 'react';

function Footer() {
    return (
        <div>
            <footer className="footer p-10 bg-neutral text-neutral-content">
                <nav>
                    <h6 className="footer-title text-xl">Features</h6>
                    <a className="text-lg link link-hover capitalize">View the top 100 Anime</a>
                    <a className="text-lg link link-hover capitalize">Search Anime</a>
                    <a className="text-lg link link-hover capitalize">Get anime recommendations</a>
                </nav>
                <nav>
                    <h6 className="footer-title text-xl">About</h6>
                    <a className="text-lg link link-hover" href="" target="_blank" rel="noopener noreferrer">
                        Acknowledgements
                    </a>
                    <a className="text-lg link link-hover" href="" target="_blank" rel="noopener noreferrer">
                        Documentation
                    </a>
                    <a className="text-lg link link-hover" href="" target="_blank" rel="noopener noreferrer">
                        GitHub
                    </a>
                </nav>
            </footer>
            <footer className="footer footer-center px-10 py-4 border-t bg-neutral text-base-content border-base-300">
                <div className="text-lg text-center text-neutral-content">
                    &copy; {new Date().getFullYear()} Placeholder Name
                    <span>All images and text belong to their rightful owners.</span>
                </div>
            </footer>
        </div>
    );
}

export default Footer;
