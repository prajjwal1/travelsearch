from elasticsearch import Elasticsearch, RequestsHttpConnection
from elasticsearch.helpers import parallel_bulk
from requests_aws4auth import AWS4Auth
import boto3
import json

def load_credentials():
    with open('credentials.json', 'r') as file:
        return json.loads(file.read())

def stream_data():
    with open('elastic_search_data.json', 'r') as file:
        elastic_search_docs = json.loads(file.read())
    for doc in elastic_search_docs:
        yield {
            "_index": "travel",
            "ingoing_edges": doc['ingoing_edges'],
            "outgoing_edges": doc['outgoing_edges'],
            "page_text": doc['page_text'],
            "page_name": doc['page_name']
        }
if __name__ == '__main__':
    # doc_tokens, _, _, _ = load_processed_tokens()
    host = 'search-travelsearch-sdyfnx547dsnfrh43mo6d4s3he.us-east-2.es.amazonaws.com'
    region = 'us-east-2'
    service = 'es'
    creds = load_credentials()
    credentials = boto3.Session(
        aws_secret_access_key=creds['AWSSecretKey'],
        aws_access_key_id=creds['AWSAccessKeyId']
    ).get_credentials()
    awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)
    es = Elasticsearch(
        hosts=[{'host': host, 'port': 443}],
        http_auth=awsauth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection
    )
    count = 0
    for success, info in parallel_bulk(es, stream_data()):
        if not success:
            print('A document failed:', info)
        print('Processed Doc {}'.format(count))
        count += 1
