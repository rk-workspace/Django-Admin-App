def get_multiplier_kg(unit):
    if unit == 'GM':
        return 0.001
    if unit == 'MG':
        return 0.000001
    return 1
