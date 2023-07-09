import json
import requests
from requests.auth import HTTPBasicAuth
from random import randint, randrange
from randomuser import RandomUser
from datetime import datetime, timedelta
from configparser import ConfigParser
parser = ConfigParser()
parser.read('config.ini')

BASE_URL = parser['Connection']['baseurl']

SUPERUSER_USERNAME = parser['Connection']['username']
SUPERUSER_PASSWORD = parser['Connection']['password']

OUTPUT_FILE = parser['Output']['file_name']

ADMIN_COUNT = int(parser['Creation Counts']['admins'])
AIRLINE_COUNT = int(parser['Creation Counts']['airlines'])
CUSTOMER_COUNT = int(parser['Creation Counts']['customers'])
FLIGHT_COUNT = int(parser['Creation Counts']['flights_per_airline'])
TICKET_COUNT = int(parser['Creation Counts']['tickets_per_flight'])


def random_datetime(start, end):
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = randrange(int_delta)
    return start + timedelta(seconds=random_second)

randcountry = lambda: randint(1, 194)
randdate = lambda: random_datetime(datetime.now(), datetime.now() + timedelta(weeks=156))
randdelta = lambda: timedelta(days=randint(0,1), hours=randint(0, 23), minutes=randint(0, 59))

# Create admins
admins = []
auth = HTTPBasicAuth(SUPERUSER_USERNAME, SUPERUSER_PASSWORD)

for index in range(ADMIN_COUNT):
    user = RandomUser()
    password = user.get_password()
    request_body = {
        'username': user.get_username(),
        'password': password,
        'email': user.get_email(),
        'first_name': user.get_first_name(),
        'last_name': user.get_last_name()
    }
    response = requests.post(BASE_URL + "admins/", data=request_body, auth=auth)
    if response.status_code == 201:
        admins.append(response.json()['data'])
        admins[index]['user']['password'] = password
        print(f'Created admin {index + 1}/{ADMIN_COUNT}...')
    else:
        print(response.json())
        
# Create airlines
airlines = []
auth = HTTPBasicAuth(SUPERUSER_USERNAME, SUPERUSER_PASSWORD)

for index in range(AIRLINE_COUNT):
    user = RandomUser()
    password = user.get_password()
    request_body = {
        'username': user.get_username(),
        'password': password,
        'email': user.get_email(),
        'name': user.get_full_name() + ' Airlines',
        'country': randcountry()
    }
    response = requests.post(BASE_URL + "airlines/", data=request_body, auth=auth)
    if response.status_code == 201:
        airlines.append(response.json()['data'])
        airlines[index]['user']['password'] = password
        print(f'Created airline {index + 1}/{AIRLINE_COUNT}...')
    else:
        print(response.json())

# Create customers
customers = []
auth = HTTPBasicAuth(SUPERUSER_USERNAME, SUPERUSER_PASSWORD)

for index in range(CUSTOMER_COUNT):
    user = RandomUser()
    password = user.get_password()
    request_body = {
        'username': user.get_username(),
        'password': password,
        'email': user.get_email(),
        'first_name': user.get_first_name(),
        'last_name': user.get_last_name(),
        'address': user.get_street() + ', ' + user.get_city(),
        'phone_number': user.get_phone()
    }
    response = requests.post(BASE_URL + "customers/", data=request_body, auth=auth)
    if response.status_code == 201:
        customers.append(response.json()['data'])
        customers[index]['user']['password'] = password
        print(f'Created customer {index + 1}/{CUSTOMER_COUNT}...')
    else:
        print(response.json())

# Create flights
flight_dict = {}
flight_index = 1
total_flights = len(airlines) * FLIGHT_COUNT
for airline in airlines:
    flights = []
    auth = HTTPBasicAuth(airline['user']['username'], airline['user']['password'])

    for index in range(FLIGHT_COUNT):
        date = randdate()
        request_body = {
            'origin_country': randcountry(),
            'destination_country': randcountry(),
            'departure_datetime': date.isoformat(),
            'arrival_datetime': (date + randdelta()).isoformat(),
            'total_seats': randint(50, 300)
        }
        
        response = requests.post(BASE_URL + "flights/", data=request_body, auth=auth)
        if response.status_code == 201:
            flights.append(response.json()['data'])
            print(f'Created flight {flight_index}/{total_flights}...')
            flight_index += 1
        else:
            print(response.json())
    flight_dict[airline['airline']['id']] = flights

# Create tickets
tickets_dict = {}
ticket_index = 1
total_tickets = TICKET_COUNT * total_flights
for airline, flights in flight_dict.items():
    for flight in flights:
        tickets_dict[flight['id']] = {}
        tickets = []
        for index in range(TICKET_COUNT):
            customer = customers[randint(0, len(customers) - 1)]
            auth = HTTPBasicAuth(customer['user']['username'], customer['user']['password'])
            
            request_body = {
                'flight_id': int(flight['id']),
                'seat_count': randint(1,5) 
            }
            response = requests.post(BASE_URL + "tickets/", data=request_body, auth=auth)
            if response.status_code == 201:
                tickets.append(response.json()['data'])
                print(f'Created ticket {ticket_index}/{total_tickets}...')
            else:
                print(response.json())
        tickets_dict[flight['id']] = tickets
                

output_dict = {
    'admins': admins,
    'airlines': airlines,
    'customers': customers,
    'flights': flight_dict,
    'tickets': tickets_dict
}
            
with open(OUTPUT_FILE, "w") as outfile:
    json.dump(output_dict, outfile)