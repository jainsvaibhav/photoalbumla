import json
import boto3
import requests

def detect_labels(photo, bucket):
    #test upload2
    labels_res = []
    client=boto3.client('rekognition')
    response = client.detect_labels(Image={'S3Object':{'Bucket':bucket,'Name':photo}},
        MaxLabels=10)
    print(photo) 
    for label in response['Labels']:
        print ("Label: " + label['Name'])
        labels_res.append(label['Name'])
    return labels_res

def lambda_handler(event, context):
    
    # updating code to see 
    # TODO implement
    print(event)
    bucket = "picturesb2"
    for record in event['Records']:
        image_name = record["s3"]["object"]["key"]
        eventtime = record["eventTime"]
        s3client = boto3.client('s3')
        metadata = s3client.head_object(Bucket=bucket, Key=image_name)
        print("metdata", metadata)
        given_labels=[]
        if 'Metadata' in metadata.keys() and 'customlabel' in metadata['Metadata'].keys():
            given_labels = metadata['Metadata']["customlabel"].split(",")
            given_labels = [x.strip() for x in given_labels]
        print("given_labels", given_labels)
        print(image_name,eventtime)
        labels_res=detect_labels(image_name, bucket)
        print(labels_res)
        labels_res += given_labels
        temp=[]
        url = "https://search-photosindex-nhstcgewxc644dwhjtcaqel3zi.us-west-2.es.amazonaws.com/photos/_doc"
        headers = {'Content-Type' : 'application/json'}
        format={'objectkey':image_name,'timstamp':eventtime,'bucket':bucket,'labels':labels_res}
        response = requests.post(url, data=json.dumps(format).encode("utf-8"), headers=headers,auth=('admin', 'Admin@123'))
        dat=json.loads(response.text)
        print (dat)
    return {
        'statusCode': 200,
        'body': json.dumps('Labels added to ES')
    }
