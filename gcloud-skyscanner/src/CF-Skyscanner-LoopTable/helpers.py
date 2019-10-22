def query_table(query):
    """Reads BigQuery Table
    Args:
         query (string): SQL query
    """
    from google.cloud import bigquery
    client = bigquery.Client()
    query_job = client.query(query)
    result_rows = query_job.result()  # Waits for job to complete.
    # Returns iterator
    return result_rows


def publish_pubsub(project_id, topic_name, **attributes):
    """Publish message and attributes in topic'
    Args:
         project_id (string): project ID from Pub/Sub
         topic_name (string): topic ID from Pub/Sub
         attributes (dict)
    """
    from google.cloud import pubsub_v1
    publisher = pubsub_v1.PublisherClient()
    # The `topic_path` method creates a fully qualified identifier
    # in the form `projects/{project_id}/topics/{topic_name}`
    topic_path = publisher.topic_path(project_id, topic_name)
    data = 'message'  # data not needed if attributes are present
    # Data must be a bytestring
    data = data.encode('utf-8')
    # When publishing a message, the client returns a future.
    future = publisher.publish(
        topic_path,
        data=data,
        **attributes)