import argparse
import logging

from dataprofiler.storage.LocalStorageEngine import LocalStorageEngine
from dataprofiler import *


def main():
    log = logging.getLogger(__name__)
    log.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    log.addHandler(handler)
    args_parser = argparse.ArgumentParser(description='Generate data profiling report')
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
                             default=None,
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
    args = args_parser.parse_args()
    if args.storage_type == "local":
        storage_engine = LocalStorageEngine()
