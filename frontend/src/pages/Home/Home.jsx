import React, { useState } from 'react';

function Home() {
    return (
        <div className="hero flex min-h-screen items-center justify-center bg-primary">
            <div className="hero-content text-center">
                <div className="max-w-md">
                    <h1 className="text-5xl font-bold">Discover Your Next Favourite Anime</h1>
                    <p className="py-6">
                        Embark on an epic anime adventure with [Placeholder Name]! Tired of searching for a new anime or
                        trying to find a new movie to watch but can't find one that suits your taste? Look no further!
                        Search for one of your favorites, and you'll be presented with a selection of similar anime,
                        tailored just for you. Not happy with the suggestions? Refresh and you'll be presented with even
                        more!
                    </p>
                    <div className="flex justify-center space-x-4">
                        <button className="btn btn-accent rounded-lg px-6 py-3 text-white">Start Your Journey</button>
                        <button className="btn btn-accent rounded-lg px-6 py-3 text-white">View All Anime</button>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default Home;
