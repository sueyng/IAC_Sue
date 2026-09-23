"""
AWS Glue ETL job for transforming audit log data from landing zone to Iceberg tables.

This script handles parquet files with inconsistent schemas by reading each file
individually and unifying them before transformation.
"""

import sys
import boto3
import pytz
import pyspark

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.conf import SparkConf
from pyspark.sql import DataFrame
from pyspark.sql.functions import days, lit
from pyspark.sql.types import (
    LongType,
    StringType,
    StructField,
    StructType,
    TimestampType,
    ArrayType,
)

from audit_transform import transform_audit_log


def get_default_iceberg_spark_conf(s3_bucket: str, catalog_name: str) -> SparkConf:
    """
    Gets the default spark configuration for Iceberg.

    Parameters
    ----------
    s3_bucket : str
        S3 bucket name for the warehouse
    catalog_name : str
        Name of the Iceberg catalog

    Returns
    -------
    SparkConf
        Configured Spark configuration object
    """
    conf = SparkConf()
    conf.set(
        "spark.sql.extensions",
        "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions",
    ).set(
        f"spark.sql.catalog.{catalog_name}",
        "org.apache.iceberg.spark.SparkCatalog",
    ).set(
        f"spark.sql.catalog.{catalog_name}.warehouse",
        f"s3://{s3_bucket}",
    ).set(
        f"spark.sql.catalog.{catalog_name}.catalog-impl",
        "org.apache.iceberg.aws.glue.GlueCatalog",
    ).set(
        f"spark.sql.catalog.{catalog_name}.io-impl",
        "org.apache.iceberg.aws.s3.S3FileIO",
    ).set(
        "spark.sql.defaultCatalog", catalog_name
    ).set(
        "write.parquet.compression-codec", "snappy"
    ).set(
        "spark.sql.session.timeZone", "Singapore"
    )
    return conf


def create_s3_iceberg_table(
    *,
    df: DataFrame,
    full_table_name: str,
    compaction_strategy: str,
    snapshot_lifetime_ms: int,
    min_snapshots: str,
    s3_location: str,
    partition_cols: List[pyspark.sql.Column],
) -> None:
    """
    Creates an Iceberg table in S3.

    Parameters
    ----------
    df : DataFrame
        DataFrame with the schema for the table
    full_table_name : str
        Full table identifier (catalog.database.table)
    compaction_strategy : str
        Compaction strategy (copy-on-write or merge-on-read)
    snapshot_lifetime_ms : int
        Snapshot lifetime in milliseconds
    min_snapshots : str
        Minimum snapshots to keep after expiry
    s3_location : str
        S3 location for table storage
    partition_cols : List[Column]
        Columns for partitioning
    """
    df.writeTo(full_table_name).tableProperty(
        "format-version", "2"
    ).tableProperty(
        "location", s3_location
    ).tableProperty(
        "write.update.mode", compaction_strategy
    ).tableProperty(
        "write.delete.mode", compaction_strategy
    ).tableProperty(
        "write.merge.mode", compaction_strategy
    ).tableProperty(
        "history.expire.max-snapshot-age-ms", str(snapshot_lifetime_ms)
    ).tableProperty(
        "history.expire.min-snapshots-to-keep", str(min_snapshots)
    ).tableProperty(
        "write.metadata.delete-after-commit.enabled", "true"
    ).tableProperty(
        "write.metadata.previous-versions-max", str(min_snapshots)
    ).partitionedBy(
        *partition_cols
    ).createOrReplace()


