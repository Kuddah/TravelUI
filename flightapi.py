Flight_API = """Reference
Client
classamadeus.Client(**options)[source]
The Amadeus client library for accessing the travel APIs.
originLocationCode should be in IATA format.
destinationLocationCode should be in IATA format
__init__(**options)[source]
Initialize using your credentials:

from amadeus import Client

amadeus = Client(
    client_id='iApYXewA9W2JFPQggvjA46TsOSfV1fvb',
    client_secret='ATEFOu6fmUGd79ki'
)
Alternatively, initialize the library using the environment variables AMADEUS_CLIENT_ID and AMADEUS_CLIENT_SECRET.

sample for an api call 
https://test.api.amadeus.com/v2/shopping/flight-offers?originLocationCode=MCT&destinationLocationCode=KUL&departureDate=2023-05-22&adults=5&currencyCode=USD&max=30

amadeus = amadeus.Client()

Parameters
client_id (str) – the API key used to authenticate the API

client_secret (str) – the API secret used to authenticate the API

logger (logging.Logger) – (optional) a Python compatible logger (Default: logging.Logger)

log_level (str) – (optional) the log level of the client, either "debug", "warn", or "silent" mode (Default: "silent")

hostname (str) – (optional) the name of the server API calls are made to, "production" or "test". (Default: "test")

host (str) – (optional) alternatively, you can specify a full host domain name instead, e.g. "api.example.com"

ssl (bool) – if this client is should use HTTPS (Default: True)

port (int) – the port this client should use (Default: 80 for HTTP and 443 for HTTPS)

custom_app_id (str) – (optional) a custom App ID to be passed in the User Agent to the server (Default: None)

custom_app_version (str) – (optional) a custom App Version number to be passed in the User Agent to the server (Default: None)

http (urllib.request.urlopen) – (optional) a urllib.request.urlopen() compatible client that accepts a urllib.request.Request compatible object (Default: urlopen)

Raises
ValueError – when a required param is missing

get(path, **params)
A helper function for making generic GET requests calls. It is used by every namespaced API GET method.

It can be used to make any generic API call that is automatically authenticated using your API credentials:

amadeus.get('/foo/bar', airline='1X')
Parameters
path (str) – path the full path for the API call

params (dict) – (optional) params to pass to the API

Return type
amadeus.Response

Raises
amadeus.ResponseError – when the request fails

post(path, params=None)
A helper function for making generic POST requests calls. It is used by every namespaced API POST method.

It can be used to make any generic API call that is automatically authenticated using your API credentials:

amadeus.post('/foo/bar', airline='1X')
Parameters
path (str) – path the full path for the API call

params (dict) – (optional) params to pass to the API

Return type
amadeus.Response

Raises
amadeus.ResponseError – when the request fails

request(verb, path, params)
A helper function for making generic POST requests calls. It is used by every namespaced API method. It can be used to make any generic API call that is automatically authenticated using your API credentials:

amadeus.request('GET', '/foo/bar', airline='1X')
Parameters
verb (str) – the HTTP verb to use

path (str) – path the full path for the API call

params (dict) – (optional) params to pass to the API

Return type
amadeus.Response

Raises
amadeus.ResponseError – when the request fails

Response
classamadeus.Response(http_response, request)[source]
The response object returned for every API call.

Variables
http_response – the raw http response

request (amadeus.Request) – the original Request object used to make this call

result (dict) – the parsed JSON received from the API, if the result was JSON

data (dict) – the data extracted from the JSON data, if the body contained JSON

body (str) – the raw body received from the API

parsed (bool) – wether the raw body has been parsed into JSON

status_code (int) – The HTTP status code for the response, if any

ResponseError
classamadeus.ResponseError(response)[source]
An Amadeus error

Variables
response (amadeus.Response) – The response object containing the raw HTTP response and the request used to make the API call.

code (str) – A unique code for this type of error. Options include NetworkError, ParserError, ServerError, AuthenticationError, NotFoundError and UnknownError.

classamadeus.AuthenticationError(response)[source]
Bases: amadeus.client.errors.ResponseError

This error occurs when the client did not provide the right credentials

classamadeus.ClientError(response)[source]
Bases: amadeus.client.errors.ResponseError

This error occurs when the client did not provide the right parameters

classamadeus.NetworkError(response)[source]
Bases: amadeus.client.errors.ResponseError

This error occurs when there is some kind of error in the network

classamadeus.ServerError(response)[source]
Bases: amadeus.client.errors.ResponseError

This error occurs when there is an error on the server

classamadeus.NotFoundError(response)[source]
Bases: amadeus.client.errors.ResponseError

This error occurs when the path could not be found

classamadeus.ParserError(response)[source]
Bases: amadeus.client.errors.ResponseError

This error occurs when the response type was JSOn but could not be parsed

Request
classamadeus.Request(options)[source]
An object containing all the compiled information about the request made.

Variables
host (str) – The host used for this API call

port (int) – The port for this API call. Standard set to 443.

ssl (bool) – Wether to use SSL for a call, defaults to true

scheme (str) – The scheme used to make the API call

params (dict) – The GET/POST params for the API call

path (str) – The path of the API to be called

verb (str) – The verb used to make an API call (‘GET’ or ‘POST’)

bearer_token (str) – The bearer token (if any) that was used for authentication

headers (dict) – The headers used for the API call

client_version (str) – The library version used for this request

language_version (str) – The Python language version used for this request

app_id (str) – The custom app ID passed in for this request

app_version (str) – The custom app version used for this request

Shopping/Flights
classamadeus.shopping.FlightDestinations(client)[source]
get(**params)[source]
Find the cheapest destinations where you can fly to.

amadeus.shopping.flight_destinations.get(origin='LON')
Parameters
origin – the City/Airport IATA code from which the flight will depart. "LON", for example for London.

Return type
amadeus.Response

Raises
amadeus.ResponseError – if the request could not be completed

classamadeus.shopping.FlightDates(client)[source]
get(**params)[source]
Find the cheapest flight dates from an origin to a destination.

amadeus.shopping.flight_dates.get(origin='NYC', destination='MAD')
Parameters
origin – the City/Airport IATA code from which the flight will depart. "NYC", for example for New-York.

destination – the City/Airport IATA code to which the flight is going. "MAD", for example for Madrid.

Return type
amadeus.Response

Raises
amadeus.ResponseError – if the request could not be completed

classamadeus.shopping.FlightOffersSearch(client)[source]
get(**params)[source]
Get the cheapest flights on a given journey

amadeus.shopping.flight_offers_search.get(
    originLocationCode='MAD',
    destinationLocationCode='BOS',
    departureDate='2019-11-01',
    adults='1'
)
Parameters
originLocationCode – the City/Airport IATA code from which the flight will depart. "MAD", for example for Madrid.

destinationLocationCode – the City/Airport IATA code to which the flight is going. "BOS", for example for Boston.

departureDate – the date on which to fly out, in YYYY-MM-DD format

adults – the number of adult passengers with age 12 or older

Return type
amadeus.Response

Raises
amadeus.ResponseError – if the request could not be completed

classamadeus.shopping.FlightOffersSearch(client)[source]
post(body)[source]
Get the cheapest flights on a given journey.

amadeus.shopping.flight_offers_search.post(body)
Parameters
body – the parameters to send to the API

Return type
amadeus.Response

Raises
amadeus.ResponseError – if the request could not be completed"""