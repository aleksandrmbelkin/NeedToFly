from amadeus import Client, ResponseError
from dotenv import dotenv_values
import flask
from flask import render_template, redirect
from forms.searchform import SearchForm
import isodate
from pages.search_processing import *

blueprint = flask.Blueprint(
    'search',
    __name__,
    template_folder='templates'
)

@blueprint.route('/search', methods=['GET', 'POST'])
def search():
    form = SearchForm()
    if form.submit.data:
        form.originLocationCode.data = form.originLocationCode.data.strip()
        form.destinationLocationCode.data = form.destinationLocationCode.data.strip()

        departure_town = searcher.find_iata(form.originLocationCode.data)
        arrive_town = searcher.find_iata(form.destinationLocationCode.data)

        # Ошибки
        if departure_town == None or arrive_town == None:
            return render_template('search.html', title='Поиск авиабилетов',
                                    header=True, form=form, message='Город не существует или не имеет аэропорота')
        elif departure_town.lower() ==  arrive_town.lower():
            return render_template('search.html', title='Поиск авиабилетов',
                                    header=True, form=form, message='Аэропорт прибытия не может быть такой же, как аэропорт вылета')
        elif form.returnDate.data and form.departureDate.data > form.returnDate.data:
            return render_template('search.html', title='Поиск авиабилетов',
                                    header=True, form=form, message='Дата возвращения не может быть раньше, чем дата вылета')
        elif int(form.adults.data) + int(form.children.data) > 9:
            return render_template('search.html', title='Поиск авиабилетов',
                                    header=True, form=form, message='Колличество взрослых и детей вместе не должно превышать 9')
        elif int(form.adults.data) < int(form.infants.data):
            return render_template('search.html', title='Поиск авиабилетов',
                                    header=True, form=form, message='Младенцев не может быть больше, чем взрослых')
        
        # Проверка на наличие пересадок
        nonStop = 'false'
        if form.nonStop.data:
            nonStop = 'true'

        info = []
        config = dotenv_values('.env')
        amadeus = Client(client_id=config['AMADEUS_CLIENT_ID'], client_secret=config['AMADEUS_CLIENT_SECRET'])
        
        # Запрос к амадеусу, если билет в один конец
        if not form.returnDate.data:
            type = 'one-way'
            response = amadeus.shopping.flight_offers_search.get(
                    originLocationCode=str(departure_town),
                    destinationLocationCode=str(arrive_town),

                    departureDate=str(form.departureDate.data),

                    adults=str(form.adults.data),
                    children=str(form.children.data),
                    infants=str(form.infants.data),

                    travelClass=classes[form.travelClass.data],
                    nonStop=nonStop
                )
            
            # Обработка запроса и составление списка с билетами и нужной в них информации

            # Без пересадок
            if form.nonStop.data:
                for flight in response.data:
                    duration = isodate.parse_duration(flight['itineraries'][0]['duration'])
                    aviacompany_name = response.result['dictionaries']['carriers'][flight['itineraries'][0]['segments'][0]['carrierCode']]
                    aircraft = response.result['dictionaries']['aircraft'][flight['itineraries'][0]['segments'][0]['aircraft']['code']]
                    
                    baggage = {}
                    if 'includedCheckedBags' in flight['travelerPricings'][0]['fareDetailsBySegment'][0]:
                        if "quantity" in flight['travelerPricings'][0]['fareDetailsBySegment'][0]['includedCheckedBags']:
                            baggage['includedCheckedBags'] = f'Багаж*: {flight['travelerPricings'][0]['fareDetailsBySegment'][0]['includedCheckedBags']['quantity']} шт.'
                        elif "weight" in flight['travelerPricings'][0]['fareDetailsBySegment'][0]['includedCheckedBags']:
                            baggage['includedCheckedBags'] = f'Багаж*: {flight['travelerPricings'][0]['fareDetailsBySegment'][0]['includedCheckedBags']['weight']} {flight['travelerPricings'][0]['fareDetailsBySegment'][0]['includedCheckedBags']['weightUnit']}'
                    else:
                        baggage['includedCheckedBags'] = 'Без багажа'
                    
                    if 'includedCabinBags' in flight['travelerPricings'][0]['fareDetailsBySegment'][0]:
                        if "quantity" in flight['travelerPricings'][0]['fareDetailsBySegment'][0]['includedCabinBags']:
                            baggage['includedCabinBags'] = f'Ручная кладь*: {flight['travelerPricings'][0]['fareDetailsBySegment'][0]['includedCabinBags']['quantity']} шт.'
                        elif "weight" in flight['travelerPricings'][0]['fareDetailsBySegment'][0]['includedCabinBags']:
                            baggage['includedCabinBags'] = f'Ручная кладь*: {flight['travelerPricings'][0]['fareDetailsBySegment'][0]['includedCabinBags']['weight']} {flight['travelerPricings'][0]['fareDetailsBySegment'][0]['includedCabinBags']['weightUnit']}'
                    else:
                        baggage['includedCabinBags'] = 'Без ручной клади'
                    
                    depart_town = searcher.find_city_by_iata(flight['itineraries'][0]['segments'][0]['departure']['iataCode']) or form.originLocationCode.data
                    arriv_town = searcher.find_city_by_iata(flight['itineraries'][0]['segments'][-1]['arrival']['iataCode']) or form.destinationLocationCode.data
                    
                    info.append({"duration": f"{duration.seconds // 3600} часов {duration.seconds % 3600 // 60} минут",
                                 'segments': [
                                     {'departure': 
                                         {'town': depart_town,
                                          'iataCode' : flight['itineraries'][0]['segments'][0]['departure']['iataCode'],
                                          'at': split_datetime(flight['itineraries'][0]['segments'][0]['departure']['at'])},
                                     'arrival': 
                                         {'town': arriv_town,
                                          'iataCode' : flight['itineraries'][0]['segments'][0]['arrival']['iataCode'],
                                          'at': split_datetime(flight['itineraries'][0]['segments'][0]['arrival']['at'])},
                                     'aviacompany' : {'name': aviacompany_name,
                                         'logo': get_logo(flight['itineraries'][0]['segments'][0]['carrierCode']),
                                         'aircraft': aircraft}}],
                                  'price': {'currency': flight['price']['currency'], 'base': str(flight['price']['base'])},
                                  'travelClass': classes[form.travelClass.data],
                                  'place': str(form.adults.data + form.children.data),
                                  'bagage': baggage})
            
            # С пересадками
            else:
                for flight in response.data:
                    duration = isodate.parse_duration(flight['itineraries'][0]['duration'])
                    aviacompany_name = response.result['dictionaries']['carriers'][flight['itineraries'][0]['segments'][0]['carrierCode']]
                    aircraft = response.result['dictionaries']['aircraft'][flight['itineraries'][0]['segments'][0]['aircraft']['code']]
                    
                    baggage = {}
                    if 'includedCheckedBags' in flight['travelerPricings'][0]['fareDetailsBySegment'][0]:
                        if "quantity" in flight['travelerPricings'][0]['fareDetailsBySegment'][0]['includedCheckedBags']:
                            baggage['includedCheckedBags'] = f'Багаж*: {flight['travelerPricings'][0]['fareDetailsBySegment'][0]['includedCheckedBags']['quantity']} шт.'
                        elif "weight" in flight['travelerPricings'][0]['fareDetailsBySegment'][0]['includedCheckedBags']:
                            baggage['includedCheckedBags'] = f'Багаж*: {flight['travelerPricings'][0]['fareDetailsBySegment'][0]['includedCheckedBags']['weight']} {flight['travelerPricings'][0]['fareDetailsBySegment'][0]['includedCheckedBags']['weightUnit']}'
                    else:
                        baggage['includedCheckedBags'] = 'Без багажа*'
                    
                    if 'includedCabinBags' in flight['travelerPricings'][0]['fareDetailsBySegment'][0]:
                        if "quantity" in flight['travelerPricings'][0]['fareDetailsBySegment'][0]['includedCabinBags']:
                            baggage['includedCabinBags'] = f'Ручная кладь*: {flight['travelerPricings'][0]['fareDetailsBySegment'][0]['includedCabinBags']['quantity']} шт.'
                        elif "weight" in flight['travelerPricings'][0]['fareDetailsBySegment'][0]['includedCabinBags']:
                            baggage['includedCabinBags'] = f'Ручная кладь*: {flight['travelerPricings'][0]['fareDetailsBySegment'][0]['includedCabinBags']['weight']} {flight['travelerPricings'][0]['fareDetailsBySegment'][0]['includedCabinBags']['weightUnit']}'
                    else:
                        baggage['includedCabinBags'] = 'Без ручной клади*'

                    way = []
                    for segment in flight['itineraries'][0]['segments']:
                        way.append({'departure': 
                                        {'town': searcher.find_city_by_iata(segment['departure']['iataCode']),
                                        'iataCode' : segment['departure']['iataCode'],
                                        'at': split_datetime(segment['departure']['at'])},
                                    'arrival': 
                                        {'town': searcher.find_city_by_iata(segment['arrival']['iataCode']),
                                        'iataCode' : segment['arrival']['iataCode'],
                                        'at': split_datetime(segment['arrival']['at'])},
                                    'aviacompany' : {'name': aviacompany_name,
                                        'logo': get_logo(segment['carrierCode']),
                                        'aircraft': aircraft},
                                    'duration': f"{isodate.parse_duration(segment['duration']).seconds // 3600} часов {isodate.parse_duration(segment['duration']).seconds % 3600 // 60} минут"})
                        
                    info.append({'id': int(flight['id']) - 1,
                                "duration": f"{duration.seconds // 3600} часов {duration.seconds % 3600 // 60} минут",
                                'segments': way,
                                'price': {'currency': flight['price']['currency'], 'base': str(flight['price']['base'])},
                                'travelClass': classes[form.travelClass.data],
                                'place': str(form.adults.data + form.children.data),
                                'bagage': baggage})
                    
                    depart_town = searcher.find_city_by_iata(flight['itineraries'][0]['segments'][0]['departure']['iataCode']) or form.originLocationCode.data
                    arriv_town = searcher.find_city_by_iata(flight['itineraries'][0]['segments'][-1]['arrival']['iataCode']) or form.destinationLocationCode.data

                    info[int(flight['id']) - 1]['segments'][0]['departure']['town'] = depart_town
                    info[int(flight['id']) - 1]['segments'][-1]['arrival']['town'] = arriv_town

        # Запрос к амадеусу, если билет - туда-обратно
        else:
            type = 'round-trip'
            response = amadeus.shopping.flight_offers_search.get(
                    originLocationCode=str(departure_town),
                    destinationLocationCode=str(arrive_town),

                    departureDate=str(form.departureDate.data),
                    returnDate=str(form.returnDate.data),

                    adults=str(form.adults.data),
                    children=str(form.children.data),
                    infants=str(form.infants.data),

                    travelClass=classes[form.travelClass.data],
                    nonStop=nonStop
                )
            
            itineraries = [{}, {}]
            # Без пересадок
            if form.nonStop.data:
                for flight in response.data:
                    for i in range(2):
                        itineraries[i]['duration'] = isodate.parse_duration(flight['itineraries'][i]['duration'])
                        itineraries[i]['aviacompany_name'] = response.result['dictionaries']['carriers'][flight['itineraries'][i]['segments'][0]['carrierCode']]
                        itineraries[i]['aircraft'] = response.result['dictionaries']['aircraft'][flight['itineraries'][i]['segments'][0]['aircraft']['code']]
                        
                        baggage = {}
                        if 'includedCheckedBags' in flight['travelerPricings'][0]['fareDetailsBySegment'][0]:
                            if "quantity" in flight['travelerPricings'][0]['fareDetailsBySegment'][0]['includedCheckedBags']:
                                baggage['includedCheckedBags'] = f'Багаж*: {flight['travelerPricings'][0]['fareDetailsBySegment'][0]['includedCheckedBags']['quantity']} шт.'
                            elif "weight" in flight['travelerPricings'][0]['fareDetailsBySegment'][0]['includedCheckedBags']:
                                baggage['includedCheckedBags'] = f'Багаж*: {flight['travelerPricings'][0]['fareDetailsBySegment'][0]['includedCheckedBags']['weight']} {flight['travelerPricings'][0]['fareDetailsBySegment'][0]['includedCheckedBags']['weightUnit']}'
                        else:
                            baggage['includedCheckedBags'] = 'Без багажа'
                        
                        if 'includedCabinBags' in flight['travelerPricings'][0]['fareDetailsBySegment'][0]:
                            if "quantity" in flight['travelerPricings'][0]['fareDetailsBySegment'][0]['includedCabinBags']:
                                baggage['includedCabinBags'] = f'Ручная кладь*: {flight['travelerPricings'][0]['fareDetailsBySegment'][0]['includedCabinBags']['quantity']} шт.'
                            elif "weight" in flight['travelerPricings'][0]['fareDetailsBySegment'][0]['includedCabinBags']:
                                baggage['includedCabinBags'] = f'Ручная кладь*: {flight['travelerPricings'][0]['fareDetailsBySegment'][0]['includedCabinBags']['weight']} {flight['travelerPricings'][0]['fareDetailsBySegment'][0]['includedCabinBags']['weightUnit']}'
                        else:
                            baggage['includedCabinBags'] = 'Без ручной клади'
                        
                    info.append({'itineraries': [
                                    {"duration": f"{itineraries[0]['duration'].seconds // 3600} часов {itineraries[0]['duration'].seconds % 3600 // 60} минут",
                                     'segments': [
                                         {'departure': 
                                             {'town': form.originLocationCode.data,
                                             'iataCode' : flight['itineraries'][0]['segments'][0]['departure']['iataCode'],
                                             'at': split_datetime(flight['itineraries'][0]['segments'][0]['departure']['at'])},
                                         'arrival': 
                                             {'town': form.destinationLocationCode.data,
                                             'iataCode' : flight['itineraries'][0]['segments'][0]['arrival']['iataCode'],
                                             'at': split_datetime(flight['itineraries'][0]['segments'][0]['arrival']['at'])},
                                         'aviacompany' : {'name': itineraries[0]['aviacompany_name'],
                                             'logo': get_logo(flight['itineraries'][0]['segments'][0]['carrierCode']),
                                             'aircraft': itineraries[0]['aircraft']}}]},
                                    
                                    {"duration": f"{itineraries[1]['duration'].seconds // 3600} часов {itineraries[1]['duration'].seconds % 3600 // 60} минут",
                                     'segments': [
                                         {'departure': 
                                             {'town': form.destinationLocationCode.data,
                                             'iataCode' : flight['itineraries'][1]['segments'][0]['departure']['iataCode'],
                                             'at': split_datetime(flight['itineraries'][1]['segments'][0]['departure']['at'])},
                                         'arrival': 
                                             {'town': form.originLocationCode.data,
                                             'iataCode' : flight['itineraries'][1]['segments'][0]['arrival']['iataCode'],
                                             'at': split_datetime(flight['itineraries'][1]['segments'][0]['arrival']['at'])},
                                         'aviacompany' : {'name': itineraries[1]['aviacompany_name'],
                                             'logo': get_logo(flight['itineraries'][1]['segments'][0]['carrierCode']),
                                             'aircraft': itineraries[1]['aircraft']}}]}],

                                 'bagage': baggage,
                                 'price': {'currency': flight['price']['currency'], 'base': str(flight['price']['base'])},
                                 'travelClass': classes[form.travelClass.data],
                                 'place': str(form.adults.data + form.children.data),})
            
            # С пересадками
            else:
                for flight in response.data:
                    for i in range(2):
                        itineraries[i]['duration'] = isodate.parse_duration(flight['itineraries'][i]['duration'])
                        itineraries[i]['aviacompany_name'] = response.result['dictionaries']['carriers'][flight['itineraries'][i]['segments'][0]['carrierCode']]
                        itineraries[i]['aircraft'] = response.result['dictionaries']['aircraft'][flight['itineraries'][i]['segments'][0]['aircraft']['code']]
                        baggage = {}
                        if 'includedCheckedBags' in flight['travelerPricings'][0]['fareDetailsBySegment'][0]:
                            if "quantity" in flight['travelerPricings'][0]['fareDetailsBySegment'][0]['includedCheckedBags']:
                                baggage['includedCheckedBags'] = f'Багаж*: {flight['travelerPricings'][0]['fareDetailsBySegment'][0]['includedCheckedBags']['quantity']} шт.'
                            elif "weight" in flight['travelerPricings'][0]['fareDetailsBySegment'][0]['includedCheckedBags']:
                                baggage['includedCheckedBags'] = f'Багаж*: {flight['travelerPricings'][0]['fareDetailsBySegment'][0]['includedCheckedBags']['weight']} {flight['travelerPricings'][0]['fareDetailsBySegment'][0]['includedCheckedBags']['weightUnit']}'
                        else:
                            baggage['includedCheckedBags'] = 'Без багажа*'
                        if 'includedCabinBags' in flight['travelerPricings'][0]['fareDetailsBySegment'][0]:
                            if "quantity" in flight['travelerPricings'][0]['fareDetailsBySegment'][0]['includedCabinBags']:
                                baggage['includedCabinBags'] = f'Ручная кладь*: {flight['travelerPricings'][0]['fareDetailsBySegment'][0]['includedCabinBags']['quantity']} шт.'
                            elif "weight" in flight['travelerPricings'][0]['fareDetailsBySegment'][0]['includedCabinBags']:
                                baggage['includedCabinBags'] = f'Ручная кладь*: {flight['travelerPricings'][0]['fareDetailsBySegment'][0]['includedCabinBags']['weight']} {flight['travelerPricings'][0]['fareDetailsBySegment'][0]['includedCabinBags']['weightUnit']}'
                        else:
                            baggage['includedCabinBags'] = 'Без ручной клади*'

                        itineraries[i]['way'] = []
                        for segment in flight['itineraries'][i]['segments']:
                            itineraries[i]['way'].append({'departure': 
                                            {'town': searcher.find_city_by_iata(segment['departure']['iataCode']),
                                            'iataCode' : segment['departure']['iataCode'],
                                            'at': split_datetime(segment['departure']['at'])},
                                        'arrival': 
                                            {'town': searcher.find_city_by_iata(segment['arrival']['iataCode']),
                                            'iataCode' : segment['arrival']['iataCode'],
                                            'at': split_datetime(segment['arrival']['at'])},
                                        'aviacompany' : {'name': itineraries[i]['aviacompany_name'],
                                            'logo': get_logo(segment['carrierCode']),
                                            'aircraft': itineraries[i]['aircraft']},
                                        'duration': f"{isodate.parse_duration(segment['duration']).seconds // 3600} часов {isodate.parse_duration(segment['duration']).seconds % 3600 // 60} минут"})
                    info.append({'id': int(flight['id']) - 1,
                                 'itineraries': [
                                    {"duration": f"{itineraries[0]['duration'].seconds // 3600} часов {itineraries[0]['duration'].seconds % 3600 // 60} минут",
                                     'segments': itineraries[0]['way']},
                                    
                                    {"duration": f"{itineraries[1]['duration'].seconds // 3600} часов {itineraries[1]['duration'].seconds % 3600 // 60} минут",
                                     'segments': itineraries[1]['way']}],
                                
                                 'bagage': baggage,
                                 'price': {'currency': flight['price']['currency'], 'base': str(flight['price']['base'])},
                                 'travelClass': classes[form.travelClass.data],
                                 'place': str(form.adults.data + form.children.data)})
                        
                    for i in range(2):
                        depart_town = searcher.find_city_by_iata(flight['itineraries'][i]['segments'][0]['departure']['iataCode']) or form.originLocationCode.data
                        arriv_town = searcher.find_city_by_iata(flight['itineraries'][i]['segments'][-1]['arrival']['iataCode']) or form.destinationLocationCode.data
                        
                        info[int(flight['id']) - 1]['itineraries'][i]['segments'][0]['departure']['town'] = depart_town
                        info[int(flight['id']) - 1]['itineraries'][i]['segments'][-1]['arrival']['town'] = arriv_town
                        
        return render_template('search_result.html', data=info, type=type, title='Поиск авиабилетов', header=True)
    return render_template('search.html', title='Поиск авиабилетов', header=True, form=form)
