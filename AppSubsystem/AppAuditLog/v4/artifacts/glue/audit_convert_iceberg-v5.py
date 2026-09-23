import sys
import pytz
import pyspark

from datetime import datetime, timedelta, timezone
from typing import Dict, List
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.conf import SparkConf

# from pyspark.sql.functions import days, to_timestamp, col, when, array, size, lit
from pyspark.sql.functions import *
from pyspark.sql.types import (
    DoubleType,
    LongType,
    StringType,
    StructField,
    StructType,
    TimestampType,
    ArrayType
)

def get_default_iceberg_spark_conf(s3_bucket: str, catalog_name: str) -> SparkConf:
    """
    Gets the default HSAR spark configuration for iceberg.

    Parameters
    ----------
    s3_bucket : str
        S3 bucket name
    catalog_name : str
        Name of the iceberg catalog

    Returns
    -------
    SparkConf
        Spark configuration object
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
    
def get_latest_snapshot_id(
    spark: pyspark.sql.SparkSession,
    df: pyspark.sql.DataFrame,
    catalog_name: str,
    datalake: str,
    table_name: str,
) -> str:
    """
    Gets the latest snapshot id from the iceberg table.

    Parameters
    ----------
    df : pyspark.sql.DataFrame
        Dataframe to get the snapshot id
    catalog_name : str
        Name of the catalog
    datalake : str
        Name of the datalake
    table_name : str
        Name of the table

    Returns
    -------
    str
        Latest snapshot id
    """
    df.createOrReplaceTempView(table_name)
    df_res = spark.sql(
        f"SELECT snapshot_id FROM {catalog_name}.{datalake}.{table_name}.history ORDER BY made_current_at DESC LIMIT 1"
    )
    return str(df_res.collect()[0][0])

def create_s3_iceberg_table(
    *,
    df: pyspark.sql.DataFrame,
    full_table_name: str,
    compaction_strategy: str,
    snapshot_lifetime_ms: int,
    min_snapshots: str,
    s3_location: str,
    partition_cols: List[pyspark.sql.Column],
) -> None:
    """
    Creates or appends an iceberg table to s3.

    Parameters
    ----------
    df : pyspark.sql.DataFrame
        Dataframe to write to iceberg table
    full_table_name : str
        Full identifier of the table. Example: catalog_name.datalake_name.table_name
    compaction_strategy : str
        Compaction strategy. In iceberg, it is copy-on-write or merge-on-read
    snapshot_lifetime_ms : int
        Snapshot lifetime in milliseconds
    min_snapshots : str
        Minimum number of snapshots to keep after snapshot expiry
    s3_location : str
        S3 location where the table is stored.
        Example: s3://bucket-name/path/to/table
    partition_cols : List[pyspark.sql.Column]
        Columns to partition the table. Also accepts an iceberg hidden partition column
    """
    df.writeTo(full_table_name).tableProperty("format-version", "2").tableProperty(
        "location", s3_location
    ).tableProperty("write.update.mode", compaction_strategy).tableProperty(
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
    def __init__(self, args: Dict[str, str], spark, glueContext):
        self.args = args
        self.spark = spark
        self.glueContext = glueContext
        self.logger = glueContext.get_logger()
        self.job = Job(glueContext)
        self.job.init("auditlog job", args)
        
        self.args["CDC_START"] = (
            (datetime.now(pytz.timezone("Asia/Singapore")) - timedelta(1)).strftime(
                "%Y%m%d"
            )
            if self.args["CDC_START"].lower() == "null"
            else self.args["CDC_START"]
        )
        self.args["CDC_END"] = (
            (datetime.now(pytz.timezone("Asia/Singapore")) - timedelta(1)).strftime(
                "%Y%m%d"
            )
            if self.args["CDC_END"].lower() == "null"
            else self.args["CDC_END"]
        )
    
    def run(self):
        self.create_auditlog_df()
        self.job.commit()

    def create_auditlog_df(self) -> pyspark.sql.DataFrame:
        df = self.glueContext.create_dynamic_frame.from_catalog(
            database=self.args["RAW_DATALAKE"],
            table_name=self.args["RAW_TABLE"],
            push_down_predicate=f"partition_0 between '{self.args['CDC_START']}' and '{self.args['CDC_END']}'",
            transformation_ctx="datasource0",
        ).toDF()

        # in case of empty dataframe, return directly
        if df.count() == 0:
            return

        df = df.withColumn(
            "Headers",
            when(
                col("Headers").isNull() | (size(col("Headers")) == 0),
                array(lit("")).cast(ArrayType(StringType()))
                ).otherwise(col("Headers"))
            )
        # Convert the timestamp columns to UTC
        df = df.withColumn(
            "startdatetime_utc", to_timestamp("startdatetime")
        ).withColumn(
            "enddatetime_utc", to_timestamp("enddatetime")
        )

        # Convert to lower case
        for col_name in df.columns:
            df = df.withColumnRenamed(col_name, col_name.lower())
        current_cols = [x for x in df.columns]
        expected_cols = self.schema().fieldNames()
        # Ensure all columns in the schema are present in the DataFrame
        for field in self.schema().fields:
            if field.name not in current_cols:
                df = df.withColumn(field.name, pyspark.sql.functions.lit(None).cast(field.dataType))

        # Drop columns that are not in the schema
        columns_to_drop = [col_name for col_name in df.columns if col_name not in expected_cols]
        df = df.drop(*columns_to_drop)
        df = df.select(self.schema().fieldNames())
        
        count = df.count()
        if count == 0:
            self.logger.info("No auditlog payloads to process.")
            self.job.commit()
            return
        
        self.write_to_s3(
            df=df,
            table_name=self.args["TRANS_TABLE"],
            s3_location=f"s3://{self.args['S3_DST_BUCKET']}/{self.args['RAW_TABLE']}/{self.args['S3_DST_PREFIX']}",
            partition_col=days("startdatetime_utc"),
        )
        return
        
    def schema(self) -> StructType:
        return StructType(
            [
                StructField("id", StringType(), False),
                StructField("correlationid", StringType(), True),
                StructField("startdatetime_utc", TimestampType(), False),
                StructField("enddatetime_utc", TimestampType(), False),
                StructField("clientid", StringType(), True),
                StructField("clientname", StringType(), True),
                StructField("location", StringType(), True),
                StructField("clientuser_id", StringType(), True),
                StructField("clientmessageid", StringType(), True),
                StructField("clienttime", StringType(), True),
                StructField("method", StringType(), True),
                StructField("path", StringType(), False),
                StructField("query", StringType(), True),
                StructField("headers", ArrayType(StringType()), True),
                StructField("action", StringType(), False),
                StructField("actiontype", StringType(), False),
                StructField("operation", StringType(), True),
                StructField("apidirection", StringType(), True),
                StructField("target_typename", StringType(), True),
                StructField("target_reference", StringType(), True),
                StructField("target_resourceid", StringType(), True),
                StructField("target_versionid", StringType(), True),
                StructField("target_display", StringType(), True),
                StructField("responsestatus", LongType(), False),
                StructField("operationoutcome", StringType(), True),
                StructField("createdby", StringType(), False)
            ]
        )

    
    def table_exists(self, table_name: str) -> bool:
        try:
            self.glueContext.create_data_frame.from_catalog(
                database=self.args["TRANS_DATALAKE"], table_name=table_name
            )
            return True
        except Exception as e:
            self.logger.warn(str(e))
            return False
        
    def write_to_s3(
        self,
        df: pyspark.sql.DataFrame,
        table_name: str,
        s3_location: str,
        partition_col: str,
    ) -> None:
        snapshot_lifetime = (
            int(self.args.get("SNAPSHOT_EXPIRY_HOURS", 168)) * 60 * 60 * 1000
        )  # to milliseconds
        full_table_name = (
            f"{self.args['CATALOG_NAME']}.{self.args['TRANS_DATALAKE']}.{table_name}"
        )
        if not self.table_exists(table_name):
            create_s3_iceberg_table(
                df=self.spark.createDataFrame([], df.schema),
                full_table_name=full_table_name,
                compaction_strategy=self.args.get("COMPACTION_STRATEGY", "copy-on-write"),
                snapshot_lifetime_ms=snapshot_lifetime,
                min_snapshots=self.args.get("MIN_SNAPSHOTS_TO_KEEP", "5"),
                s3_location=s3_location,
                partition_cols=[partition_col],
            )
        df.writeTo(full_table_name).tableProperty("format-version", "2").append()

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
    glueContext = GlueContext(sc)
    spark = glueContext.spark_session
    transformer = AuditLogTransformer(args, spark, glueContext)
    transformer.run()