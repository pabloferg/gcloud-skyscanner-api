from helpers import query_table
from helpers import publish_pubsub

def main(event, context):
    """Triggered from a message on a Cloud Pub/Sub topic.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """
    # Query Table where destination Codes are stored
    dataset = "skyscanner"
    table = "main"
    query = """SELECT * FROM """ + dataset + "." + table
    result_rows = query_table(query)

    # Number of rows
    total_rows = result_rows.total_rows
    # Read each row
    for index, row in enumerate(result_rows):
        print("**********", int((index / total_rows) * 100), "%")
        attributes = {'code': row.code, 'haul': row.haul}
        # Publish attributes
        publish_pubsub(
            project_id="flights-243314", topic_name="row-read", **attributes)
    print("********** FINISHED")
