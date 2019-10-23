# gcloud-skyscanner-api

This projects uses Google Cloud Functions and Pub/Sub Topics with Skyscanne API to get fares for different destination. 




```
├── assets
│   ├── airport_codes_200.csv
│   └── images
│       └── bigpicture.png
├── README.md
└── src
    └── CF-Skyscanner-ProcessRow
        └── main.py
        └── helpers.py
        └── requirements.txt
    └── CF-Skyscanner-ProcessRow
        └── main.py
        └── helpers.py
        └── requirements.txt
    └── CF-Skyscanner-ProcessRow
        └── main.py
        └── helpers.py
        └── requirements.txt
    └── setup
        └── main.py
        └── helpers.py
        └── requirements.txt
 ```
    
    

Costs
This tutorial uses billable components of Cloud Platform, including:

Google Cloud Functions
Google Cloud Pub/Sub
Google Cloud Scheduler



Pub/Sub CLient Libraries: https://cloud.google.com/pubsub/docs/reference/libraries



If you are playing locally with python and gcloud, you may face the following error message:
```
google.auth.exceptions.DefaultCredentialsError: Could not automatically determine credentials. Please set GOOGLE_APPLICATION_CREDENTIALS or explicitly create credentials and re-run the application. For more information, please see https://cloud.google.com/docs/authentication/getting-started
```

import os 
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="/users/<username>/<path>/credentials.json"
  
You will have to create a service account following https://cloud.google.com/docs/authentication/production , and you will download a json file that contains your key.

### Request access to Skyscanner API on RapidAPI.com

[RapidAPI] platform is an easy way to start using Skyscanner API. First, you just need to sign up and find the API [here](https://rapidapi.com/skyscanner/api/skyscanner-flight-search). You can play with the UI on your browser to see how the REST API works, but we will use Python instead. 

You will need your `KEY` to access the API. **You will set this key as environment variable in the Cloud Function calling the API** (Explained lateron)

![Screenshot](gcloud-skyscanner/assets/images/signup.png)

## Initial Setup

1. Create a [Google Cloud Project](https://cloud.google.com/).
2. You will need 3 Cloud Functions and 3 Pub/Sub Topics.

You can read [this](https://cloud.google.com/scheduler/docs/tut-pub-sub) tutorial to have an idea about how this works. 

There are 3 folders in this repository containing 3 Cloud Functions (CF):
```
└── src
    └── CF-Skyscanner-ProcessRow
        └── main.py
        └── helpers.py
        └── requirements.txt
    └── CF-Skyscanner-ProcessRow
        └── main.py
        └── helpers.py
        └── requirements.txt
    └── CF-Skyscanner-ProcessRow
        └── main.py
        └── helpers.py
        └── requirements.txt
```
        
You will deploy this functions using the [Google Cloud SDK](https://cloud.google.com/appengine/docs/standard/go/download). You need to install it first to be able to uset `gcloud` command in your terminal. Once installed, try to get familiarised with it before moving forward.
 
Download the folders. In your Terminal, move to the folder path with `cd <path>`. Once in the folder, run the following command to deploy the function

```
$ gcloud functions deploy FUNCTION_NAME --runtime python37 --trigger-topic TOPIC_NAME
```

Examples:
```
$ gcloud functions deploy Skyscanner-LoopTable --runtime python37 --trigger-topic skyscanner-start
$ gcloud functions deploy Skyscanner-ProcessRow --runtime python37 --trigger-topic row-read
$ gcloud functions deploy Skyscanner-APIrequest --runtime python37 --trigger-topic search-created
```


3. You will need to setup an environment variable in the Cloud Function calling the API with your Skyscanner key.
```
gcloud functions deploy Skyscanner-LoopTable --set-env-vars SKYSCANNER_KEY=<YOUR KEY FROM RAPID-API>
```

4. You will need to create [2 Tables](https://github.com/pabloferg/gcloud-skyscanner-api/blob/master/gcloud-skyscanner/src/setup/createPubsubTopic.py#L13) in BigQuery:
            a) to store the list of destination codes to search on skyscanner,
            b) to save results from the API response
           
# Scheduler
![Screenshot](gcloud-skyscanner/assets/images/scheduler.png)

## Architecture

![Screenshot](gcloud-skyscanner/assets/images/bigpicture.png)

