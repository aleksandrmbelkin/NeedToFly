import os
import flask
from flask import render_template
from forms.tabloform import TabloForm
from amadeus import Client
from dotenv import load_dotenv
import requests


blueprint = flask.Blueprint(
    'tablo',
    __name__,
    template_folder='templates'
)


load_dotenv()
AMADEUS_CLIENT_ID = os.getenv('AMADEUS_CLIENT_ID')
AMADEUS_CLIENT_SECRET = os.getenv('AMADEUS_CLIENT_SECRET')
AVIATIONSTACK_KEY = os.getenv('AVIATIONSTACK_KEY')


@blueprint.route('/tablo', methods=['GET', 'POST'])
def search():
    form = TabloForm()
    if form.submit.data:
        # Если пользователь подтвердил ввод, выводим при помощи amadeus информацию о рейсах
        amadeus = Client(client_id=AMADEUS_CLIENT_ID, client_secret=AMADEUS_CLIENT_SECRET)
        try:
            response = amadeus.airport.direct_destinations.get(departureAirportCode=str(form.airport.data))
            lt = []
            for i in response.data:
                lt.append({'country': i['address']['countryName'], 'airport_departure': str(form.airport.data),
                           'name': i["iataCode"]})
            return render_template('tablo.html', title='Поиск авиабилетов', header=True, form=form,
                                   message='', lt=lt)
        except Exception as e:
            # Если возникла ошибка с amadeus, возвращаем ошибку
            print(e)
            return render_template('tablo.html', title='Поиск авиабилетов', header=True, form=form,
                                   message='Code 404')
    return render_template('tablo.html', title='Поиск авиабилетов', header=True, form=form)


@blueprint.route('/<name>/<airport_departure>')
def tickets(name, airport_departure):
    # Возвращаем билеты
    lt = []
    no_ans = ''
    print(airport_departure, '->', name)
    url = f'https://api.aviationstack.com/v1/flights?access_key={AVIATIONSTACK_KEY}'
    response = requests.get(url, params={'dep_iata': airport_departure, 'arr_iata': name}).json()
    print(response)
    # Создаём список словарей с информацией о билетах
    for i in response['data']:
        lt.append({"flight_date": i['departure']['scheduled'], 'airport_departure': i['departure']['airport'],
                   'airport_arrival': i['arrival']['airport'], "flight_date_arrival": i['arrival']['scheduled'],
                   'airline_name': i['airline']['name'], 'flight_number': i['flight']['number']})
    print(lt)
    if len(lt) == 0:
        no_ans = 'Билеты не найдены. Попробуйте ещё раз или посмотрите другие рейсы'
    return render_template('flights_dates.html', title=f'Билеты из {airport_departure} в {name}', header=True,
                           flights_info=lt, no_ans=no_ans)
