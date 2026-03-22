# 🎨 HyperCode Translation: Task 17

# HyperCode Spatial Logic: Shopping Cart Processor

## 🎯 What This Code Does (Plain English)
This code **calculates your total shopping bill**, checking if items are actually available and giving VIP customers a 20% discount.

---

## 🗺️ The Visual Journey

**Start** ➡️ 📦 Create empty total ➡️ 🔄 Loop through each item ➡️ 🔀 Check if in stock ➡️ 🔀 Check if VIP ➡️ ⚙️ Calculate price ➡️ **End with final total**

---

## 🧱 Breaking It Into Blocks

### Block 1: 📦 The Setup
```
Create a box called "total"
Put 0 inside it (starting amount)
```

### Block 2: 🔄 The Loop (Do This For Each Item)
```
Pick up one item from the cart
Ask: "Is this item actually in stock?"
  ↓ YES → Go to Block 3
  ↓ NO → Skip this item, grab the next one
```

### Block 3: 🔀 The VIP Check
```
Ask: "Is this customer a VIP?"
  ↓ YES → Go to Block 4A (VIP pricing)
  ↓ NO → Go to Block 4B (regular pricing)
```

### Block 4A: ⚙️ VIP Discount Math
```
Take the item's price
Multiply by 0.8 (that's 80% of the price = 20% off)
Add the discounted price to your total box
```

### Block 4B: ⚙️ Regular Pricing
```
Take the item's price as-is
Add it to your total box
```

### Block 5: 🎁 The Result
```
Hand back the final total
(This is what the customer owes)
```

---

## 🚫 What You Don't Need to Know
- `def`, `return`, `==` — these are just syntax noise
- The code structure itself handles the repetition; you just need to understand the *logic flow*
