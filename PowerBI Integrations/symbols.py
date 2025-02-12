import json
class Symbols:
    filePath = 'currencysymbol.json'
    @staticmethod
    def currencySymbol(filePath):
        with open(filePath, 'r', encoding='utf-8') as file:
            data = json.load(file)
        simplified_data = {country: info['currency_symbol'] for country, info in data.items()}
        return simplified_data