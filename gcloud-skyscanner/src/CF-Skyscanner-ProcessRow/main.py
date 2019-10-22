from helpers import process_row_and_publish

def main(event, context):
    """Triggered from a message on a Cloud Pub/Sub topic.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """
    row = event['attributes'] # dict i.e {code:'JFK',haul:'LH'}

    project_id = "flights-243314"
    topic_name = "search-created"
    process_row_and_publish(row=row,project_id=project_id,topic_name=topic_name)
