import argparse
import logging


def main():
    log = logging.getLogger(__name__)
    log.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    log.addHandler(handler)
    args_parser = argparse.ArgumentParser(description='Generate data profiling report')
    args_parser.add_argument("--input_file",
                             metavar="full_file_path",
                             required=True,
                             help="Full file path of the input file which you want to profile")
    args_parser.add_argument("--report_path",
                             metavar="report_output_path",
                             default=None,
                             help="Parent dir for storing output report")
    args_parser.add_argument("--report_format",
                             metavar="storage_type",
                             choices=['local', 's3', 'hdfs'],
                             required=True,
                             help="The storage type that you want to connect to. Possible values: "
                                  "'local', 's3', 'hdfs'"
                             )