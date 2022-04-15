SOLID_UNIT_CONVERTIONS = {"To": 1000, "Kg": 1}


def convert_quantity_kg(quantity_unit, quantity):
    return SOLID_UNIT_CONVERTIONS.get(quantity_unit, 1000) * quantity
