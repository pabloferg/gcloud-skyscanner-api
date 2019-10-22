def post_request(origin, destination_code, out_date, in_date, cabinClass, point_of_sale):
    import requests
    import time
    import os

    key = os.environ.get('SKYSCANNER_KEY')

    if point_of_sale == "UK":
        country = "GB"
        currency = "GBP"
        locale = "en-GB"
    elif point_of_sale == "US":
        country = "US"
        currency = "USD"
        locale = "en-US"

    post_response = []
    while str(post_response) != "<Response [201]>":
        post_response = requests.post(
            "https://skyscanner-skyscanner-flight-search-v1.p.mashape.com/apiservices/pricing/v1.0",
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "X-Mashape-Key": key,
                "X-Mashape-Host": "skyscanner-skyscanner-flight-search-v1.p.mashape.com"
            },
            data={
                "country": country,
                "currency": currency,
                "locale": locale,
                "originPlace": origin + "-sky",
                "destinationPlace": destination_code + "-sky",
                "outboundDate": out_date,
                "inboundDate": in_date,
                "cabinClass": cabinClass,
                "adults": 1,
                "children": 0,
                "infants": 0,
                "includeCarriers": "",
                "excludeCarriers": ""
            }
        )
        print(post_response)
        time.sleep(1)

    session_id = post_response.headers['Location'].split("/")[-1]

    return session_id


def get_request(session_id):
    import requests
    import os

    key = os.environ.get('SKYSCANNER_KEY')
    get_status = ""
    while get_status != "UpdatesComplete":
        try:
            url = "https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com/apiservices/pricing/uk2/v1.0/" + session_id

            querystring = {"sortType": "price", "sortOrder": "asc", "stops": "0", "pageIndex": "0", "pageSize": "50"}
            headers = {
                'x-rapidapi-host': "skyscanner-skyscanner-flight-search-v1.p.rapidapi.com",
                'x-rapidapi-key': key
            }

            response = requests.request("GET", url, headers=headers, params=querystring)

            get_status = response.json()["Status"]
        except:
            continue

    json_response = response.json()

    return json_response

def process_json_response(json_response, pubsub_attributes):
    import datetime


    # Create dictionaries to decode values
    carriers_dict = create_carriers_dict(json_response)
    legs_dict = create_legs_dict(json_response)
    places_dict = create_places_dict(json_response)

    list_of_dicts_OutInb = []
    for index, itinerary in enumerate(json_response['Itineraries']):
        OutboundLegId = itinerary['OutboundLegId']
        OutboundLeg_dict = legs_dict[OutboundLegId]
        InboundLegId = itinerary['InboundLegId']
        InboundLeg_dict = legs_dict[InboundLegId]

        Outbound_dict = {'Out_OriginStation': places_dict[OutboundLeg_dict['OriginStation']]['Code'],
                         'Out_DestinationStation': places_dict[OutboundLeg_dict['DestinationStation']]['Code'],
                         'Out_Departure': OutboundLeg_dict['Departure'],
                         'Out_Arrival': OutboundLeg_dict['Arrival'],
                         'Out_Duration': OutboundLeg_dict['Duration'],
                         'Out_JourneyMode': OutboundLeg_dict['JourneyMode'],
                         'Out_Stops': str([places_dict[stop]['Code'] for stop in OutboundLeg_dict['Stops']]),
                         'Out_Carriers': str(
                             [carriers_dict[carrier]['Name'] for carrier in OutboundLeg_dict['Carriers']]),
                         'Out_OperatingCarriers': str([carriers_dict[carrier]['Name'] for carrier in
                                                       OutboundLeg_dict['OperatingCarriers']]),
                         'Out_Directionality': OutboundLeg_dict['Directionality'],
                         'Out_FlightNumbers': str(OutboundLeg_dict['FlightNumbers'])
                         }
        Inbound_dict = {'Inb_OriginStation': places_dict[InboundLeg_dict['OriginStation']]['Code'],
                        'Inb_DestinationStation': places_dict[InboundLeg_dict['DestinationStation']]['Code'],
                        'Inb_Departure': InboundLeg_dict['Departure'],
                        'Inb_Arrival': InboundLeg_dict['Arrival'],
                        'Inb_Duration': InboundLeg_dict['Duration'],
                        'Inb_JourneyMode': InboundLeg_dict['JourneyMode'],
                        'Inb_Stops': str([places_dict[stop]['Code'] for stop in InboundLeg_dict['Stops']]),
                        'Inb_Carriers': str(
                            [carriers_dict[carrier]['Name'] for carrier in InboundLeg_dict['Carriers']]),
                        'Inb_OperatingCarriers': str([carriers_dict[carrier]['Name'] for carrier in
                                                      InboundLeg_dict['OperatingCarriers']]),
                        'Inb_Directionality': InboundLeg_dict['Directionality'],
                        'Inb_FlightNumbers': str(InboundLeg_dict['FlightNumbers'])
                        }

        # merge Outbound and Inbound dictionaries
        dict_OutInb = {**Outbound_dict, **Inbound_dict}


        # add extra info into the dictionary
        dict_OutInb['cheapestPrice'] = itinerary['PricingOptions'][0]['Price']
        dict_OutInb['index'] = index
        dict_OutInb['query_Locale'] = json_response['Query']['Locale']
        dict_OutInb['query_Currency'] = json_response['Query']['Currency']
        dict_OutInb['query_Adults'] = json_response['Query']['Adults']
        dict_OutInb['query_CabinClass'] = json_response['Query']['CabinClass']
        dict_OutInb['query_Timestamp'] = datetime.datetime.now()
        dict_OutInb['haul'] = pubsub_attributes['haul']
        dict_OutInb['query_DateType'] = eval(pubsub_attributes['dates_dict'])['date_type']

        list_of_dicts_OutInb.append(dict_OutInb)

    return list_of_dicts_OutInb


def insert_to_bigquery(dataset, table, dict_to_insert):
    from google.cloud import bigquery
    # Instantiates a client
    bigquery_client = bigquery.Client()

    # Prepares a reference to the dataset
    dataset_ref = bigquery_client.dataset(dataset)

    table_ref = dataset_ref.table(table)
    table = bigquery_client.get_table(table_ref)  # API call

    row = tuple([
        dict_to_insert[field.name] for field in table.schema
    ])

    errors = bigquery_client.insert_rows(table, [row])  # API request
    assert errors == []





def create_carriers_dict(json_response):
    carriers_dict = {}
    for carrier in json_response["Carriers"]:
        carriers_dict[carrier["Id"]] = carrier
    return carriers_dict

def create_legs_dict(json_response):
    legs_dict = {}
    for leg in json_response["Legs"]:
        legs_dict[leg["Id"]] = leg
    return legs_dict

def create_places_dict(json_response):
    places_dict = {}
    for place in json_response["Places"]:
        places_dict[place["Id"]] = place
    return places_dict