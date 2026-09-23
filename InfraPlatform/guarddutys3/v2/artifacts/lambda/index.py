import json
import boto3
import logging
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)
s3 = boto3.client('s3')

def parse_prefix_mapping(prefix_config):
    """
    Parse prefix mapping configuration.
    Format: 'source-prefix>dest-prefix,source-prefix>dest-prefix'
    Example: 'uploads/>scanned/,documents/>verified/,*>other/'
    Returns a list of tuples: [(source, dest), ...] with default ('*', dest) last
    """
    if not prefix_config or prefix_config.strip() == '':
        return []
    
    # Check if it's a simple prefix (no '>' character)
    if '>' not in prefix_config:
        # Simple prefix - applies to all files
        return [('*', prefix_config)]
    
    mappings = []
    default_mapping = None
    
    for mapping in prefix_config.split(','):
        mapping = mapping.strip()
        if '>' in mapping:
            source, dest = mapping.split('>', 1)
            source = source.strip()
            dest = dest.strip()
            
            if source == '*':
                default_mapping = ('*', dest)
            else:
                mappings.append((source, dest))
    
    # Add default mapping at the end
    if default_mapping:
        mappings.append(default_mapping)
    
    return mappings

def get_destination_key(object_key, prefix_mappings):
    """
    Determine destination key based on prefix mappings.
    Returns the object key with appropriate prefix applied.
    """
    if not prefix_mappings:
        return object_key
    
    # Try to match specific prefixes first
    for source_prefix, dest_prefix in prefix_mappings:
        if source_prefix == '*':
            # Default case - apply prefix
            return f"{dest_prefix}{object_key}" if dest_prefix else object_key
        elif object_key.startswith(source_prefix):
            # Matched specific prefix - apply destination prefix
            return f"{dest_prefix}{object_key}" if dest_prefix else object_key
    
    # No match found - return original key
    return object_key

def lambda_handler(event, context):
    logger.info("Received event:")
    logger.info(json.dumps(event, indent=2))

    try:
        detail = event.get('detail', {})
        s3_object = detail.get('s3ObjectDetails', {})

        if not s3_object or 'objectKey' not in s3_object or 'bucketName' not in s3_object:
            logger.error("Missing required objectKey or bucketName in event details.")
            return

        source_bucket = s3_object['bucketName']
        object_key = s3_object['objectKey']
        destination_bucket = os.environ['DEST_BUCKET']
        destination_prefix_config = os.environ.get('DEST_BUCKET_PREFIX', '')
        destination_prefix_config_2 = os.environ.get('DEST_BUCKET_PREFIX_2', '')
        quarantine_bucket = os.environ.get('QUARANTINE_BUCKET', '')
        quarantine_prefix_config = os.environ.get('QUARANTINE_BUCKET_PREFIX', '')
        quarantine_prefix_config_2 = os.environ.get('QUARANTINE_BUCKET_PREFIX_2', '')
        scan_result = detail.get('scanResultDetails', {}).get('scanResultStatus', 'UNKNOWN')
        
        # Parse prefix mappings
        dest_prefix_mappings = parse_prefix_mapping(destination_prefix_config)
        dest_prefix_mappings_2 = parse_prefix_mapping(destination_prefix_config_2)
        quarantine_prefix_mappings = parse_prefix_mapping(quarantine_prefix_config)
        quarantine_prefix_mappings_2 = parse_prefix_mapping(quarantine_prefix_config_2)

        logger.info(f"Processing file: {object_key} from {source_bucket} with scan result: {scan_result}")

        if scan_result == "NO_THREATS_FOUND":
            try:
                destination_key = get_destination_key(object_key, dest_prefix_mappings)
                s3.copy_object(
                    CopySource={'Bucket': source_bucket, 'Key': object_key},
                    Bucket=destination_bucket,
                    Key=destination_key
                )
                logger.info(f"Successfully copied {object_key} to {destination_bucket}/{destination_key}")
                
                # Copy to secondary prefix if configured
                if dest_prefix_mappings_2:
                    destination_key_2 = get_destination_key(object_key, dest_prefix_mappings_2)
                    s3.copy_object(
                        CopySource={'Bucket': source_bucket, 'Key': object_key},
                        Bucket=destination_bucket,
                        Key=destination_key_2
                    )
                    logger.info(f"Successfully copied {object_key} to secondary prefix {destination_bucket}/{destination_key_2}")
            except Exception as copy_error:
                logger.error(f"Error copying {object_key} to {destination_bucket}: {str(copy_error)}")
                return

        elif scan_result == "THREATS_FOUND" and quarantine_bucket:
            try:
                quarantine_key = get_destination_key(object_key, quarantine_prefix_mappings)
                s3.copy_object(
                    CopySource={'Bucket': source_bucket, 'Key': object_key},
                    Bucket=quarantine_bucket,
                    Key=quarantine_key
                )
                s3.put_object_tagging(
                    Bucket=quarantine_bucket,
                    Key=quarantine_key,
                    Tagging={
                        'TagSet': [
                            {'Key': 'QuarantineReason', 'Value': 'THREATS_FOUND'},
                            {'Key': 'SourceBucket', 'Value': source_bucket}
                        ]
                    }
                )
                logger.info(f"Quarantined {object_key} to {quarantine_bucket}/{quarantine_key}")
                
                # Copy to secondary quarantine prefix if configured
                if quarantine_prefix_mappings_2:
                    quarantine_key_2 = get_destination_key(object_key, quarantine_prefix_mappings_2)
                    s3.copy_object(
                        CopySource={'Bucket': source_bucket, 'Key': object_key},
                        Bucket=quarantine_bucket,
                        Key=quarantine_key_2
                    )
                    s3.put_object_tagging(
                        Bucket=quarantine_bucket,
                        Key=quarantine_key_2,
                        Tagging={
                            'TagSet': [
                                {'Key': 'QuarantineReason', 'Value': 'THREATS_FOUND'},
                                {'Key': 'SourceBucket', 'Value': source_bucket}
                            ]
                        }
                    )
                    logger.info(f"Quarantined {object_key} to secondary prefix {quarantine_bucket}/{quarantine_key_2}")
            except Exception as quarantine_error:
                logger.error(f"Error quarantining {object_key} to {quarantine_bucket}: {str(quarantine_error)}")
                return

        elif scan_result == "THREATS_FOUND":
            logger.warning(f"Threats found in {object_key} - no quarantine bucket configured, deleting from source")

        else:
            logger.info(f"Scan result {scan_result} for {object_key} - deleting from source")

        try:
            s3.delete_object(Bucket=source_bucket, Key=object_key)
            logger.info(f"Deleted {object_key} from {source_bucket}")
        except Exception as delete_error:
            logger.error(f"Error deleting {object_key} from {source_bucket}: {str(delete_error)}")

    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
