def process_row_and_publish(row,project_id,topic_name):
    """Creates list of attributes dictionaries from BigQuery row
    Args:
         row (dict)
    """
    # Create combinations of days
    dates_dict_list = generate_outbound_inbound_dates(
        days_ahead=30, length_stay=7)
    for cabin in ['economy', 'business']:
        for point_of_sale in ['UK', 'US']:
            for dates_dict in dates_dict_list:
                search = {
                    'code': row['code'],
                    'haul': row['haul'],
                    'cabin': cabin,
                    'point_of_sale': point_of_sale,
                    'dates_dict': str(dates_dict)
                }
                publish_pubsub(project_id=project_id, topic_name=topic_name, **search)

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



def generate_outbound_inbound_dates(days_ahead, length_stay):
    import datetime
    outbound_date = (datetime.datetime.today() +
                     datetime.timedelta(days=days_ahead)).strftime('%Y-%m-%d')
    inbound_date = (
        datetime.datetime.today() +
        datetime.timedelta(days=days_ahead + length_stay)).strftime('%Y-%m-%d')
    outbound_date_3m = (
        datetime.datetime.today() +
        datetime.timedelta(days=days_ahead + 90)).strftime('%Y-%m-%d')
    inbound_date_3m = (datetime.datetime.today() +
                       datetime.timedelta(days=days_ahead + length_stay + 90)
                      ).strftime('%Y-%m-%d')
    dates_dict_list = [{
        'outbound': outbound_date,
        'inbound': inbound_date,
        'date_type': 'outbound'
    }, {
        'outbound': outbound_date_3m,
        'inbound': inbound_date_3m,
        'date_type': 'outbound + 90 days'
    }]

    return dates_dict_list

