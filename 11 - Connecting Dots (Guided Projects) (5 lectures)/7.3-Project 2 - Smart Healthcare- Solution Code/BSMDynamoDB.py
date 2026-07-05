import boto3
import datetime
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key
import statistics
import itertools
import json


class BSMDynamoDB:
    def __init__(self):
        # Instantiate a Dynamo DB  resource table resources.
        self._dynamodb = boto3.resource('dynamodb')

    # Create table  based on table name, partition key and sort key
    def create_table(self, table_name, partition_key, sort_key):
        print(f"Creating table : {table_name}")
        try:
            table = self._dynamodb.create_table(
                TableName=table_name,
                KeySchema=[
                    {'AttributeName': partition_key, 'KeyType': 'HASH'},
                    {'AttributeName': sort_key, 'KeyType': 'RANGE'}
                    ],
                AttributeDefinitions=[
                    {'AttributeName': partition_key, 'AttributeType': 'S'},
                    {'AttributeName': sort_key, 'AttributeType': 'S'}
                    ],
                ProvisionedThroughput={'ReadCapacityUnits': 10, 'WriteCapacityUnits': 10}
                )
            table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
            print(f".........table creation Done ")
            return self._dynamodb.Table(table_name)
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            print(f'....Skipped due to exception : {error_code} ...  Reason : {error_message}')
            return None

    # Insert raw data in bsm_data table only for testing/PoC.
    # Not  to be used for creating project related bsm raw data in bsm_data table
    def insert_bsm_data(self, device_id, sensor_data_type, value):
        bsm_data_table = self._dynamodb.Table('bsm_data')
        print(f"Inserting data in bsm_data table...")
        for count in range(1, 10):
            value = value+1
            data_item = {
                'device_id': device_id,
                'timestamp': str(datetime.datetime.now()),
                'sensor_data_type': sensor_data_type,
                'value': value}
            try:
                bsm_data_table.put_item(Item=data_item)
                print(f"...Put item ({data_item}  succeeded.")
            except ClientError as e:
                error_code = e.response['Error']['Code']
                error_message = e.response['Error']['Message']
                print(f'....Skipped due to exception : {error_code} ...  Reason : {error_message}')
        return

    # Aggregate function - for each device type aggregation is done at  minute level for all sensor type
    # Read from bsm_data and aggregate into bsm_agg_data table
    def aggregate(self, device_id, from_time, to_time):
        print(f'Aggregation started for device_id: {device_id} from ({from_time}) to ({to_time})')

        # Reading raw data from bsm_data table
        bsm_data_table = self._dynamodb.Table('bsm_data')
        bsm_agg_data_table = self._dynamodb.Table('bsm_agg_data')
        response = bsm_data_table.query(
            KeyConditionExpression=Key('device_id').eq(device_id) & Key('timestamp').between(from_time, to_time))
        print('...Records for aggregation in bsm_data table : ', response['Count'])

        # Sorting and then Grouping the result set by  sensor data type
        bsm_items = itertools.groupby(
            sorted(response["Items"], key=lambda x: x["sensor_datatype"]),
            key=lambda x: x["sensor_datatype"]
        )
        agg_rec_count = 0
        for sensor_type, device_data in bsm_items:
            # Grouping further at minute level
            items_by_minute = itertools.groupby(
                device_data,
                key=lambda x: x["timestamp"][:16]  # first 16 characters including minute
            )
            for minute, items in items_by_minute:
                # generate aggregate stats for that minute
                values_per_minute = [item["value"] for item in items]
                avg = statistics.mean(values_per_minute)
                min_value = min(values_per_minute)
                max_value = max(values_per_minute)
                data_item = {
                    'device_id_datatype': device_id+'_'+sensor_type,
                    'timestamp': minute,
                    'device_id': device_id,
                    'sensor_data_type': sensor_type,
                    'avg': round(avg, 2),
                    'min_value': round(min_value, 2),
                    'max_value': round(max_value, 2)
                }
                bsm_agg_data_table.put_item(Item=data_item)
                agg_rec_count = agg_rec_count + 1
        print(f'...Aggregation completed for {device_id}. Total aggregated records : {agg_rec_count}')
        return

    # Anomaly detection function - for each device type scan aggregated data from bsm_agg_data table.
    # Verify for anomaly based on rule defined in json file and insert into bsm_alert_data
    def anomaly_detection(self, device_id, from_time, to_time):
        print(f'Anomaly Detection : Processing rule for device : {device_id}')

        # fetching rule from rule.json file
        file = open('rule.json')
        anomaly_rule = json.load(file)
        file.close()

        bsm_agg_data = self._dynamodb.Table('bsm_agg_data')
        bsm_alert_data = self._dynamodb.Table('bsm_alert_data')

        # for every anomaly  rule scan and bsm_agg_data table and detect anomaly
        for anomaly_rule in anomaly_rule['rule_data']:
            anomaly_rule_id = anomaly_rule['Rule_id']
            query_key = device_id + '_' + anomaly_rule['sensor_data_type']
            response = bsm_agg_data.query(
                 KeyConditionExpression=Key('device_id_datatype').eq(query_key) &
                 Key('timestamp').between(from_time, to_time))

            # For every record in bsm_agg_data table check if there is anomaly in data for this rile
            print(f'...Rule {anomaly_rule_id} processing for {query_key} from {from_time} to {to_time}: '
                  f'Number of records in bsm_agg_data table :', response['Count'])
            trigger_counter = 0
            anomaly_counter = 0
            for items in response["Items"]:
                anomaly_timestamp = items['timestamp']
                anomaly_type = ''
                anomaly_detected = False

                # check for anomaly
                if int(items['avg']) <= int(anomaly_rule['avg_min']):
                    anomaly_type = 'MIN'
                    anomaly_detected = True
                    trigger_counter = trigger_counter + 1
                elif int(items['avg']) >= int(anomaly_rule['avg_max']):
                    anomaly_type = 'MAX'
                    anomaly_detected = True
                    trigger_counter = trigger_counter + 1  # increment the anomaly counter
                else:
                    trigger_counter = 0  # reset counter in anomaly is not continuous

                # if anomaly is detected continuous for more than threshold value in rule.json
                # then log anomaly in bsm_alert_data table
                if anomaly_detected is True and trigger_counter >= int(anomaly_rule['trigger_count']):
                    print(f'        Alert for device_id ({device_id}); rule ({anomaly_rule_id}); '
                          f'time ({anomaly_timestamp}); breach type : {anomaly_type} Value :', items['avg'])
                    data_item = {
                        'device_id_rule_id': device_id + '_' + anomaly_rule_id,
                        'timestamp': anomaly_timestamp,
                        'device_id': device_id,
                        'rule_id': anomaly_rule_id,
                        'breach_type': anomaly_type
                     }
                    anomaly_counter = anomaly_counter + 1
                    bsm_alert_data.put_item(Item=data_item)
            print(f'...Rule {anomaly_rule_id} processed for {query_key} : Total anomaly detected : {anomaly_counter}')
