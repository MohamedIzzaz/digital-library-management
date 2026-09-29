# Digital Library Management System

A terminal-based library management system written in Python with SQLite.

## Features
- Add, list, search and remove books (with multiple copies)
- Register and list members
- Issue and return books (14-day loan period)
- Automatic late fine calculation (2 per overdue day)
- Active loan list and full loan history
- Data stored persistently in `library.db`

## Requirements
- Python 3.8 or newer (no extra packages needed)

## Run

**Web version (localhost)**
```bash
pip install -r requirements.txt
python app.py
```
Then open http://localhost:5000 in your browser. Press `Ctrl + C` in the terminal to stop.

**Terminal version**
```bash
python main.py
```

## Test
```bash
python -m unittest -v
```

## Project structure
```
digital-library-management/
├── app.py             # web interface (Flask, localhost:5000)
├── templates/
│   └── index.html     # web page
├── main.py            # terminal menu / user interface
├── library.py         # business logic + SQLite database
├── test_library.py    # unit tests
├── requirements.txt
├── .gitignore
└── README.md
```

## Configuration
Edit `LOAN_DAYS` and `FINE_PER_DAY` at the top of `library.py`.

## License
MIT
