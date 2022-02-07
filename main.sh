#!/bin/sh

if [ "$FILE_FORMAT" = "parquet" ];
then python dataprofiler/main.py --action render --storage_type s3 --input_file $INPUT_FILE --file_format parquet --report_render_path /html --report_format html --report_name index
elif [ "$FILE_FORMAT" = "json" ];
then python dataprofiler/main.py --action render --storage_type s3 --input_file $INPUT_FILE --file_format json --report_render_path /html --report_format html --report_name index
elif [ "$FILE_FORMAT" = "csv" ];
then
    if [ -z "$NA_VAL" ];
    then python dataprofiler/main.py --action render --storage_type s3 --input_file $INPUT_FILE --file_format $FILE_FORMAT --separator $SEPARATOR --report_render_path /html --report_format html --report_name index
    else python dataprofiler/main.py --action render --storage_type s3 --input_file $INPUT_FILE --file_format $FILE_FORMAT --separator $SEPARATOR --na_val $NA_VAL --report_render_path /html --report_format html --report_name index
    fi;
fi;