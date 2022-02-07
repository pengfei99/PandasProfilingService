import json
import logging
import os
from typing import Optional

import pandas as pd
import pandas_profiling as pp
import pyarrow.parquet as pq
from pandas_profiling import ProfileReport

from dataprofiler.storage.StorageEngineInterface import StorageEngineInterface

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
log.addHandler(handler)


class DataProfiler:
    def __init__(self, storage_engine: StorageEngineInterface, tmp_dir: str):
        self.storage_engine = storage_engine
        self.tmp_dir = tmp_dir

    def save_report(self, input_file_path: str, file_format: str, report_format: str, report_destination: str,
                    separator=',', na_val='', report_title="", report_name="", minimal=True, explorative=False):
        """
        This function takes a input file path, generate a data profiling report, and copy it to a output path

        :param report_destination: the path to store output report
        :param explorative: remove some stats from column detail page for better speed
        :param minimal: remove correlation and duplication row detection for better speed.
        :param input_file_path: full input file path. if s3 path, it must be in format s3://{bucket_name}/{bucket_key}
        :param file_format: input data file format, only csv, json and parquet are accepted
        :param report_format: output report format, only html and json are accepted
        :param separator: if input data file format is csv, you can specify a custom csv
        :param na_val: if input data file format is csv, you can specify a custom na_val
        :param report_title: The title of the report in the generated report file
        :param report_name: The name of the generated report file
        :return: if success, return nothing, otherwise raise exception

        """
        local_path = self.make_report(input_file_path, file_format, report_format, separator, na_val, report_title,
                                      report_name, minimal=minimal, explorative=explorative)
        if local_path is not None:
            full_report_path = f"{report_destination}/{report_name}.{report_format}"
            if self.storage_engine.upload_data(local_path, full_report_path):
                log.info(f"Report has been generated and uploaded to {full_report_path}")
            else:
                log.error(f"Fail to upload report to {full_report_path}")
                raise
        else:
            log.error(f"Fail to generate report for {input_file_path}")
            raise

    def make_report(self, input_file_path: str, file_format: str, report_format: str, separator=',', na_val='',
                    report_title="", report_name="", minimal=True, explorative=False) -> Optional[str]:
        """
        This function takes a data file path, and generate a data profile report, the parameter such as separator, na_val
        is optional, and only has effect if file_format is csv. If the report_title and report_name are empty, we
        will generate one based on input file name

        :param explorative: remove some stats from column detail page for better speed
        :param minimal: remove correlation and duplication row detection for better speed.
        :param input_file_path: full input file path. if s3 path, it must be in format s3://{bucket_name}/{bucket_key}
        :param file_format: input data file format, only csv, json and parquet are accepted
        :param report_format: output report format, only html and json are accepted
        :param separator: if input data file format is csv, you can specify a custom csv
        :param na_val: if input data file format is csv, you can specify a custom na_val
        :param report_title: The title of the report in the generated report file
        :param report_name: The name of the generated report file
        :return: if success, return the full path of the generated report, otherwise return None

        Note the param report_name should not contain format. The final report_name will be
             built report_name.report_format
        """
        # build local file path for download
        source_file_name = self.storage_engine.get_short_file_name(input_file_path)
        local_path = f"{self.tmp_dir}/{source_file_name}"
        # build report title
        if report_title == "":
            report_title = f"Profiling report of {source_file_name}"
        # build report name, if none is given
        if report_name == "":
            report_name = f"{source_file_name}_report.{report_format}"
        else:
            report_name = f"{report_name}.{report_format}"
        # if download success, produce report
        if self.storage_engine.download_data(input_file_path, local_path):
            df = DataProfiler.get_source_df(local_path, file_format, separator, na_val)
            # if convert to pandas dataframe is successful, start generate report
            if df is not None:
                # if generate report is successful, log success
                if DataProfiler.generate_report(df, self.tmp_dir, report_name, report_title, minimal=minimal,
                                                explorative=explorative):
                    report_full_path = f"{self.tmp_dir}/{report_name}"
                    log.info(f"Successfully generated report for {input_file_path}, report location {report_full_path}")
                    return report_full_path
                else:
                    log.exception(f"Fail to generate profiling report for {input_file_path}")
                    return None
            else:
                log.exception("Fail to convert data to pandas dataframe")
                return None
        else:
            log.exception(f"Fail to download file from {input_file_path}")
            return None

    @staticmethod
    def get_source_df(input_file_path: str, file_format: str, separator=',', na_val='') -> Optional[pd.DataFrame]:
        """
        This function read various data source file (e.g. csv, json, parquet), then return a pandas data frame of the
        data source file

        :param input_file_path: path of the input file
        :param file_format: file format, only accept csv, json, and parquet
        :param separator: if file is csv, can specify a separator
        :param na_val: if file is csv, can specify a null value identifier
        :return: a pandas dataframe, or none, if the file format is not supported
        """
        if file_format == "csv":
            df = pd.read_csv(input_file_path, sep=separator, na_values=[na_val])
        elif file_format == "json":
            rows = []
            for line in open(input_file_path, 'r'):
                rows.append(json.loads(line))
            df = pd.DataFrame(rows)
            # I don't use df = pd.read_json(input_file_path), because it can't handle null value in json file correctly.

        elif file_format == "parquet":
            table = pq.read_table(input_file_path)
            df = table.to_pandas()
        else:
            log.error("The input data format is not supported")
            df = None
        return df

    @staticmethod
    def generate_report(df: pd.DataFrame, output_path: str, report_name: str, report_title="Profiling Report",
                        minimal=True, explorative=False) -> bool:
        """
        This function generates a data profiling report without metadata and column description

        :param explorative: remove some stats from column detail page for better speed
        :param minimal: remove correlation and duplication row detection for better speed.
        :param df: input pandas dataframe which we will profile
        :param output_path: output report parent directory
        :param report_name: the name of the output report
        :param report_title: the title of the report, default value is 'Profiling Report'
        :return: return true if the report is generated successfully
        """

        try:
            os.makedirs(output_path, exist_ok=True)
            profile = ProfileReport(df, title=report_title, minimal=minimal, explorative=explorative)
            report_full_path = f"{output_path}/{report_name}"
            profile.to_file(report_full_path)
        except Exception as e:
            log.exception(f"Fail to generate report. {e}")
            return False
        else:
            log.info(f"Profiling Report is successfully generated at {report_full_path} ")
            return True

    @staticmethod
    def generate_report_with_meta(df: pd.DataFrame, dataset_metadata: dict, columns_description: dict) -> \
            Optional[pp.ProfileReport]:
        """
        This function generates report with metadata and column description. Check below example for more information about
        the format of metadata and column description


        :param df: input pandas dataframe which we will profile
        :param dataset_metadata:
        :param columns_description:
        :return: return a ProfileReport that can be written in html or json

        Examples:

        dataset_metadata = {
        "description": "This profiling report was generated by using the census dataset.",
        "creator": "toto",
        "author": "toto",
        "copyright_holder": "toto LLC",
        "copyright_year": "2020",
        "url": "http://toto.org"}

        columns_description = {
        "descriptions": {
            "column_name": "column_description",
            ...
            "column_name": "column_description", }
               }

        """
        try:
            profile = ProfileReport(df, title="Agriculture Data", dataset=dataset_metadata,
                                    variables=columns_description)
        except Exception as e:
            log.exception(f"Fail to generate report. {e}")
            return None
        else:
            log.info(f"Profiling Report is successfully generated")
            return profile


def main():
    pass


if __name__ == "__main__":
    main()
