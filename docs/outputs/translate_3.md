# 🧠 HyperCode Output: TRANSLATE

# 🛒 **HyperCode Spatial Logic: Cart Total Journey**

**Main Job:** Add up cart prices with VIP discount if stock is good. Start at zero ➡️ check each item ➡️ add smart price ➡️ end with total.[1][3]

## 📦 **Block 1: Grab Inputs**
- **Inputs:** Cart list (items) + user level (VIP or not).
- *What it does:* Sets up the shopping bags to scan.
- Flow: Inputs ➡️ zero counter.

```
📦 cart_items  📦 user_tier
```

## ⚙️ **Block 2: Zero Total**
- **Action:** Total starts empty (0).
- *What it does:* Fresh calculator pad.
- Flow: Inputs ➡️ 📦 total = 0 ➡️ scan loop.

```
📦 total = 0
```

## 🔄 **Block 3: Scan Each Item Loop**
- **Loop:** Visit every item in cart (🔄 one by one).
- *What it does:* Walk through shopping bag, skip empties.
- Flow: Zero total ➡️ 🔄 for each item ➡️ check stock ➡️ add price ➡️ next item.

```
🔄 for each 📦 item in cart_items:
```

## 🔀 **Block 4: Stock Check Gate**
- **Gate:** If item has stock? (Yes ➡️ price path | No ➡️ skip).
- *What it does:* Only grab stocked goodies.
- Flow: Loop ➡️ 🔀 item.in_stock? ➡️ VIP gate or normal add.

```
🔀 if item.in_stock:
```

## 🔀 **Block 5: VIP Discount Gate**
- **Gate:** VIP level? (Yes ➡️ 80% price | No ➡️ full price).
- *What it does:* VIP saves 20% on stocked items.
- Flow: Stock yes ➡️ 🔀 user_tier == 'VIP' ➡️ discount add ➡️ total.

**VIP Path:**
```
total += item.price * 0.8  🤑
```

**Normal Path:**
```
total += item.price  💰
```

## 🏁 **Block 6: Send Total Out**
- **Output:** Hand back the final number.
- *What it does:* Done shopping, get receipt.
- Flow: All loops + gates ➡️ return total.

```
return 📦 total
```

**Full Journey Map:**  
Inputs ➡️ Zero ➡️ 🔄 Loop Items ➡️ 🔀 Stock? ➡️ 🔀 VIP? ➡️ Add Price ➡️ 🏁 Total Out.[1][3]
