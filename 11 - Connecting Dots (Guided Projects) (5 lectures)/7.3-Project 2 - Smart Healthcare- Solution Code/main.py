from BSMDynamoDB import BSMDynamoDB
# Author :  Rajesh K. Sinha, ACSE_Apr_22
# Purpose : Project for IoT Cloud Processing  assignment.


START_TIME = '2022-10-09 15:22:00'
END_TIME = '2022-10-09 16:32:00'

if __name__ == '__main__':
    # create dynamoDB object for DB operations
    bsm_db = BSMDynamoDB()

    # bsm_data table operations is only for testing/PoC.
    # Not  to be used for creating bsm raw data in bsm_data table
    # bsm_data_table = bsm_db.create_table('bsm_data', 'device_id', 'timestamp')
    # bsm_db.insert_bsm_data('BSM_G101', 'SPO2', 88)

    # Create table for aggregation (will skip if table exists) .
    # Read from bsm_data table and aggregate every minute data for specific duration
    print('********Aggregating data for devices ****************')
    bsm_agg_data = bsm_db.create_table('bsm_agg_data', 'device_id_datatype', 'timestamp')
    bsm_db.aggregate('BSM_G101', START_TIME, END_TIME)
    bsm_db.aggregate('BSM_G102', START_TIME, END_TIME)
    bsm_db.aggregate('BSM_G103', START_TIME, END_TIME)

    # Create table for storing alerts  (will skip if table exists) .
    # Read from bsm_Agg_data for specific duration to detect anomaly and store in alert table
    print('********Processing Rules ****************')
    bsm_alert_data = bsm_db.create_table('bsm_alert_data', 'device_id_rule_id', 'timestamp')
    bsm_db.anomaly_detection('BSM_G101', START_TIME, END_TIME)
    bsm_db.anomaly_detection('BSM_G102', START_TIME, END_TIME)
    bsm_db.anomaly_detection('BSM_G103', START_TIME, END_TIME)
