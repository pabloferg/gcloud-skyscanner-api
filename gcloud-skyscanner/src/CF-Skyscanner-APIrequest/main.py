from helpers import post_request
from helpers import get_request
from helpers import insert_to_bigquery
from helpers import process_json_response

def main(event, context):
    """Triggered from a message on a Cloud Pub/Sub topic.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """
    pubsub_attributes = event['attributes']
    dates_dict = eval(event['attributes']['dates_dict'])  # transforms str into dict

    # get session_id
    session_id = post_request(origin='LOND',
                                   destination_code=event['attributes']['code'],
                                   out_date=dates_dict['outbound'],
                                   in_date=dates_dict['inbound'],
                                   cabinClass=event['attributes']['cabin'],
                                   point_of_sale=event['attributes']['point_of_sale'])

    # use session_id to retrieve the full json response
    json_response = get_request(session_id)

    # Insert results in BigQuery

    list_of_dicts_OutInb = process_json_response(json_response=json_response,pubsub_attributes=pubsub_attributes)

    for dict_to_insert in list_of_dicts_OutInb:
        insert_to_bigquery(dataset='skyscanner',
                           table='results',
                           dict_to_insert=dict_to_insert)

    print("**** Rows inserted ****")

