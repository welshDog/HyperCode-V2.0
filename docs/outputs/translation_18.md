# 🎨 HyperCode Translation: Task 18

# 🛒 **HyperCode Spatial Logic: Cart Total Journey**

**Main Job:** Grabs cart stuff + user level ➡️ Crunches numbers ➡️ Spits out final bill.  
*Visual Start:* 📦 Cart items + 📦 User tier → Enter **Process Gate** ➡️ Exit with total cash.

## 🧱 **Block 1: Setup Zero**  
📦 **Total** = 0  
*What it does:* Fresh counter. No junk. Ready for adds.

## 🧱 **Block 2: 🔄 Item Hunt Loop**  
🔄 **For each** item in 📦 cart_items:  
*Journey:* Dive into cart bag ➡️ Grab one item ➡️ Check it ➡️ Add to total ➡️ Next item ➡️ Repeat till empty.

## 🧱 **Block 3: 🔀 Stock Check Gate**  
🔀 **If** item.in_stock = yes:  
*What it does:* Skip empty shelves. Only real items count.  
*Flow:* Block 2 ➡️ Hits gate ➡️ Green light ➡️ Jump to discount check ➡️ Else: Skip ➡️ Back to loop.

## 🧱 **Block 4: 🔀 VIP Discount Gate**  
🔀 **If** 📦 user_tier = "VIP":  
📦 **Total** += item.price * 0.8  *(20% off!)*  
**Else:**  
📦 **Total** += item.price  *(Full price)*  
*What it does:* VIPs pay less. Normals pay full. Pile on the total.  
*Flow:* Block 3 ➡️ VIP gate ➡️ Discount math ➡️ Add ➡️ Back to loop.

## 🧱 **Block 5: Exit Handover**  
**Return** 📦 total  
*Journey End:* All loops done ➡️ Full total ready ➡️ Hand off to world.

**Full Path Map:**  
**Start** (cart + tier) ➡️ **Block1** (zero total) ➡️ **🔄 Block2** (item loop) ➡️ **🔀 Block3** (stock?) ➡️ **🔀 Block4** (VIP?) ➡️ Loop back ➡️ **Block5** (return total).  
*Pro Tip:* Only stocked items add up. VIP magic slashes 20%.[1][2]