class AuditLogTransformer:
    """
    Transforms audit log data from raw parquet files to Iceberg tables.

    Handles parquet files with inconsistent schemas by reading each file
    individually and unifying them with a common schema.
    """

    # Target schema for transformed data
    TARGET_SCHEMA = StructType([
        StructField("id", StringType(), True),
        StructField("correlationid", StringType(), True),
        StructField("startdatetime_utc", TimestampType(), True),
        StructField("enddatetime_utc", TimestampType(), True),
        StructField("clientid", StringType(), True),
        StructField("clientname", StringType(), True),
        StructField("location", StringType(), True),
        StructField("clientuser_id", StringType(), True),
        StructField("clientmessageid", StringType(), True),
        StructField("clienttime", StringType(), True),
        StructField("method", StringType(), True),
        StructField("path", StringType(), True),
        StructField("query", StringType(), True),
        StructField("headers", ArrayType(StringType()), True),
        StructField("action", StringType(), True),
        StructField("actiontype", StringType(), True),
        StructField("operation", StringType(), True),
        StructField("apidirection", StringType(), True),
        StructField("target_typename", StringType(), True),
        StructField("target_reference", StringType(), True),
        StructField("target_resourceid", StringType(), True),
        StructField("target_versionid", StringType(), True),
        StructField("target_display", StringType(), True),
        StructField("responsestatus", LongType(), True),
        StructField("operationoutcome", StringType(), True),
        StructField("createdby", StringType(), True),
    ])

    def __init__(self, args: Dict[str, str], spark: pyspark.sql.SparkSession, glue_context: GlueContext):
        self.args = args
        self.spark = spark
        self.glue_context = glue_context
        self.logger = glue_context.get_logger()
        self.job = Job(glue_context)
        self.job.init("auditlog job", args)
        self.s3_client = boto3.client('s3')
        self.glue_client = boto3.client('glue')

        self._resolve_date_parameters()

    def _resolve_date_parameters(self) -> None:
        """Resolve CDC_START and CDC_END parameters, defaulting to yesterday."""
        yesterday = (datetime.now(pytz.timezone("Asia/Singapore")) - timedelta(1)).strftime("%Y%m%d")

        if self.args["CDC_START"].lower() == "null":
            self.args["CDC_START"] = yesterday
        if self.args["CDC_END"].lower() == "null":
            self.args["CDC_END"] = yesterday

    def run(self) -> None:
        """Main entry point for the transformation job."""
        self._process_audit_logs()
        self.job.commit()

    def _get_table_location(self) -> str:
        """Get the S3 location of the raw table from Glue catalog."""
        response = self.glue_client.get_table(
            DatabaseName=self.args["RAW_DATALAKE"],
            Name=self.args["RAW_TABLE"]
        )
        return response['Table']['StorageDescriptor']['Location']

    def _get_partition_paths(self, base_location: str) -> List[str]:
        """Build S3 paths for date range partitions."""
        partition_paths = []
        start_date = datetime.strptime(self.args["CDC_START"], "%Y%m%d")
        end_date = datetime.strptime(self.args["CDC_END"], "%Y%m%d")

        current_date = start_date
        while current_date <= end_date:
            partition_path = f"{base_location}{current_date.strftime('%Y%m%d')}/"
            partition_paths.append(partition_path)
            current_date += timedelta(days=1)

        return partition_paths

    def _list_parquet_files(self, partition_paths: List[str]) -> List[str]:
        """List all parquet files in the given partition paths."""
        parquet_files = []

        for partition_path in partition_paths:
            # Parse bucket and prefix from S3 path
            path_without_scheme = partition_path.replace("s3://", "")
            bucket = path_without_scheme.split("/", 1)[0]
            prefix = path_without_scheme.split("/", 1)[1] if "/" in path_without_scheme else ""

            response = self.s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix)
            for obj in response.get('Contents', []):
                if obj['Key'].endswith('.parquet'):
                    parquet_files.append(f"s3://{bucket}/{obj['Key']}")

        return parquet_files

    def _read_parquet_files(self, parquet_files: List[str]) -> List[DataFrame]:
        """Read each parquet file individually."""
        dataframes = []

        for parquet_file in parquet_files:
            try:
                df = self.spark.read.parquet(parquet_file)
                dataframes.append(df)
                self.logger.info(f"Read {parquet_file}: columns = {df.columns}")
            except Exception as e:
                self.logger.warn(f"Could not read {parquet_file}: {e}")

        return dataframes

    def _unify_dataframes(self, dataframes: List[DataFrame]) -> Optional[DataFrame]:
        """
        Unify DataFrames with different schemas into a single DataFrame.

        This handles the case where different parquet files have different columns
        by building a union of all column types and adding missing columns with null values.
        """
        if not dataframes:
            return None

        # Build column name -> type mapping from all DataFrames
        column_types = {}
        for df in dataframes:
            for field in df.schema.fields:
                if field.name not in column_types:
                    column_types[field.name] = field.dataType

        all_columns = sorted(column_types.keys())
        self.logger.info(f"Unified columns: {all_columns}")

        # Add missing columns to each DataFrame with correct types
        unified_dfs = []
        for df in dataframes:
            for col_name, col_type in column_types.items():
                if col_name not in df.columns:
                    df = df.withColumn(col_name, lit(None).cast(col_type))
            unified_dfs.append(df.select(*all_columns))

        # Union all DataFrames
        result = unified_dfs[0]
        for other_df in unified_dfs[1:]:
            result = result.unionByName(other_df)

        return result

    def _table_exists(self, table_name: str) -> bool:
        """Check if a table exists in the Glue catalog."""
        try:
            self.glue_context.create_data_frame.from_catalog(
                database=self.args["TRANS_DATALAKE"],
                table_name=table_name
            )
            return True
        except Exception as e:
            self.logger.warn(str(e))
            return False

    def _merge_into_table(self, df: DataFrame, full_table_name: str) -> None:
        """
        Merge DataFrame into Iceberg table using upsert logic.

        Updates existing records matching by id, inserts new records.

        Parameters
        ----------
        df : DataFrame
            Source DataFrame to merge
        full_table_name : str
            Full table identifier (catalog.database.table)
        """
        df.createOrReplaceTempView("source_data")

        columns = df.columns
        update_set = ", ".join([f"target.{c} = source.{c}" for c in columns if c != "id"])
        insert_cols = ", ".join(columns)
        insert_vals = ", ".join([f"source.{c}" for c in columns])

        merge_sql = f"""
            MERGE INTO {full_table_name} AS target
            USING source_data AS source
            ON target.id = source.id
            WHEN MATCHED THEN UPDATE SET {update_set}
            WHEN NOT MATCHED THEN INSERT ({insert_cols}) VALUES ({insert_vals})
        """

        self.spark.sql(merge_sql)
        self.logger.info(f"Merged records into {full_table_name}")

    def _write_to_iceberg(self, df: DataFrame, table_name: str, s3_location: str) -> None:
        """Write DataFrame to Iceberg table using MERGE for deduplication."""
        snapshot_lifetime_ms = int(self.args.get("SNAPSHOT_EXPIRY_HOURS", 168)) * 60 * 60 * 1000
        full_table_name = f"{self.args['CATALOG_NAME']}.{self.args['TRANS_DATALAKE']}.{table_name}"

        if not self._table_exists(table_name):
            create_s3_iceberg_table(
                df=self.spark.createDataFrame([], df.schema),
                full_table_name=full_table_name,
                compaction_strategy=self.args.get("COMPACTION_STRATEGY", "copy-on-write"),
                snapshot_lifetime_ms=snapshot_lifetime_ms,
                min_snapshots=self.args.get("MIN_SNAPSHOTS_TO_KEEP", "5"),
                s3_location=s3_location,
                partition_cols=[days("startdatetime_utc")],
            )
            # First run - append since table is empty
            df.writeTo(full_table_name).append()
        else:
            # Use MERGE for upsert to handle duplicates
            self._merge_into_table(df, full_table_name)

    def _process_audit_logs(self) -> None:
        """Main processing logic for audit logs."""
        # Get table location and partition paths
        base_location = self._get_table_location()
        partition_paths = self._get_partition_paths(base_location)
        self.logger.info(f"Reading from partitions: {partition_paths}")

        # List and read parquet files
        parquet_files = self._list_parquet_files(partition_paths)
        self.logger.info(f"Found {len(parquet_files)} parquet files")

        if not parquet_files:
            self.logger.info("No parquet files found.")
            return

        # Read and unify DataFrames
        dataframes = self._read_parquet_files(parquet_files)
        if not dataframes:
            self.logger.info("No data could be read.")
            return

        df = self._unify_dataframes(dataframes)
        if df is None or df.count() == 0:
            self.logger.info("No raw data found for the specified date range.")
            return

        # Apply transformations
        df = transform_audit_log(df, self.TARGET_SCHEMA)

        record_count = df.count()
        if record_count == 0:
            self.logger.info("No audit log records after transformation.")
            return

        self.logger.info(f"Processing {record_count} audit log records.")

        # Write to Iceberg
        s3_location = f"s3://{self.args['S3_DST_BUCKET']}/{self.args['RAW_TABLE']}/{self.args['S3_DST_PREFIX']}"
        self._write_to_iceberg(df, self.args["TRANS_TABLE"], s3_location)


if __name__ == "__main__":
    args = getResolvedOptions(
        sys.argv,
        [
            "CDC_START",
            "CDC_END",
            "S3_DST_BUCKET",
            "S3_DST_PREFIX",
            "RAW_DATALAKE",
            "TRANS_DATALAKE",
            "CATALOG_NAME",
            "RAW_TABLE",
            "TRANS_TABLE",
            "SNAPSHOT_EXPIRY_HOURS",
            "COMPACTION_STRATEGY",
            "MIN_SNAPSHOTS_TO_KEEP",
        ],
    )

    conf = get_default_iceberg_spark_conf(args["S3_DST_BUCKET"], args["CATALOG_NAME"])
    sc = SparkContext(conf=conf)
    glue_context = GlueContext(sc)
    spark = glue_context.spark_session

    transformer = AuditLogTransformer(args, spark, glue_context)
    transformer.run()
