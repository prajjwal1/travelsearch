from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import boto3
import json

def load_credentials():
    with open('credentials.json', 'r') as file:
        return json.loads(file.read())

class Index:
    def __init__(self):
        host = 'search-travelsearch-sdyfnx547dsnfrh43mo6d4s3he.us-east-2.es.amazonaws.com'
        region = 'us-east-2'
        service = 'es'
        creds = load_credentials()
        credentials = boto3.Session(
            aws_secret_access_key=creds['AWSSecretKey'],
            aws_access_key_id=creds['AWSAccessKeyId']
        ).get_credentials()
        awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service,
                           session_token=credentials.token)
        self.es = Elasticsearch(
            hosts=[{'host': host, 'port': 443}],
            http_auth=awsauth,
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection
        )

    def query(self, query, max_queries=50):
        body = {
            'query': {
                "term": {
                    "page_text": query
                }
            }
        }
        result =  self.es.search(index='travel', body=body, size=max_queries)['hits']['hits']
        return [doc['_source'] for doc in result]

if __name__ == '__main__':
    es = Index()
    res = es.query('vegas')

