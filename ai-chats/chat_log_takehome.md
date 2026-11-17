# AI Interaction Logs & Engineering Transcripts

> Note for Reviewers: As instructed in the assignment guidelines, this file logs the core brainstorming, architectural refinement, and code generation conversations between the candidate and the AI assistant.

---

## Session 1: Problem Ideation & Reality Check (Human vs. AI)

**User (Candidate):**  
"I have 24 hours for a take-home assignment. I walked down to the chai and egg cart near our hostel road. The vendor (Manoj bhaiya) operates at night without a fridge. He says milk curdles if left overnight and boiled eggs have to be thrown out, but raw eggs survive. I want to build a tool to help him decide how much milk and boiled eggs to prepare. Don't give me a generic mobile app or cloud database. What operations research model fits this best?"

**AI:**  
"This is a classic variation of the Single-Period Newsvendor Problem with Asymmetric Salvage Values.
- In traditional inventory theory, items have a holding cost.
- In Manoj's case, items have binary holding characteristics:
  * Milk (opened 500ml pouch): Salvage value $S = 0$ after shift ends (curdles overnight).
  * Boiled eggs: Salvage value $S = 0$ (must be discarded by morning).
  * Raw eggs: Salvage value $S \approx C$ (can be safely used tomorrow).
  * Sealed Maggi: Salvage value $S = C$ (non-perishable).

The optimal service level for perishable items is determined by the critical ratio:
$$CR = \frac{C_u}{C_u + C_o}$$
Where:
- $C_u$ (Underage cost) = Lost gross margin when turning away a customer during peak hours (10:15–11:30 PM) after dairies close.
- $C_o$ (Overage cost) = Full purchase price lost when an opened milk pouch or boiled egg is discarded.

Instead of an interactive app he can't touch with oily hands, you should design a command-line prep advisor that takes a 20-30 minute peak-window observation log and computes the exact prep plan for tomorrow."

---

## Session 2: Preventing Over-Engineering

**User (Candidate):**  
"You're suggesting using Pandas and Scikit-learn for time-series forecasting. That's overkill and creates dependency headaches. The rubric says the evaluator will run our code and live-test a bad row. Write pure Python 3 using only the standard library (`csv`, `math`, `sys`, `argparse`, `datetime`). Make sure it gracefully skips bad rows instead of crashing."

**AI:**  
"Understood. Using pure standard library Python is much more reliable for evaluation. Here is the architecture:
1. `load_and_validate_data()`: Reads the CSV with `csv.DictReader`, checks for mandatory columns, validates data types, and prints non-fatal warnings to `sys.stderr` while appending valid rows.
2. `analyze_sales_and_consumption()`: Aggregates metrics (revenue, velocity per minute, milk burn in mL, raw vs boiled egg count).
3. `compute_recommendations()`: Converts burn rates to a shift-wide demand projection with discrete pouch ceiling (`math.ceil`) and safe pre-boil batch capping.
4. `print_cli_report()`: Generates a structured terminal report.

Let's test edge cases:
- Missing fields in a row
- Negative price or negative quantity
- Invalid timestamp formats like `22:99:99`
The validator will catch these and skip the row with `[SKIP ROW X]` while continuing to process the remaining valid dataset."

---

## Session 3: Live Threshold Tweaking Strategy

**User (Candidate):**  
"The panel will ask me to change a threshold live on the 10-minute call. Where should I expose those thresholds?"

**AI:**  
"Expose them in two distinct, easy-to-reach places:
1. As top-level named constants in `stall_optimizer.py`:
   - `MILK_BUFFER_PERCENT = 0.15` (Line 23)
   - `BOILED_EGG_SERVICE_LEVEL = 0.90` (Line 24)
   - `PEAK_HOURS_SCALE_FACTOR = 1.35` (Line 25)
2. As CLI arguments in `argparse`:
   - `--milk-buffer`
   - `--surge`
   - `--hours`

If the interviewer asks: *'What if milk boiling loss is 25% instead of 15%?'* you can either change line 23 to `0.25` or simply run:
`python tool/stall_optimizer.py --milk-buffer 0.25`"
