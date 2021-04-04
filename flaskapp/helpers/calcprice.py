def calculate_price(distance, pricePerMile, weight, productType):
    if productType == "fragile":
        pricePerMile += 0.05
    
    elif productType == "flammable":
        pricePerMile += 0.1
    
    elif productType == "toxic":
        pricePerMile += 0.09
    
    elif productType == "corrosive":
        pricePerMile += 0.07
        
    price = pricePerMile * distance * weight
    
    return price
    
    
    