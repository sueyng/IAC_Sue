"""
Audit Log Transformation Module

This module contains the core transformation logic for audit log data,
separated from Glue-specific code to enable unit testing.
"""

import pyspark
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import col, when, array, size, lit, to_timestamp
from pyspark.sql.types import (
    ArrayType,
    LongType,
    StringType,
    StructField,
    StructType,
    TimestampType,
)


def get_target_schema() -> StructType:
    """
    Returns the target schema for the transformed audit log data.

    Returns
    -------
    StructType
        The target schema definition
    """
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
            StructField("createdby", StringType(), False),
        ]
    )


def normalize_column_names(df: DataFrame) -> DataFrame:
    """
    Converts all column names to lowercase.

    Parameters
    ----------
    df : DataFrame
        Input DataFrame with potentially mixed-case column names

    Returns
    -------
    DataFrame
        DataFrame with all lowercase column names
    """
    for col_name in df.columns:
        df = df.withColumnRenamed(col_name, col_name.lower())
    return df


def handle_headers_column(df: DataFrame) -> DataFrame:
    """
    Handles the headers column transformation.
    - If headers column doesn't exist, creates it with empty array default
    - If headers is null or empty, replaces with array containing empty string

    Parameters
    ----------
    df : DataFrame
        Input DataFrame

    Returns
    -------
    DataFrame
        DataFrame with properly handled headers column
    """
    default_headers = array(lit(""))

    if "headers" not in df.columns:
        # Column doesn't exist, create with default empty array
        df = df.withColumn("headers", default_headers)
    else:
        # Column exists, handle null/empty cases
        df = df.withColumn(
            "headers",
            when(
                col("headers").isNull() | (size(col("headers")) == 0),
                default_headers
            ).otherwise(col("headers"))
        )
    return df


def add_timestamp_columns(df: DataFrame) -> DataFrame:
    """
    Adds UTC timestamp columns derived from startdatetime and enddatetime.

    Parameters
    ----------
    df : DataFrame
        Input DataFrame with startdatetime and enddatetime columns

    Returns
    -------
    DataFrame
        DataFrame with added startdatetime_utc and enddatetime_utc columns
    """
    if "startdatetime" in df.columns:
        df = df.withColumn("startdatetime_utc", to_timestamp("startdatetime"))
    else:
        df = df.withColumn("startdatetime_utc", lit(None).cast(TimestampType()))

    if "enddatetime" in df.columns:
        df = df.withColumn("enddatetime_utc", to_timestamp("enddatetime"))
    else:
        df = df.withColumn("enddatetime_utc", lit(None).cast(TimestampType()))

    return df


def ensure_schema_columns(df: DataFrame, schema: StructType) -> DataFrame:
    """
    Ensures all columns defined in the schema exist in the DataFrame.
    Missing columns are added with null values of the appropriate type.

    Parameters
    ----------
    df : DataFrame
        Input DataFrame
    schema : StructType
        Target schema

    Returns
    -------
    DataFrame
        DataFrame with all schema columns present
    """
    current_cols = df.columns
    for field in schema.fields:
        if field.name not in current_cols:
            df = df.withColumn(field.name, lit(None).cast(field.dataType))
    return df


def drop_extra_columns(df: DataFrame, schema: StructType) -> DataFrame:
    """
    Drops columns that are not in the target schema.

    Parameters
    ----------
    df : DataFrame
        Input DataFrame
    schema : StructType
        Target schema

    Returns
    -------
    DataFrame
        DataFrame with only schema columns
    """
    expected_cols = schema.fieldNames()
    columns_to_drop = [col_name for col_name in df.columns if col_name not in expected_cols]
    return df.drop(*columns_to_drop)


def select_ordered_columns(df: DataFrame, schema: StructType) -> DataFrame:
    """
    Selects columns in the order defined by the schema.

    Parameters
    ----------
    df : DataFrame
        Input DataFrame
    schema : StructType
        Target schema

    Returns
    -------
    DataFrame
        DataFrame with columns in schema order
    """
    return df.select(schema.fieldNames())


def transform_audit_log(df: DataFrame, schema: StructType = None) -> DataFrame:
    """
    Main transformation function that applies all transformations to audit log data.

    This function:
    1. Normalizes column names to lowercase
    2. Handles headers column (null/empty/missing)
    3. Adds UTC timestamp columns
    4. Ensures all schema columns exist
    5. Drops extra columns not in schema
    6. Orders columns according to schema

    Parameters
    ----------
    df : DataFrame
        Raw input DataFrame from landing zone
    schema : StructType, optional
        Target schema. If not provided, uses default schema.

    Returns
    -------
    DataFrame
        Transformed DataFrame ready for the transform zone
    """
    if schema is None:
        schema = get_target_schema()

    # Return empty DataFrame if input is empty
    if df.count() == 0:
        return df

    # Step 1: Normalize column names to lowercase
    df = normalize_column_names(df)

    # Step 2: Handle headers column
    df = handle_headers_column(df)

    # Step 3: Add timestamp columns
    df = add_timestamp_columns(df)

    # Step 4: Ensure all schema columns exist
    df = ensure_schema_columns(df, schema)

    # Step 5: Drop extra columns
    df = drop_extra_columns(df, schema)

    # Step 6: Select columns in schema order
    df = select_ordered_columns(df, schema)

    return df
