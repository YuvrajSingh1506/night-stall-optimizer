# Step 1: Problem Definition and Research

## 1. The Problem (in 5 lines)
1. Roadside night tea and egg stalls operate entirely without refrigeration or cold storage, relying on open ambient carts with extreme heat from LPG burners.
2. Perishable ingredients—specifically unsealed 500ml milk pouches and pre-boiled eggs—spoil within 4–6 hours in ambient night heat and must be discarded if unsold by close (11:30 PM).
3. Conversely, running out of milk or eggs during the 10:00 PM–11:15 PM peak rush causes immediate lost sales because wholesale dairies and local kiranas shut by 10:00 PM.
4. The cart owner (Manoj Kumar) currently guesses his evening prep by gut feeling, regularly resulting in either ₹150–₹250 nightly spoilage or closing up to 45 minutes prematurely.
5. What is needed is an offline, low-friction inventory decision rule that recommends the exact milk pouch procurement and pre-boiled egg batch count based on real peak-hour velocity.

---

## 2. Existing Solutions and Why They Do Not Fit

### Solution 1: Mobile POS & Khata Inventory Apps (e.g., Vyapar, Khatabook, Petpooja)
* **What they do**: Provide smartphone-based point-of-sale inventory tracking where every item sold is logged digitally to decrement raw material stock.
* **Why it does not fit Manoj**: Manoj runs a one-man cart. While cooking over two open burners, his hands are coated in egg yolk, butter, water, and soot. Stopping to unlock an Android phone, navigate multi-tiered touch menus, and log each ₹12 cutting chai or ₹25 omelette while three customers wait in line creates an intolerable bottleneck. Furthermore, these apps assume continuous re-ordering, ignoring the hard cutoff when local dairy suppliers shut down at 10 PM.

### Solution 2: Standard Economic Order Quantity (EOQ) & Safety Stock Formulas
* **What they do**: Classical operations research formulas compute optimal order quantities balancing ordering costs against inventory holding costs.
* **Why it does not fit Manoj**: Traditional holding cost models assume preserved inventory carry-over with moderate depreciation. For an open street cart with no refrigerator, the holding cost of opened milk and pre-boiled eggs overnight is binary (100% total loss). Additionally, EOQ assumes stable, continuous replenishment lead times; here, lead time between 10:00 PM and 7:00 AM is effectively infinite (zero supplier availability). Applying textbook EOQ leads to chronic over-ordering of perishables.

---

## 3. Sources Actually Read

### Source 1: WIEGO (Women in Informal Employment: Globalizing and Organizing) & ILO Research on Urban Street Food Vendors in India
* **Reference**: Bhowmik, S. K., *Street Vendors in the Global Urban Economy*, Routledge India / WIEGO Research Series on Informal Micro-Enterprises.
* **3-Line Note**:
  1. Documents that urban Indian street food carts operate on tight daily rolling working capital (₹1,500–₹3,500) where raw materials consume 60–70% of gross daily receipts.
  2. Demonstrates that perishable inventory losses (milk, prepared batters, boiled items) directly cannibalize the next morning's wholesale buying power, trapping vendors in debt cycles.
  3. Recommends that interventions for solo vendors must prioritize "zero write-off heuristics" over complex predictive software.

### Source 2: Classical Perishable Inventory Theory — The Newsvendor (Single-Period) Problem
* **Reference**: Porteus, E. L., *Foundations of Stochastic Inventory Theory*, Stanford University Press (Chapter 2: The Newsvendor Problem with Zero Salvage Value).
* **3-Line Note**:
  1. Formulates the mathematical balance between Underage Cost ($C_u = \text{Lost Margin} = \text{Selling Price} - \text{Cost Price}$) and Overage Cost ($C_o = \text{Direct Purchase Cost} - \text{Salvage Value}$).
  2. Proves that for zero salvage value items (spoiled milk and discarded boiled eggs, where $C_o = \text{Full Cost}$), the optimal service level is strictly bounded by the critical ratio $\frac{C_u}{C_u + C_o}$.
  3. Showed me that raw eggs (shelf-stable carryover, salvage value = 100%) and boiled eggs (zero salvage value = 0%) must be mathematically treated as two distinct inventory classes rather than a single "egg" pool.
