import argparse
import logging
import sys

from dataprofiler.DataProfiler import DataProfiler
from dataprofiler.storage.LocalStorageEngine import LocalStorageEngine
import os

from dataprofiler.storage.S3StorageEngine import S3StorageEngine


def main():
    log = logging.getLogger(__name__)
    log.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    log.addHandler(handler)
    args_parser = argparse.ArgumentParser(description='Generate data profiling report')
    args_parser.add_argument("--action",
                             metavar="action",
                             choices=['render', 'save'],
                             required=True,
                             help="The action that CLI provides. Possible values: 'render', 'save'"
                             )
    args_parser.add_argument("--storage_type",
                             metavar="storage_type",
                             choices=['local', 's3'],
                             required=True,
                             help="The storage type that you want to connect to. Possible values: "
                                  "'local', 's3'"
                             )
    args_parser.add_argument("--input_file",
                             metavar="full_file_path",
                             required=True,
                             help="Full file path of the input file which you want to profile")
    args_parser.add_argument("--file_format",
                             metavar="full_file_path",
                             choices=['parquet', 'csv', 'json'],
                             required=True,
                             help="File format of the input file which you want to profile, Possible values: csv ,json")
    args_parser.add_argument("--report_path",
                             metavar="report_output_path",
                             required=True,
                             help="Parent dir for storing output report")
    args_parser.add_argument("--report_format",
                             metavar="storage_type",
                             choices=['html', 'json'],
                             help="The output report format Possible values: 'html', 'json' "
                             )
    args_parser.add_argument("--separator",
                             metavar="csv_file_separator",
                             default=None,
                             help="Separator for csv file")
    args_parser.add_argument("--na_val",
                             metavar="csv_file_na",
                             default=None,
                             help="Null value identifier for csv file")
    args_parser.add_argument("--report_title",
                             metavar="title",
                             default="",
                             help="The title of the report in the generated report file")
    args_parser.add_argument("--report_save_path",
                             metavar="destination",
                             default=None,
                             help="The path to save the generated report")
    args_parser.add_argument("--report_name",
                             metavar="name",
                             default=None,
                             help="The name of the generated report")
    args = args_parser.parse_args()

    if args.storage_type == "local":
        storage_engine = LocalStorageEngine()
    elif args.storage_type == "s3":
        endpoint = "https://" + os.getenv("AWS_S3_ENDPOINT")
        access_key = os.getenv("AWS_ACCESS_KEY_ID")
        secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        session_token = os.getenv("AWS_SESSION_TOKEN")
        storage_engine = S3StorageEngine(endpoint, access_key, secret_key, session_token)
    else:
        log.error(f"We don't support the storage type {args.storage_type} for now, please enter a "
                  f"storage type that we support")
        storage_engine = None
        exit(1)

    # build a data profiler
    profiler = DataProfiler(storage_engine, args.report_path)

    #
    if args.action == "render":
        try:
            profiler.make_report(input_file_path=args.input_file, file_format=args.file_format,
                                 report_format=args.report_format, separator=args.separator, na_val=args.na_val,
                                 report_title=args.report_title, report_name=args.report_name)
        except Exception as e:
            log.error(e)
            sys.exit(1)

    if args.action == "save":
        try:
            profiler.save_report(input_file_path=args.input_file, file_format=args.file_format,
                                 report_format=args.report_format, separator=args.separator, na_val=args.na_val,
                                 report_title=args.report_title, report_name=args.report_name,
                                 report_destination=args.report_save_path)
        except Exception as e:
            log.error(e)
            sys.exit(1)


if __name__ == '__main__':
    main()
