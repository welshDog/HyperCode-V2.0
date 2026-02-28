def calculate_mortgage(principal, rate, years):
    # This is a messy function to calculate monthly payments
    r = rate / 100 / 12
    n = years * 12
    
    if r == 0:
        return principal / n
        
    top = r * ((1 + r) ** n)
    bottom = ((1 + r) ** n) - 1
    
    payment = principal * (top / bottom)
    
    print("Your payment is: " + str(payment))
    return payment

def check_affordability(salary, payment):
    if payment > (salary * 0.3):
        print("Too expensive!")
        return False
    else:
        print("You can afford it.")
        return True
