#!/usr/bin/env python

import os
import json
import urllib
import boto3

input_bucket_name = 'samplenc'
output_bucket_name = 'weather-imgbucket'
sqsqueue_name = 'ncfile-listener-queue'
aws_region = 'eu-west-2'

s3 = boto3.client('s3', region_name=aws_region)
sqs = boto3.resource('sqs', region_name=aws_region)
ddb = boto3.resource('dynamodb', region_name=aws_region)

def generate_image(ncfile, imgfile):
    import iris
    [mydata] = iris.load(ncfile)
    air_temps = mydata.extract(iris.Constraint(realization=0))
    air_temp = air_temps.extract(iris.Constraint(pressure=1000.0))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import iris.quickplot as qplt

    # Set the size of the plot
    plt.figure(figsize=(20, 20))

    qplt.pcolormesh(air_temp)
    plt.gca().coastlines('50m')

    plt.savefig(imgfile)

def cleanup_files(image):
    os.remove(image)


def upload_image(image):
    s3.upload_file(image,
                   output_bucket_name, image)

def insert_to_table(location, forecast_time, image):
    table = ddb.Table('weather-forcast-table')
    print('insert_to_table starts')
    table.put_item(
       Item={
         'location': location,
         'forecast-time': forecast_time,
         'reference-time': '2019-01-09 12:00:00',
         'url': 's3://'+output_bucket_name+'/'+image
       } 
    )
    print('insert_to_table finished')  

def get_messages_from_sqs():
    results = []
    queue = sqs.get_queue_by_name(QueueName=sqsqueue_name)
    for message in queue.receive_messages(VisibilityTimeout=120,
                                          WaitTimeSeconds=20,
                                          MaxNumberOfMessages=1):
        results.append(message)
    return(results)

def process_images():
    """Process the image
    No real error handling in this sample code. In case of error we'll put
    the message back in the queue and make it visable again. It will end up in
    the dead letter queue after five failed attempts.
    """
    for message in get_messages_from_sqs():
        try:
            #notification = json.loads(message['Body'])
            message_content = json.loads(message.body)
            #s3_object = json.loads(notification['Message'])
            #ncfile = urllib.unquote_plus(message_content
            #                            ['Records'][0]['s3']['object']
            #                            ['key']).encode('utf-8')
            #ncfile=json.loads(s3_object['key'])
            ncfile=message_content['Records'][0]['s3']['object']['key']
            print('ncfile:'+ncfile)
            s3.download_file(input_bucket_name, ncfile, ncfile)
            imgfile=os.path.splitext(ncfile)[0]+'.png'
            print('imgfile:'+imgfile)
            generate_image(ncfile,imgfile)
            upload_image(imgfile)
            insert_to_table('London','20190109 18:00:00', imgfile) 
            os.remove(imgfile)
            os.remove(ncfile)
        except:
            message.change_visibility(VisibilityTimeout=0)
            continue
        else:
            message.delete()

def main():
    while True:
        process_images()


if __name__ == "__main__":
    main()
