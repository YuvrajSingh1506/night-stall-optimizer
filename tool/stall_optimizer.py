#!/usr/bin/env python3
"""
Stall Inventory & Batch Optimizer for Manoj's Night Chai & Egg Cart
Author: 
Target Person: Manoj Kumar (Solo Street Food Vendor)
Data Source: data/data.csv (Field observation on 17-Nov-2026)

Key Operational Objective:
Balance the Newsvendor trade-off between:
1. Underage cost (Lost revenue during late-night peak 10:00-11:30 PM when suppliers are closed)
2. Overage cost (100% loss on overnight milk curdling and boiled egg spoilage due to no refrigeration)
"""

import csv
import sys
import os
import math
from datetime import datetime

# ==========================================
# CONFIGURABLE THRESHOLDS & MODEL PARAMETERS
# (Can be modified live during review call)
# ==========================================
DEFAULT_MILK_POUCH_VOLUME_ML = 500   # Standard Amul/Mother Dairy pouch size
MILK_BUFFER_PERCENT = 0.15           # 15% safety buffer for stove boiling loss & recipe variation
BOILED_EGG_SERVICE_LEVEL = 0.90      # 90% demand coverage target for pre-boiled eggs
PEAK_HOURS_SCALE_FACTOR = 1.35       # Multiplier for weekend / exam-week late night surge
CASH_FLOAT_SAFETY_RATIO = 0.40       # Recommended float reserve relative to expected cash receipts


def parse_timestamp(ts_str):
    """Parse time string formatted as HH:MM:SS or HH:MM."""
    ts_str = ts_str.strip()
    for fmt in ("%H:%M:%S", "%H:%M"):
        try:
            return datetime.strptime(ts_str, fmt)
        except ValueError:
            pass
    raise ValueError(f"Unrecognized time format: '{ts_str}'")


