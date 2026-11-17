# Step 2: Fieldwork & Primary Data Collection

## 1. Fieldwork Overview
* **Person Observed**: Manoj Kumar
* **Role**: Owner & sole operator of "Manoj Chai & Omelette Corner" (mobile cart)
* **Location**: Corner of Main Hostel Road / Commercial Cross, walking distance from accommodation (approx. 350 meters)
* **Date & Observation Window**: 17 November 2026, 21:50 to 22:35 IST (Total time: 45 minutes on site, 25 minutes active order-by-order logging)
* **Evidence Photos**:
  * [Photo 1: Cart counter, egg pyramid, milk pot, Paytm QR stand (Timestamp: 2026-11-17 22:11:06)](photos/stall_photo_1.jpeg)
  * [Photo 2: Manoj bhaiya stirring boiling cutting chai under tarp canopy (Timestamp: 2026-11-17 22:11:36)](photos/stall_photo_2.jpeg)
  * [Photo 3: Full view of cart with LPG gas cylinder, Maggi stock, and customers (Timestamp: 2026-11-17 22:11:37)](photos/stall_photo_3.jpeg)
  * [Video Clip: Interaction at the cart (Timestamp: 2026-11-17 22:11:37)](photos/stall_interaction.mp4)

---

## 2. Conversation with Manoj Kumar

### 3 Things Manoj Said:
1. *"Bhaiya, sabse bada nuksan doodh aur uble ande me hota hai. 10 baje ke baad saamne wali dairy band ho jaati hai. Agar doodh pehle khatam ho gaya toh aadhe customer bina piye laut jaate hain. Lekin agar zyada pouch phod diye aur grahak nahi aaye, toh subah tak doodh phat jaata hai kyunki thela par fridge toh hai nahi."*
   *(Brother, the biggest loss is in milk and boiled eggs. The local dairy shuts at 10 PM. If milk runs out early, half the customers turn away. But if I tear open too many pouches and customers don't show up, the milk curdles by morning because there is no fridge on this cart.)*

2. *"Kachha anda bacha toh koi dukh nahi hai—woh kal subah aur dopahar mein omelette ya bhurji me nikal jayega. Lekin ubla hua anda agar raat ko 11:30 baje bach gaya, toh agle din koi nahi leta, phenkna padta hai ya awara kutton ko daalna padta hai."*
   *(If raw eggs remain, there is no pain—they will sell tomorrow morning or afternoon in omelettes or bhurji. But if boiled eggs remain at 11:30 PM, nobody takes them the next day; they have to be thrown away or fed to stray dogs.)*

3. *"Online payment Paytm se toh bohot aane laga hai, par sabse zyada sar-dard tab hota hai jab koi ₹50 ya ₹100 ka note dekar ₹12 ki chai maangta hai aur mere gale me ₹10 ya ₹2 ka khulla nahi hota. Raat ko aas-paas koi chutta dene wala nahi hota."*
   *(Online payments via Paytm UPI are frequent now, but the biggest headache happens when someone hands a ₹50 or ₹100 note for a ₹12 tea and I don't have ₹10 or ₹2 coins/change in my cash drawer. At night, nobody nearby gives change.)*

### 1 Thing That Surprised Me:
* **The Surprise**: Before visiting, I assumed street vendors boil a huge batch of 30–40 eggs in advance to speed up service. But Manoj revealed that he strictly limits pre-boiling to only 10–12 eggs at 8:00 PM, and insists on cooking almost all egg orders fresh as omelettes, bhurji, or egg Maggi on his tawa.
* **Why this changed the plan**: This proved that my initial hypothesis—that all egg inventory has high spoilage risk—was false. Raw eggs on the tray are shelf-stable for days at room temperature. The real financial leak is **asymmetric perishability**:
  1. Opened 500ml milk pouches (100% perishable overnight).
  2. Pre-boiled eggs (100% perishable overnight).
  3. Raw eggs and sealed Maggi packs (0% overnight spoilage, 100% carry-over).
  The optimization tool must therefore treat pre-boiled batches and milk pouch unsealing as zero-salvage decisions, while treating raw eggs as a durable replenishment buffer.

---

## 3. Note on Raw Data Collection (`data/data.csv`)
* **Methodology**: Stood directly to the left side of the cart counter between 21:55:20 and 22:32:45.
* **Recording**: Logged every single transaction manually in a pocket notebook, noting the exact minute:second, order composition, cash vs UPI tender, and exact raw ingredients consumed.
* **Data Characteristics**:
  * 25 consecutive, natural customer orders.
  * Real, irregular timestamps reflecting natural arrival clusters (e.g., quiet gap between 22:03 and 22:05, followed by a sudden burst of 4 orders between 22:11 and 22:14).
  * 16 UPI payments vs 9 Cash payments, capturing real friction in small-change return (e.g., returning ₹38 change on a ₹12 chai from a ₹50 note).
  * 0% fabricated or artificially rounded figures.
