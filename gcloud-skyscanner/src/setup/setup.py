# TODO(developer) : project_id = YOUR GCLOUD PROJECTID

# AUTHENTICATION
set_credentials(filename)

# BIGQUERY SETUP
# Create dataset
dataset_id = "skyscanner"
create_dataset(dataset_name = dataset_id)
# Load csv to dataset
table_id = "main"
# TODO(developer) : filename = '/<path?/destinationCodes.csv'
load_csv(dataset_id=dataset_id,table_id,filename)

# Create Pub/Sub topics
for topic in ["skyscanner-start", "row-read", "search-created"]:
    create_topic(project_id, topic)


# Load csv with destination codes
load_csv(dataset_id,table_id,filename)

def set_credentials(filename):
    """Provide authentication credentials to your application code by setting the environment
    variable GOOGLE_APPLICATION_CREDENTIALS. Download from the Console the JSON file that contains your
    service account key.
    Args:
         filename (string): "/path/to/key.json"
    """
    import os
    # filename -> "/path/to/key.json'"
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"]=filename


def load_csv(dataset_id,table_id,filename):
    # from https://cloud.google.com/bigquery/docs/loading-data-local
    from google.cloud import bigquery
    client = bigquery.Client()

    dataset_ref = client.dataset(dataset_id)
    table_ref = dataset_ref.table(table_id)
    job_config = bigquery.LoadJobConfig()
    job_config.source_format = bigquery.SourceFormat.CSV
    job_config.skip_leading_rows = 1
    job_config.schema = [
        bigquery.SchemaField("code", "STRING"),
        bigquery.SchemaField("haul", "STRING"),
    ]
    #job_config.autodetect = True

    with open(filename, "rb") as source_file:
        job = client.load_table_from_file(source_file, table_ref, job_config=job_config)

    job.result()  # Waits for table load to complete.

    print("Loaded {} rows into {}:{}.".format(job.output_rows, dataset_id, table_id))


def create_topic(project_id, topic):
    """Create a Cloud Pub/Sub topic.
    Args:
         project_id (string): your Google Cloud Project ID
         topic (string): the name of the Topic
    """
    from google.cloud import pubsub_v1
    publisher = pubsub_v1.PublisherClient()
    topic_name = 'projects/{project_id}/topics/{topic}'.format(
        project_id=project_id,
        topic=topic)
    publisher.create_topic(topic_name)

def create_dataset(dataset_name):
    """Create a BigQUery Dataset.
    Args:
         dataset_name (string): name of the dataset to create
    """
    from google.cloud import bigquery
    client = bigquery.Client()

    dataset_id = "{}.{}".format(client.project,dataset_name)

    # Construct a full Dataset object to send to the API.
    dataset = bigquery.Dataset(dataset_id)

    # TODO(developer): Specify the geographic location where the dataset should reside.
    dataset.location = "US"

    # Send the dataset to the API for creation.
    # Raises google.api_core.exceptions.Conflict if the Dataset already
    # exists within the project.
    dataset = client.create_dataset(dataset)  # API request
    print("Created dataset {}.{}".format(client.project, dataset.dataset_id))

