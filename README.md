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

- Kris Gethin – Legacy 12-Week Program
- Jeff Nippard – 12-Week Program (data entry in progress)

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

- Program Data: Workout content now lives in `data/program-data.js`. The Gethin Legacy program currently includes manual entries for Weeks 1-4 (Weeks 5-12 are marked "Not Loaded" while we keep rebuilding them). Jeff Nippard’s 12-week program is fully populated from the spreadsheet export.
- Source Material: Raw text extracted from the PDFs lives under `WorkoutPrograms/` for quick cross-referencing.
- Dev Utilities: Helper scripts in `.devtools/` can regenerate structured data if we need to revisit the conversion.
- Future Work: Continue filling Gethin Weeks 5-12, then polish tasks/notes and run a pass over cardio/rest terminology for consistency.

5. Data & Dev Notes

- Program Data: All of Kris Gethin’s Legacy workouts (weeks 1–12) are hard-coded inside `index.html` under `programs.gethin.weeks`.
- Source Material: The raw text extracted from the official PDF lives at `WorkoutPrograms/legacy_program_text.txt` for quick reference.
- Dev Utilities: A hidden `.devtools/` directory stores helper scripts. `extract_pdf.py` lives there if you ever need to re-extract or parse new PDFs—leave the folder hidden so the app stays clean.
- Backups: Avoid editing the PDF directly; make changes in the text file or the data object and keep the extractor script handy for future programs.