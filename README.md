# Rainbow Money SWPC

**Systematic Withdrawal Plan Calculator** for personalized retirement and SWP (Systematic Withdrawal Plan) analysis.

## 🚀 Project Overview

Rainbow Money SWPC helps users plan sustainable retirement withdrawals by projecting:

* Future value of current retirement investments (corpus + SIP)
* Required target corpus based on expected expenses
* Withdrawal strategies under **aggressive** or **conservative** modes

It leverages:

* Historical asset portfolios defined in `config/config.py`
* XIRR-based return estimates via Monte Carlo-like rolling calculations
* Two SWP approaches:

  * **Aggressive**: Full corpus available for withdrawal
  * **Conservative**: Maintain a reserve percentage after withdrawals

## 📂 Repository Structure

```
.
├── config/        # Portfolio definitions and constants
├── core/          # Core SWP and XIRR calculation modules
├── data/          # Historical NAV & forex datasets
├── models/        # Pydantic models for user input schemas
├── temp/          # Example input profiles and generated output
├── utils/         # Helper functions for I/O and logging
├── main.py        # Entry point for running simulations
├── requirements.txt  # Python dependencies
└── README.md      # Project documentation
```

## 💻 Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/Aryan-Bodhe/Rainbow-Money-SWPC.git
   cd Rainbow-Money-SWPC
   ```

2. **Create and activate a virtual environment** (recommended)

   ```bash
   python3 -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

## ⚙️ Usage

By default, `main.py` runs a sample profile located at `temp/profiles/middle.json`. To execute:

```bash
python main.py
```

### Custom Input

1. Copy one of the example JSON files in `temp/profiles/` and modify fields:

   ```json
   {
     "current_age": 45,
     "expected_retirement_age": 60,
     "expected_retirement_expenses": 50000,
     "current_retirement_corpus": 2000000,
     "retirement_sip": 10000
   }
   ```
2. In `main.py`, update the `data_path` argument in `runTest(...)` to point at your custom file.
3. Rerun `python main.py`.

### Output

* Console prints:

  * **Future Value of Investments**
  * **Ideal Target Corpus**
  * **Corpus Gap** and **Adequacy (%)**
  * **Extra SIP Required**
  * **Manual vs. Sustainable SWP amounts**
* Schedules written to `temp/current_schedule.txt` and `temp/target_schedule.txt`

## ⚙️ Configuration

All parameters and portfolio mixes live in `config/config.py`:

* Annual inflation and return rates
* Average life expectancy
* Pre/post-retirement portfolios
* Paths to historical NAV and forex data

Modify these constants to suit alternate assumptions or data sources.

## 📊 Example Profiles

* **young.json**: Early-career user
* **middle.json**: Mid-career user (default)
* **old.json**: Near-retirement scenario

## 🧠 Extending the Project

* Add a CLI interface (Click/argparse) for dynamic file inputs
* Integrate a web dashboard (Streamlit) for interactive plots
* Replace static config with external JSON or database

---

Created and maintained by **Aryan Bodhe**. Feel free to open issues or pull requests for improvements!
