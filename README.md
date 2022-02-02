# PandasProfilingService
0. 
1. get user-input, input file path, if output report path is not null, report format (html, json)
2. download data from s3
3. parse file type(accepted format json, csv ,parquet)
4. generate report (option param: metadata, column description )
5. upload report to s3

## code example
profiler make report of S3 data example

```python
    output_path = "/tmp"
    endpoint = "https://minio.lab.sspcloud.fr"
    access_key = "changeMe"
    secret = "changeMe"
    storage_engine = S3StorageEngine(endpoint=endpoint, access_key=access_key, secret_key=secret, session_token=None)
    profile = DataProfiler(storage_engine, output_path)
    file_path = "s3a://pengfei/diffusion/data_profiling/adult.csv"
    profile.make_report(file_path, "csv", "html", ",", na_val="?")
```

profiler make report of local data example

```python
    csv_file_path = "../data/adult.csv"
    output_path = "/tmp"
    storage_engine = LocalStorageEngine()
    profile = DataProfiler(storage_engine, output_path)
    profile.make_report(csv_file_path, "csv", "html", ",", na_val="?")
```

call main.py
```shell
python dataprofiler/main.py --storage_type local --input_file /home/pliu/git/PandasProfilingService/data/adult.csv --file_format csv --report_path /tmp --report_format html --separator , --na_val ?
```


## Troubleshoot

### module not found

This error is caused by python path, you need to set up your python path with following command

```shell
export PYTHONPATH=${PYTHONPATH}:~/git/PandasProfilingService
```

