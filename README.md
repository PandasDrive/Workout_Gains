My Personal Fitness Hub

1. Project Purpose

This is a private, personal project designed to consolidate all the fitness programs I have purchased from various influencers into one simple, easy-to-use application.

The goal is to stop logging into multiple different websites, which causes me to lose track of my progress. This app will be a single source of truth for all my workout plans.

This app is for my use only and will not be shared, distributed, or commercialized in any way. It simply acts as a personal digital notebook for programs I legally own.

2. Key Features

Program Dashboard: A main screen to select which program I'm currently following.

Workout Library: A section organizing each program by its creator.

Program View: A screen to select the week and day of the program.

Daily Workout View: Cleanly display the specific exercises, sets, reps, and rest periods for the current day.

Progress Tracking: A simple way to check off completed workouts and track what day/week I am on.

Notes: A place to log notes for specific exercises (e.g., "Upped the weight to 30lbs").

Exercise Links (Future Idea): Eventually, maybe add links to YouTube videos or descriptions for specific exercises for quick reference.

3. Programs to Include

This app will house the workout routines from the following programs I've purchased:

- Kris Gethin – Legacy 12-Week Program (fully loaded)
- Jeff Nippard – 12-Week Program (fully loaded)
- Kaged Programs (e.g., Legacy, 12-Week Hardcore Daily Trainer, 8-Week Muscle Building) – queued for import
- Seth Feroce – AXE & Sledge and All American Roughneck series (e.g., DOMIN8, High Volume Trainer) – queued for import
- Thenx Calisthenics – Complete beginner/intermediate/advanced bodyweight plans – queued for import
- Additional influencer programs as I continue to grab the content I legally own

4. Technical Approach

This project is being built as a Progressive Web App (PWA).

Why a PWA? It provides the best of both worlds: the ease of a website with the feel of a native app.

How it works: It's a single HTML file that can be "installed" on any phone (iPhone or Android) using the browser's "Add to Home Screen" feature.

Core Benefits:

App-like Feel: Opens full-screen from a home screen icon, with no browser URL bar.

Universal: Works on any device with a modern browser.

Private: Requires no App Store, no developer accounts, and no complex "sideloading."

Offline Progress: Uses the browser's localStorage to save progress (like the current week/day) directly on the phone, so you never lose your spot.

Technology: Built with a single file using HTML, Tailwind CSS, and plain JavaScript.

5. Data & Dev Notes

- Program Data: All structured workouts now live in `data/program-data.js`. Both Gethin and Nippard are complete (weeks 1–12). Future programs will be appended here as new datasets are parsed.
- Source Material: Raw PDFs, spreadsheets, and exported text live under `WorkoutPrograms/`. Keep each original file so the data lineage is clear.
- Dev Utilities: Helper scripts in `.devtools/` handle parsing, exporting JSON, and regenerating JS snippets. Leave the folder hidden from the main UI.
- Backups & History: The PWA supports local JSON backups via the new Progress Hub. Export regularly and keep copies with the original source files.
- Future Work: Next wave is importing the Kaged collection, Seth Feroce programs, and Thenx calisthenics templates. Once these are loaded, revisit UI polish (coach bios, onboarding quiz, video demos) and consider add-on features like set tracking or social share cards.