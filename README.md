# F1 Head-to-Head Driver Matchup Dashboard

A Formula 1 analytics dashboard built with Dash and Plotly for comparing driver performance and predicting race outcomes.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Dash](https://img.shields.io/badge/Dash-2.9+-green.svg)

## App Link Hosted on Plotly Cloud: [App_Link](https://72d41d06-2ef3-4d18-9939-027b049e6269.plotly.app/)
## Features

- **Head-to-Head Comparison**: Compare two F1 drivers across multiple metrics
  - Average finishing position
  - Total career points
  - DNF (Did Not Finish) rates
  
- **Top Drivers Sidebar**: View top N drivers by race wins (configurable)

- **Race Predictor**: Predict race outcomes using machine learning
  - Select circuit, drivers, constructors, and grid positions
  - Random Forest Classifier trained on hybrid era data (2014+)

## Project Structure

```
F1/
├── app.py                 # Main application entry point
├── layout.py              # Dashboard UI layout
├── callbacks.py           # Dash callbacks and logic
├── requirements.txt       # Python dependencies
├── README.md
│
├── assets/
│   └── style.css          # Custom CSS styling
│
├── data/
│   ├── results.csv        # Race results
│   ├── races.csv          # Race information
│   ├── drivers.csv        # Driver information
│   ├── constructors.csv   # Constructor/team data
│   ├── qualifying.csv     # Qualifying results
│   ├── pit_stops.csv      # Pit stop data
│   ├── circuits.csv       # Circuit information
│   ├── f1_cleaned.csv     # Processed dataset (generated)
│   ├── drivers_lookup.csv # Driver dropdown data (generated)
│   ├── constructors_lookup.csv
│   ├── circuits_lookup.csv
│   └── rf_classifier_h2h.pkl  # Trained model (generated)
│
└── notebooks/
    └── 01_eda_and_training.ipynb  # Data prep & model training
```

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/f1-head-to-head.git
   cd f1-head-to-head
   ```

2. **Create virtual environment** (optional but recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Download F1 data**
   
   Download the Ergast F1 dataset from [ergast.com/mrd](http://ergast.com/mrd/db/) and place CSV files in the `data/` folder.

5. **Train the model**
   
   Open and run `notebooks/01_eda_and_training.ipynb` to generate:
   - `data/f1_cleaned.csv`
   - `data/rf_classifier_h2h.pkl`
   - Lookup CSV files

6. **Run the dashboard**
   ```bash
   python app.py
   ```
   
   Open http://127.0.0.1:8050 in your browser.

## Usage

### Tab 1: H2H Stats
- Select two different drivers from the dropdowns
- View comparison charts for finish positions, points, and DNF rates
- Use the sidebar slider to see top N drivers by wins

### Tab 2: Race Predictor
- Select a circuit
- Choose drivers and their constructors
- Set grid positions (must be unique)
- View predicted finishing positions and winner

### Tab 3: Top Drivers
- Shows the all-time top 3-10 drivers based on race wins.

## Tech Stack

- **Python 3.8+**
- **Dash** - Web framework
- **Plotly** - Interactive visualizations
- **Pandas** - Data manipulation
- **Scikit-learn** - Machine learning
- **Dash Bootstrap Components** - UI components

## Data Source

Data from the [Ergast Developer API](http://ergast.com/mrd/) - a free Formula 1 historical database.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit changes (`git commit -m 'Add new feature'`)
4. Push to branch (`git push origin feature/new-feature`)
5. Open a Pull Request
