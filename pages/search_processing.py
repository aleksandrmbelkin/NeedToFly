from datetime import datetime
import json
from typing import Dict, List, Optional


# Класс названий для вводимых гоородов вылета и прилета на русском и английском
class AirportSearcher:
    def __init__(self, file_path: str):
        self.airports_data = self.load_airports_data(file_path)
        self.indexes = self.build_search_indexes(self.airports_data)
        self.iata_to_city = self.build_iata_to_city_mapping(self.airports_data)
    
    @staticmethod
    def load_airports_data(file_path: str) -> List[Dict]:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    
    @staticmethod
    def build_search_indexes(airports_data: List[Dict]) -> Dict[str, Dict[str, str]]:
        city_ru_to_iata = {}
        city_en_to_iata = {}
        
        for airport in airports_data:
            iata = airport.get("code")
            if not iata:
                continue
            
            if "name" in airport and airport["name"]:
                city_ru_to_iata[airport["name"].lower()] = iata
            
            en_name = airport.get("name_translations", {}).get("en")
            if en_name:
                city_en_to_iata[en_name.lower()] = iata
        
        return {"ru": city_ru_to_iata, "en": city_en_to_iata}
    
    @staticmethod
    def build_iata_to_city_mapping(airports_data: List[Dict]) -> Dict[str, Dict[str, str]]:
        mapping = {}
        for airport in airports_data:
            iata = airport.get("code")
            if not iata:
                continue
            
            mapping[iata] = {
                "city_ru": airport.get("name"),
                "city_en": airport.get("name_translations", {}).get("en"),
                "country_code": airport.get("country_code")
            }
        return mapping
    
    def find_iata(self, city_name: str) -> Optional[str]:
        city_name = city_name.lower()
        return (
            self.indexes["ru"].get(city_name) or 
            self.indexes["en"].get(city_name)
        )
    
    def find_city_by_iata(self, iata_code: str, lang: str = "ru") -> Optional[str]:
        airport_info = self.iata_to_city.get(iata_code.upper())

        if not airport_info:
            return ''
        
        if lang == "en":
            return airport_info.get("city_en")
        
        if airport_info.get("city_ru"):
            return airport_info.get("city_ru")
        else:
            return airport_info.get("city_en")


def get_logo(iata):
    return f"https://content.airhex.com/content/logos/airlines_{iata}_200_100_r.png"


def split_datetime(date):
    dt = datetime.fromisoformat(date)

    return {
        "date": dt.strftime("%d.%m.%Y"),
        "time": dt.strftime("%H:%M")
    }


searcher = AirportSearcher('db/airports.json')
classes = {'Эконом': 'ECONOMY', 
           'Эконом+': 'PREMIUM_ECONOMY', 
           'Бизнесс': 'BUSINESS', 
           'Первый': 'FIRST'}
