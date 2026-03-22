# 🎨 HyperCode Translation: Task 19

# 🏠 **HyperCode Spatial Logic: Mortgage Calculator**

## **Block 1: Money Math Machine** ⚙️ *calculate_mortgage*
**Inputs:** 📦 Big loan amount (principal), 📦 Yearly interest (rate), 📦 Years to pay (years)

**Journey:**  
📦 **Grab loan basics** ➡️ Turn yearly rate to monthly (divide by 100, then 12) ➡️ 📦 Count total months (years x 12)  

🔀 **Zero interest check?** ➡️ If yes: Split loan evenly over months ➡️ **Exit with answer**  

🔄 **Math power-up:**  
- Top: Monthly rate x (1 + rate) raised to total months  
- Bottom: (1 + rate) raised to total months, minus 1  
- **Payment:** Loan x (top / bottom)  

🖨️ **Shout result** ➡️ **Hand back payment number**  

**Visual Flow:**  
```
Principal + Rate + Years 
       ↓
📦 Monthly rate & months 
       ↓
🔀 Zero? → Simple split 
       ↓ No
Math: Top / Bottom x Loan 
       ↓
🖨️ Print → Return
```

## **Block 2: Wallet Check Gate** ⚙️ *check_affordability*
**Inputs:** 📦 Your salary, 📦 Monthly payment  

**Journey:**  
🔀 **Safe rule:** 30% of salary max for payment?  
- Payment > (salary x 0.3) ➡️ 🖨️ "Too expensive!" ➡️ **Return ❌ False**  
- Else ➡️ 🖨️ "You can afford it." ➡️ **Return ✅ True**  

**Visual Flow:**  
```
Salary + Payment 
       ↓
🔀 > 30% salary? 
  Yes → ❌ Print Bad 
  No  → ✅ Print Good
```

**Full Map:** Block 1 ➡️ Crunches numbers ➡️ Passes payment ➡️ Block 2 ➡️ Checks wallet fit[1][2]
