This is a core AntAlmanac service that collects class enrollment information from WebSOC. 
In this repository, it is designed to be deployed to AWS Lambda and run once a day, logging the results to a remote MongoDB.
However, it is trivial to extract the code to run however you want it.
It uses the serverless framework for easy deployment management.

To deploy, you'll need a serverless account and AWS credentials loaded on your environment.

To test locally, use pip to install the requirements from `requirements.txt`:

`pip install -r requirements.txt`

Then, set up these environment variables in a file called `.env`:

```
    SOCSPIDER_TERM = 
    SOCSPIDER_MONGODB_URI = 
    SOCSPIDER_MONGODB_USERNAME = 
    SOCSPIDER_MONGODB_PASSWORD = 
    SOCSPIDER_DB_NAME = 
    SOCSPIDER_CHUNKS_COLLECTION_NAME = 
    SOCSPIDER_ENROLLMENT_COLLECTION_NAME = 
```

Deploy: 
```
$ serverless deploy
```

