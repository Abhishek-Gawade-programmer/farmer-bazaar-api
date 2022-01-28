SOLID_UNIT_CONVERTIONS = {"To": 100_00_00, "Kg": 1000, "Gr": 1}


def convert_quantity_gram(quantity_unit, quantity):
    return SOLID_UNIT_CONVERTIONS.get(quantity_unit, 1000) * quantity