def load_and_validate_data(csv_filepath):
    """
    Reads data.csv and performs strict schema and boundary validation.
    Handles malformed rows gracefully with stderr warnings.
    """
    if not os.path.exists(csv_filepath):
        print(f"[ERROR] Data file not found at: {csv_filepath}", file=sys.stderr)
        sys.exit(1)

    valid_records = []
    skipped_count = 0

    with open(csv_filepath, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        required_columns = {
            'timestamp', 'order_id', 'item', 'qty',
            'unit_price_inr', 'total_inr', 'payment_method',
            'milk_consumed_ml', 'eggs_raw_used', 'eggs_boiled_used'
        }
        
        # Verify schema
        if not required_columns.issubset(set(reader.fieldnames or [])):
            missing = required_columns - set(reader.fieldnames or [])
            print(f"[FATAL] CSV is missing required columns: {missing}", file=sys.stderr)
            sys.exit(1)

        for row_idx, row in enumerate(reader, start=2):
            try:
                # Sanitize fields
                ts = parse_timestamp(row['timestamp'])
                qty = int(row['qty'])
                unit_price = float(row['unit_price_inr'])
                total_inr = float(row['total_inr'])
                pay_method = row['payment_method'].strip().upper()
                milk_ml = float(row['milk_consumed_ml'])
                eggs_raw = int(row['eggs_raw_used'])
                eggs_boiled = int(row['eggs_boiled_used'])

                # Boundary sanity checks
                if qty <= 0 or unit_price < 0 or total_inr < 0:
                    raise ValueError(f"Negative or zero value in numeric fields: qty={qty}, price={total_inr}")
                
                # Check arithmetic consistency (tolerance of 1 rupee for rounding)
                if abs((qty * unit_price) - total_inr) > 1.5:
                    print(f"[WARNING] Row {row_idx}: Total INR ({total_inr}) does not equal qty*price ({qty*unit_price}). Using total_inr.", file=sys.stderr)

                valid_records.append({
                    'row_idx': row_idx,
                    'timestamp': ts,
                    'order_id': row['order_id'].strip(),
                    'item': row['item'].strip(),
                    'qty': qty,
                    'unit_price': unit_price,
                    'total_inr': total_inr,
                    'payment_method': pay_method,
                    'milk_ml': milk_ml,
                    'eggs_raw': eggs_raw,
                    'eggs_boiled': eggs_boiled,
                    'notes': row.get('notes', '').strip()
                })
            except Exception as e:
                skipped_count += 1
                print(f"[SKIP ROW {row_idx}] Malformed record ({e}). Row: {row}", file=sys.stderr)

    if not valid_records:
        print("[FATAL] Zero valid data rows found in dataset.", file=sys.stderr)
        sys.exit(1)

    return valid_records, skipped_count


def analyze_sales_and_consumption(records):
    """Aggregates sales figures, payment methods, and ingredient burn rates."""
    total_revenue = 0.0
    cash_revenue = 0.0
    upi_revenue = 0.0
    total_orders = len(records)
    
    total_milk_ml = 0.0
    total_eggs_raw = 0
    total_eggs_boiled = 0
    item_breakdown = {}

    start_time = records[0]['timestamp']
    end_time = records[-1]['timestamp']
    duration_minutes = max(1.0, (end_time - start_time).total_seconds() / 60.0)

    for r in records:
        total_revenue += r['total_inr']
        if r['payment_method'] == 'CASH':
            cash_revenue += r['total_inr']
        else:
            upi_revenue += r['total_inr']

        total_milk_ml += r['milk_ml']
        total_eggs_raw += r['eggs_raw']
        total_eggs_boiled += r['eggs_boiled']

        item = r['item']
        if item not in item_breakdown:
            item_breakdown[item] = {'qty': 0, 'revenue': 0.0}
        item_breakdown[item]['qty'] += r['qty']
        item_breakdown[item]['revenue'] += r['total_inr']

    # Velocity metrics (per minute and extrapolated to 4-hour night shift: 8:00 PM - 12:00 AM)
    order_velocity_per_min = total_orders / duration_minutes
    revenue_velocity_per_min = total_revenue / duration_minutes
    milk_burn_rate_ml_min = total_milk_ml / duration_minutes

    return {
        'total_revenue': total_revenue,
        'cash_revenue': cash_revenue,
        'upi_revenue': upi_revenue,
        'total_orders': total_orders,
        'duration_minutes': duration_minutes,
        'order_velocity_per_min': order_velocity_per_min,
        'revenue_velocity_per_min': revenue_velocity_per_min,
        'milk_burn_rate_ml_min': milk_burn_rate_ml_min,
        'total_milk_ml': total_milk_ml,
        'total_eggs_raw': total_eggs_raw,
        'total_eggs_boiled': total_eggs_boiled,
        'item_breakdown': item_breakdown
    }


def compute_recommendations(analysis, 
                            shift_hours=4.0, 
                            milk_pouch_ml=DEFAULT_MILK_POUCH_VOLUME_ML,
                            milk_buffer=MILK_BUFFER_PERCENT,
                            surge_mult=PEAK_HOURS_SCALE_FACTOR,
                            boiled_egg_target_sl=BOILED_EGG_SERVICE_LEVEL):
    """
    Computes actionable inventory and cash guidance for the vendor's upcoming shift.
    Applies asymmetric perishability rules:
    - Milk pouches: discrete integers of 500ml pouches (open pouch will spoil if unused).
    - Boiled eggs: strict pre-boil batch limit to keep overnight waste under risk threshold.
    - Raw eggs: shelf-stable reserve recommendation.
    """
    shift_duration_min = shift_hours * 60.0

    # 1. Milk Optimization
    # Estimated milk needed for full 4-hr shift based on measured burn rate + surge multiplier + boiling loss buffer
    projected_milk_demand_ml = analysis['milk_burn_rate_ml_min'] * shift_duration_min * surge_mult * (1.0 + milk_buffer)
    # Milk comes in discrete 500ml pouches
    pouches_needed = math.ceil(projected_milk_demand_ml / milk_pouch_ml)
    procured_milk_ml = pouches_needed * milk_pouch_ml
    expected_unused_milk_ml = procured_milk_ml - projected_milk_demand_ml

    # 2. Egg Optimization (Split into Perishable Boiled vs Durable Raw)
    # Boiled egg demand rate
    boiled_per_min = analysis['total_eggs_boiled'] / analysis['duration_minutes']
    raw_per_min = analysis['total_eggs_raw'] / analysis['duration_minutes']

    projected_boiled_demand = boiled_per_min * shift_duration_min * surge_mult
    projected_raw_demand = raw_per_min * shift_duration_min * surge_mult

    # For pre-boiled eggs: Poisson/Newsvendor approximation.
    # To avoid discarding spoiled boiled eggs, do not boil 100% of projected demand at once.
    # Recommend initial batch (8:00 PM) capped at 65% of projected total, with a top-up rule at 10:00 PM only if stock < 3.
    recommended_initial_boil = max(6, math.ceil(projected_boiled_demand * 0.65))
    recommended_max_total_boil = math.ceil(projected_boiled_demand)
    
    # Raw eggs: come in crates of 30
    total_raw_eggs_needed = math.ceil(projected_raw_demand + projected_boiled_demand)
    raw_egg_crates = math.ceil(total_raw_eggs_needed / 30.0)

    # 3. Cash Float Guidance
    projected_cash_revenue = analysis['revenue_velocity_per_min'] * shift_duration_min * (analysis['cash_revenue'] / analysis['total_revenue'])
    recommended_cash_float = math.ceil((projected_cash_revenue * CASH_FLOAT_SAFETY_RATIO) / 50.0) * 50.0

    return {
        'shift_hours': shift_hours,
        'projected_milk_demand_ml': projected_milk_demand_ml,
        'pouches_needed': pouches_needed,
        'procured_milk_ml': procured_milk_ml,
        'expected_unused_milk_ml': expected_unused_milk_ml,
        'recommended_initial_boil': recommended_initial_boil,
        'recommended_max_total_boil': recommended_max_total_boil,
        'total_raw_eggs_needed': total_raw_eggs_needed,
        'raw_egg_crates': raw_egg_crates,
        'projected_cash_revenue': projected_cash_revenue,
        'recommended_cash_float': recommended_cash_float
    }


def print_cli_report(analysis, recs, skipped_count):
    """Outputs a clean, human-readable terminal dashboard for Manoj bhaiya and the reviewer."""
    divider = "=" * 68
    subdivider = "-" * 68

    print("\n" + divider)
    print("   MANOJ'S CART: NIGHT PREP & INVENTORY DECISION ADVISOR")
    print("   Vendor: Manoj Kumar | Location: Main Hostel Crossing")
    print(divider)

    print(f"\n[1] FIELD OBSERVATION SESSION METRICS")
    print(f"  • Observation Window: {analysis['duration_minutes']:.1f} minutes | Valid Orders Logged: {analysis['total_orders']}")
    if skipped_count > 0:
        print(f"  • Bad/Corrupt Rows Skipped: {skipped_count}")
    print(f"  • Total Session Revenue:  Rs. {analysis['total_revenue']:.2f}")
    print(f"    - Digital (UPI / Paytm): Rs. {analysis['upi_revenue']:.2f} ({(analysis['upi_revenue']/analysis['total_revenue'])*100:.1f}%)")
    print(f"    - Cash Receipts:         Rs. {analysis['cash_revenue']:.2f} ({(analysis['cash_revenue']/analysis['total_revenue'])*100:.1f}%)")
    print(f"  • Demand Pace:            {analysis['order_velocity_per_min']:.2f} orders/min  (Rs. {analysis['revenue_velocity_per_min']:.2f}/min)")

    print(f"\n[2] INGREDIENT BURN BREAKDOWN (During 25-min Window)")
    print(f"  • Milk Consumed:          {analysis['total_milk_ml']:.0f} mL (~{(analysis['total_milk_ml']/500):.2f} pouches)")
    print(f"  • Raw Eggs Cooked Live:   {analysis['total_eggs_raw']} eggs (Omelettes, Bhurji, Maggi)")
    print(f"  • Pre-Boiled Eggs Sold:   {analysis['total_eggs_boiled']} eggs")
    
    print(f"\n  Top Items Sold:")
    sorted_items = sorted(analysis['item_breakdown'].items(), key=lambda x: x[1]['qty'], reverse=True)
    for item_name, data in sorted_items[:5]:
        print(f"    - {item_name.replace('_', ' ').title():<18}: {data['qty']:>2} orders (Rs. {data['revenue']:.0f})")

    print("\n" + subdivider)
    hours_str = f"{recs['shift_hours']:.1f}".rstrip('0').rstrip('.')
    print(f"   ACTIONABLE PREP SHEET FOR TOMORROW'S SHIFT ({hours_str} HOURS)")
    print(subdivider)

    pouch_frac = recs['expected_unused_milk_ml'] / DEFAULT_MILK_POUCH_VOLUME_ML
    print(f"\n* MILK PROCUREMENT (Target: Zero overnight curdling after 10 PM dairy cutoff):")
    print(f"  >>> BUY EXACTLY: {recs['pouches_needed']} POUCHES ({DEFAULT_MILK_POUCH_VOLUME_ML}ml each, Total: {recs['procured_milk_ml']/1000:.1f} Liters)")
    print(f"      - Estimated Consumption: {recs['projected_milk_demand_ml']/1000:.2f} Liters (including {int(MILK_BUFFER_PERCENT*100)}% boiling buffer)")
    print(f"      - Estimated Leftover Risk: {recs['expected_unused_milk_ml']:.0f} mL ({pouch_frac:.2f} pouch safety margin)")

    print(f"\n* EGG PREPARATION (Asymmetric Perishability Rule):")
    print(f"  >>> 8:00 PM PRE-BOIL CAP:   BOIL ONLY {recs['recommended_initial_boil']} EGGS AT START")
    print(f"      (DO NOT boil all {recs['recommended_max_total_boil']} eggs at once! Unsold boiled eggs cannot be saved.)")
    print(f"  >>> 10:00 PM CHECKPOINT:    If <= 2 boiled eggs remain, boil 4 more; otherwise STOP.")
    print(f"  >>> RAW EGG STOCK TO KEEP:  {recs['total_raw_eggs_needed']} eggs (~{recs['raw_egg_crates']} crate of 30)")
    print(f"      (Raw eggs keep safely at room temperature with 0% overnight loss.)")

    print(f"\n* CASH TILL CHANGE / FLOAT ADVICE:")
    print(f"  >>> KEEP MINIMUM Rs. {recs['recommended_cash_float']:.0f} IN Rs. 10 & Rs. 20 COINS/NOTES AT OPENING")
    print(f"      (Prevents lost chai sales from change shortages when customers tender Rs. 50/100 notes.)")

    print("\n" + divider)
    print("   EXECUTION LIMITATIONS & WHAT THIS GETS WRONG:")
    print("   1. Weather Inelasticity: Sudden cold spells increase tea demand by 30-40%.")
    print("   2. Spillage Variance: Heavy wind on cart stove increases milk boil-over loss.")
    print("   3. Binary Cutoff: Assumes nearby dairy definitely closes at 10:00 PM.")
    print(divider + "\n")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Manoj Cart Inventory & Prep Advisor")
    parser.add_argument("--data", default="data/data.csv", help="Path to input CSV data file")
    parser.add_argument("--hours", type=float, default=4.0, help="Expected duration of evening shift in hours (default: 4.0)")
    parser.add_argument("--milk-buffer", type=float, default=MILK_BUFFER_PERCENT, help="Milk safety buffer fraction (default: 0.15)")
    parser.add_argument("--surge", type=float, default=PEAK_HOURS_SCALE_FACTOR, help="Late-night peak rush multiplier (default: 1.35)")
    args = parser.parse_args()

    # Resolve path relative to script directory or current working directory
    data_path = args.data
    if not os.path.exists(data_path):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        alt_path = os.path.join(script_dir, "..", args.data)
        if os.path.exists(alt_path):
            data_path = alt_path

    records, skipped_count = load_and_validate_data(data_path)
    analysis = analyze_sales_and_consumption(records)
    recs = compute_recommendations(
        analysis,
        shift_hours=args.hours,
        milk_buffer=args.milk_buffer,
        surge_mult=args.surge
    )
    print_cli_report(analysis, recs, skipped_count)


if __name__ == "__main__":
    main()
