# Step 4: Personal Reflection

### What I got wrong at the start
When I read the assignment prompt, my immediate engineering instinct was to treat this as a generic predictive inventory problem. I envisioned building a smartphone app with SQLite, or even training a regression model to forecast hourly demand. I also assumed that because eggs are perishable food, Manoj’s biggest headache would be cracked and spoiled eggs across the entire stock.

Going to the cart at 9:50 PM completely shattered those assumptions within ten minutes. 
First, watching Manoj cook under the dim tarp with soot, oil, and egg whites covering his hands showed me that any interactive mobile app is dead on arrival—he literally cannot swipe a capacitive screen while managing two boiling deghchis and four customers. 
Second, I was completely wrong about eggs. Raw eggs in trays don’t spoil in ambient temperature over 24–48 hours; Manoj just carries them over to the next morning. His real financial waste was strictly pre-boiled eggs and opened milk packets. He was taking the risk of boiling 15–20 eggs early in the evening to save 7 minutes of customer wait time, only to throw 6 of them away if the 11:00 PM hostel rush didn't materialize. That insight completely shifted my tool from an "egg predictor" to an "asymmetric perishability batch limiter."

### What I would cut if I had to redo this
I would completely cut the cash-float recommendation and customer grouping logic. 
While watching Manoj dig through his wooden change box for ₹35 when a customer gave a ₹50 note was an interesting observation, over 81% of his night revenue was actually collected through the Paytm QR code taped to his cart pole. The change-shortage problem, while annoying, doesn't threaten his working capital anywhere near the way ₹180 of curdled milk or discarded boiled eggs does. 
If I had only 2 hours, I would strip out every secondary metric and make the tool do exactly one thing: take the current time and remaining unopened milk pouches, and output a binary command: *"Open next pouch: YES / NO"*.

### Where AI helped, and where it wasted my time
**Where AI helped:**
AI was genuinely useful as a sounding board for the mathematical framing. When I explained Manoj’s operational constraints, the LLM immediately reminded me of the classical Newsvendor single-period problem with zero salvage value. That gave me the theoretical backing for treating opened milk vs unopened pouches as discrete integer constraints rather than a continuous linear burn rate. It also helped me write clean CSV schema validation and CLI parsing in standard library Python without pulling in external heavyweight libraries like Pandas.

**Where AI wasted time:**
AI wasted nearly 45 minutes of my time early on because its initial reflex was to over-engineer. When I first prompted it about inventory management for a street food stall, it hallucinated a full-stack architecture with FastAPI, React Native, and time-series ARIMA forecasting. It kept trying to include weather API integrations and historical seasonality trends, completely ignoring the constraint that I was collecting 25 data points on a single Tuesday night. I had to repeatedly push back and tell it: *"This man operates over an open flame with no laptop and no Wi-Fi. Give me a zero-dependency Python script that outputs a dead-simple prep sheet."* AI defaults to complexity; it took human intervention grounded in the physical cart to force it toward simplicity.
