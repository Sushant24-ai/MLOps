import os
import sys
import pickle
import pandas as pd


def main(year, month):

    input_file = get_input_path(year, month)
    output_file = get_output_path(year, month)
    
    print("Loading model.bin ...")
    with open('model.bin', 'rb') as f_in:
        dv, lr = pickle.load(f_in)

    categorical = ['PULocationID', 'DOLocationID']

    print(f"Read input file: {input_file}")
    df = read_data(input_file, categorical)
    df['ride_id'] = f'{year:04d}/{month:02d}_' + df.index.astype('str')

    print("Making transformations ...")
    dicts = df[categorical].to_dict(orient='records')
    X_val = dv.transform(dicts)

    print("Making predictions ...")
    y_pred = lr.predict(X_val)

    print('Predicted mean duration:', y_pred.mean())

    df_result = pd.DataFrame()
    df_result['ride_id'] = df['ride_id']
    df_result['predicted_duration'] = y_pred

    print(f"Write result to file {output_file}")
    save_data(df_result, output_file)
    

def prepare_data(df, categorical):
    df['duration'] = df.tpep_dropoff_datetime - df.tpep_pickup_datetime
    df['duration'] = df.duration.dt.total_seconds() / 60

    df = df[(df.duration >= 1) & (df.duration <= 60)].copy()

    df[categorical] = df[categorical].fillna(-1).astype('int').astype('str')
    return df

def get_input_path(year, month):
    default_input_pattern = 'https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_{year:04d}-{month:02d}.parquet'
    input_pattern = os.getenv('INPUT_FILE_PATTERN', default_input_pattern)
    return input_pattern.format(year=year, month=month)

def get_output_path(year, month):
    default_output_pattern = 's3://nyc-duration-prediction-alexey/taxi_type=fhv/year={year:04d}/month={month:02d}/predictions.parquet'
    output_pattern = os.getenv('OUTPUT_FILE_PATTERN', default_output_pattern)
    return output_pattern.format(year=year, month=month)


def read_data(filename, categorical):

    S3_ENDPOINT_URL = os.getenv('S3_ENDPOINT_URL')
    
    if S3_ENDPOINT_URL is None:
        df = pd.read_parquet(filename)
    else:
        options = {
            'client_kwargs': {
                'endpoint_url': S3_ENDPOINT_URL
            }
        }
        df = pd.read_parquet(filename, storage_options=options)

    return prepare_data(df, categorical)    

def save_data(df, filename):
    S3_ENDPOINT_URL = os.getenv('S3_ENDPOINT_URL')
    
    if S3_ENDPOINT_URL is None:
        df.to_parquet(filename, engine='pyarrow', index=False)
    else:
        options = {
            'client_kwargs': {
                'endpoint_url': S3_ENDPOINT_URL
            }
        }
        df.to_parquet(filename, storage_options=options)

    
if __name__ == '__main__':
    year = int(sys.argv[1])
    month = int(sys.argv[2])
    main(year, month)
