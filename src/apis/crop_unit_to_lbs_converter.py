CONVERSION_TABLE = {
    '': 0,
    'Cwt': 100,
    'Tons': 2000,
    'AUM': 750,
    'Bu': {
        'Dry peas': 60,
        'Improved bermudagrass': 40,
        'Wheat': 60,
        'Winter wheat': 60,
        'Dry beans': 60,
        'Alfalfa hay': 60,
        'Peppers': 25,
        'Table grapes': 44,
        'Cool-season grasses': 20,
        'Barley': 48,
        'Green peas': 30,
        'Apricots': 48,
        'Apples': 42,
        'Tomatoes': 53,
        'Dry lima beans': 56,
        'Plums': 56,
        'Snap beans': 28,
        'Alfafa': 60,
        'Grass-legume pasture': 20,
        'Rice': 45,
        'Flax': 56,
        'Millet': 50,
        'Grain sorghum': 56,
        'Corn': 56,
        'Pears': 50,
        'Carrots': 50,
        'Cherries': 56,
        'Winter wheat-fallow': 60,
        'Oats': 32,
        'Soybeans': 60,
        'Grass hay': 20,
        'Pasture': 30,
        'Grass-legume hay': 15,
        'Spring wheat-fallow': 60,
        'Peaches': 48,
        'Improved bermudagrass hay': 12,
        'Rye': 56,
        'Artichokes': 22,
        'Timothy-red clover hay': 13,
        'Spring wheat': 60,
        'Cotton lint': 15,
        'Unshelled lima beans': 30,
        'Sugar beets': 52,
        'Corn silage ': 76,
        'Spring canola': 50
    },
    'Thousands': {
        'Coconuts': 3000,
        'Grapefruit': 617.294,
        'Oranges': 396.832,
        'Plantains': 617.294,
        'Strawberry plants': 1500
    },
    'Boxes': {
        'Lemons': 80,
        'Avocados': 25,
        'Oranges': 40,
        'Grapefruit': 85,
        'Oats': 1600,
        'Tangerines': 80
    },
    'Crates': {
        'Asparagus': 32,
        'Brussel sprouts': 25,
        'Cabbage': 53,
        'Cantaloupe': 38,
        'Cauliflower': 50,
        'Celery': 55,
        'Lettuce': 40,
        'Pecans': 15,
        'Soybeans': 60,
        'Strawberries': 36
    }
}

def crop_unit_to_lbs(crop: str, input_unit: str, input_value: float):
    if not input_unit in CONVERSION_TABLE:
        raise ValueError(f'Unknown input_unit {input_unit}')

    input_table_or_value = CONVERSION_TABLE[input_unit]
    if isinstance(input_table_or_value, dict):
        if not crop in input_table_or_value:
            raise ValueError(f'Unknown crop {crop} for input_unit {input_unit}')
        return input_table_or_value[crop] * input_value
    else:
        return input_table_or_value * input_value
