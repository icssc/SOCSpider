# SOCSpider

SOCSpider is a service that scrapes, processes, and stores data from WebSOC. It allows viewing of historical enrollment data on [AntAlmanac](https://antalmanac.com).

## Configuration
In this repository, it is designed to be deployed to AWS Lambda and run once a day, sending the data to a MongoDB instance running on [MongoDB Atlas](https://www.mongodb.com/cloud/atlas).
However, it is trivial to extract the code to run however you want it.
It uses [Serverless Framework](https://www.serverless.com/) for easy deployment management.

## For AntAlmanac contributors:
### Please see internal AntAlmanac documentation for details.
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


# Deploy
To deploy, you'll need a Serverless account and the right AWS credentials loaded onto your environment. 

Deploy: 
```
$ serverless deploy
```
