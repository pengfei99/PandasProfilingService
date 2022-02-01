# PandasProfilingService
0. get user-input, input file path, if output report path is not null, report format (html, json)
1. download data from s3
2. parse file type(accepted format json, csv ,parquet)
3. generate report (option param: metadata, column description )
4. upload report to s3