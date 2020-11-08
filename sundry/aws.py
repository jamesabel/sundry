import time
import logging
import os
import pickle
from pathlib import Path
from dataclasses import dataclass
from math import isclose
import shutil

import boto3
from s3transfer import S3Transfer
from s3transfer.exceptions import S3UploadFailedError
from botocore.exceptions import ClientError, EndpointConnectionError
from boto3.exceptions import RetriesExceededError
from appdirs import user_cache_dir

from sundry import __application_name__, __author__, __title__, mkdirs, get_file_md5, get_string_sha512

log = logging.getLogger(__title__)


def _aws_get_session(profile_name: str):
    # use keys in AWS config
    # https://docs.aws.amazon.com/cli/latest/userguide/cli-config-files.html
    session = boto3.session.Session(profile_name=profile_name)
    return session


def aws_get_resource(resource_name: str, profile_name: str):
    session = _aws_get_session(profile_name)
    return session.resource(resource_name)


def aws_get_client(resource_name: str, profile_name: str):
    session = _aws_get_session(profile_name)
    return session.client(resource_name)


def aws_get_dynamodb_table_names(profile_name: str) -> list:
    """
    get all DynamoDB tables
    :param profile_name:  AWS IAM profile name
    :return: a list of DynamoDB table names
    """
    dynamodb_client = aws_get_client("dynamodb", profile_name)

    table_names = []
    more_to_evaluate = True
    last_evaluated_table_name = None
    while more_to_evaluate:
        if last_evaluated_table_name is None:
            response = dynamodb_client.list_tables()
        else:
            response = dynamodb_client.list_tables(ExclusiveStartTableName=last_evaluated_table_name)
        partial_table_names = response.get("TableNames")
        last_evaluated_table_name = response.get("LastEvaluatedTableName")
        if partial_table_names is not None and len(partial_table_names) > 0:
            table_names.extend(partial_table_names)
        if last_evaluated_table_name is None:
            more_to_evaluate = False
    table_names.sort()

    return table_names


def aws_dynamodb_scan_table(table_name: str, profile_name: str) -> (list, None):
    """
    returns entire lookup table
    :param table_name: DynamoDB table name
    :param profile_name: AWS IAM profile name
    :return: table contents
    """

    items = []
    dynamodb = aws_get_resource("dynamodb", profile_name)
    table = dynamodb.Table(table_name)

    more_to_evaluate = True
    exclusive_start_key = None
    while more_to_evaluate:
        try:
            if exclusive_start_key is None:
                response = table.scan()
            else:
                response = table.scan(ExclusiveStartKey=exclusive_start_key)
        except EndpointConnectionError as e:
            log.warning(e)
            response = None
            more_to_evaluate = False
            items = None

        if response is not None:
            items.extend(response["Items"])
            if "LastEvaluatedKey" not in response:
                more_to_evaluate = False
            else:
                exclusive_start_key = response["LastEvaluatedKey"]

    if items is not None:
        log.info(f"read {len(items)} items from {table_name}")

    return items


def _is_valid_db_pickled_file(file_path: str, cache_life: (float, int, None)):
    is_valid = os.path.exists(file_path) and os.path.getsize(file_path) > 0
    if is_valid and cache_life is not None:
        is_valid = time.time() <= os.path.getmtime(file_path) + cache_life
    return is_valid


def aws_dynamodb_scan_table_cached(table_name: str, profile_name: str, cache_dir: str = "cache", invalidate_cache: bool = False, cache_life: (float, None) = None) -> list:
    """

    Read data table(s) from AWS with caching.  This *requires* that the table not change during execution nor
    from run to run without setting invalidate_cache.

    :param table_name: DynamoDB table name
    :param profile_name: AWS IAM profile name
    :param cache_dir: cache dir
    :param invalidate_cache: True to initially invalidate the cache (forcing a table scan)
    :param cache_life: Life of cache in seconds (None=forever)
    :return: a list with the (possibly cached) table data
    """

    # todo: check the table size in AWS (since this is quick) and if it's different than what's in the cache, invalidate the cache first

    mkdirs(cache_dir)
    cache_file_path = os.path.join(cache_dir, f"{table_name}.pickle")
    log.debug(f"cache_file_path : {os.path.abspath(cache_file_path)}")
    if invalidate_cache and os.path.exists(cache_file_path):
        os.remove(cache_file_path)

    output_data = None
    if _is_valid_db_pickled_file(cache_file_path, cache_life):
        with open(cache_file_path, "rb") as f:
            log.info(f"{table_name} : reading {cache_file_path}")
            output_data = pickle.load(f)
            log.debug(f"done reading {cache_file_path}")

    if not _is_valid_db_pickled_file(cache_file_path, cache_life):
        log.info(f"getting {table_name} from DB")

        try:
            table_data = aws_dynamodb_scan_table(table_name, profile_name)
        except RetriesExceededError:
            table_data = None

        if table_data is not None and len(table_data) > 0:
            output_data = table_data
            # update data cache
            with open(cache_file_path, "wb") as f:
                pickle.dump(output_data, f)

    if output_data is None:
        log.error(f'table "{table_name}" not accessible')

    return output_data


@dataclass
class AWSS3DownloadStatus:
    success: bool = False
    cached: bool = None
    sizes_differ: bool = None
    mtimes_differ: bool = None


cache_abs_tol = 3.0  # seconds


def aws_s3_download_cached(s3_bucket: str, s3_key: str, dest_dir: (Path, None), dest_path: (Path, None), cache_dir: (Path, None), retries: int = 10, profile_name: str = None) -> AWSS3DownloadStatus:
    """
    download from AWS S3 with caching
    :param s3_bucket: S3 bucket of source
    :param s3_key: S3 key of source
    :param dest_dir: destination directory.  If given, the destination full path is the dest_dir and s3_key (in this case s3_key must not have slashes).  If dest_dir is used,
                     do not pass in dest_path.
    :param dest_path: destination full path.  If this is used, do not pass in dest_dir.
    :param cache_dir: cache dir
    :param retries: number of times to retry the AWS S3 access
    :param profile_name: AWS profile name
    :return: AWSS3DownloadStatus instance
    """
    status = AWSS3DownloadStatus()

    if (dest_dir is None and dest_path is None) or (dest_dir is not None and dest_path is not None):
        log.error(f"{dest_dir=} and {dest_path=}")
    else:

        if dest_dir is not None and dest_path is None:
            if "/" is s3_key or "\\" in s3_key:
                log.error(f"slash (/ or \\) in s3_key '{s3_key}' - can not download {s3_bucket}:{s3_key}")
            else:
                dest_path = Path(dest_dir, s3_key)

        if dest_path is not None:

            # use a hash of the S3 address so we don't have to try to store the local object (file) in a hierarchical directory tree
            cache_file_name = get_string_sha512(f"{s3_bucket}{s3_key}")

            if cache_dir is None:
                cache_dir = Path(user_cache_dir(__application_name__, __author__, "aws", "s3"))
            cache_path = Path(cache_dir, cache_file_name)
            log.debug(f"{cache_path}")

            if cache_path.exists():
                s3_size, s3_mtime, s3_hash = aws_s3_get_size_mtime_hash(s3_bucket, s3_key, profile_name)
                local_size = os.path.getsize(cache_path)
                local_mtime = os.path.getmtime(cache_path)

                if local_size != s3_size:
                    log.info(f"{s3_bucket}:{s3_key} cache miss: sizes differ {local_size=} {s3_size=}")
                    status.cached = False
                    status.sizes_differ = True
                elif not isclose(local_mtime, s3_mtime, abs_tol=cache_abs_tol):
                    log.info(f"{s3_bucket}:{s3_key} cache miss: mtimes differ {local_mtime=} {s3_mtime=}")
                    status.cached = False
                    status.mtimes_differ = True
                else:
                    status.cached = True
                    status.success = True
                    shutil.copy2(cache_path, dest_path)
            else:
                status.cached = False

            if not status.cached:
                log.info(f"S3 download : {s3_bucket=},{s3_key=},{dest_path=}")
                s3_client = aws_get_client("s3", profile_name)
                transfer = S3Transfer(s3_client)

                transfer_retry_count = 0

                while not status.success and transfer_retry_count < retries:
                    try:
                        transfer.download_file(s3_bucket, s3_key, dest_path)
                        shutil.copy2(dest_path, cache_path)
                        status.success = True
                    except ClientError as e:
                        log.warning(f"{s3_bucket}:{s3_key} to {dest_path=} : {transfer_retry_count=} : {e}")
                        transfer_retry_count += 1
                        time.sleep(3.0)

    return status


def aws_s3_read_string(s3_bucket_name: str, s3_key: str, profile_name: str) -> str:
    log.debug(f"reading {s3_bucket_name}:{s3_key} as {profile_name}")
    s3 = aws_get_resource("s3", profile_name)
    return s3.Object(s3_bucket_name, s3_key).get()["Body"].read().decode()


def aws_s3_read_lines(s3_bucket_name: str, s3_key: str, profile_name: str) -> list:
    return aws_s3_read_string(s3_bucket_name, s3_key, profile_name).splitlines()


def aws_s3_write_string(input_str: str, s3_bucket_name: str, s3_key: str, profile_name: str):
    log.debug(f"writing {s3_bucket_name}:{s3_key} as {profile_name}")
    s3 = aws_get_resource("s3", profile_name)
    s3.Object(s3_bucket_name, s3_key).put(Body=input_str)


def aws_s3_write_lines(input_lines: list, s3_bucket_name: str, s3_key: str, profile_name: str):
    aws_s3_write_string("\n".join(input_lines), s3_bucket_name, s3_key, profile_name)


def aws_s3_delete(s3_bucket_name: str, s3_key: str, profile_name: str):
    log.debug(f"deleting {s3_bucket_name}:{s3_key} as {profile_name}")
    s3 = aws_get_resource("s3", profile_name)
    s3.Object(s3_bucket_name, s3_key).delete()


def aws_s3_upload(file_path: (str, Path), s3_bucket: str, s3_key: str, profile_name: str, force=False):
    # todo: test if file already has been uploaded (using a hash)
    log.info(f"S3 upload : file_path={file_path} : bucket={s3_bucket} : key={s3_key}")

    uploaded_flag = False

    if isinstance(file_path, str):
        log.info(f"{file_path} is not Path object.  Non-Path objects will be deprecated in the future")

    if isinstance(file_path, Path):
        file_path = str(file_path)

    file_md5 = get_file_md5(file_path)
    _, _, s3_md5 = aws_s3_get_size_mtime_hash(s3_bucket, s3_key, profile_name)

    if file_md5 != s3_md5 or force:
        log.info(f"file hash of local file is {file_md5} and the S3 etag is {s3_md5} , force={force} - uploading")
        s3_client = aws_get_client("s3", profile_name)
        transfer = S3Transfer(s3_client)

        transfer_retry_count = 0
        while not uploaded_flag and transfer_retry_count < 10:
            try:
                transfer.upload_file(file_path, s3_bucket, s3_key)
                uploaded_flag = True
            except S3UploadFailedError as e:
                log.warning(f"{file_path} to {s3_bucket}:{s3_key} : {transfer_retry_count=} : {e}")
                transfer_retry_count += 1
                time.sleep(1.0)

    else:
        log.info(f"file hash of {file_md5} is the same as is already on S3 and force={force} - not uploading")

    return uploaded_flag


def aws_s3_download(file_path: (str, Path), s3_bucket: str, s3_key: str, profile_name: str) -> bool:

    if isinstance(file_path, str):
        log.info(f"{file_path} is not Path object.  Non-Path objects will be deprecated in the future")

    if isinstance(file_path, Path):
        file_path = str(file_path)

    log.info(f"S3 download : file_path={file_path} : bucket={s3_bucket} : key={s3_key}")
    s3_client = aws_get_client("s3", profile_name)
    transfer = S3Transfer(s3_client)

    transfer_retry_count = 0
    success = False
    while not success and transfer_retry_count < 10:
        try:
            transfer.download_file(s3_bucket, s3_key, file_path)
            success = True
        except ClientError as e:
            log.warning(f"{s3_bucket}:{s3_key} to {file_path} : {transfer_retry_count=} : {e}")
            transfer_retry_count += 1
            time.sleep(1.0)
    return success


def aws_s3_get_size_mtime_hash(s3_bucket: str, s3_key: str, profile_name: str):
    s3_resource = aws_get_resource("s3", profile_name)
    bucket_resource = s3_resource.Bucket(s3_bucket)

    # determine if the object exists before we try to get the info
    objs = list(bucket_resource.objects.filter(Prefix=s3_key))
    if len(objs) > 0 and objs[0].key == s3_key:
        bucket_object = bucket_resource.Object(s3_key)
        object_size = bucket_object.content_length
        object_mtime = bucket_object.last_modified
        object_hash = bucket_object.e_tag[1:-1].lower()
    else:
        object_size = None
        object_mtime = None
        object_hash = None  # does not exist
    log.debug(f"size : {object_size} ,  mtime : {object_mtime} , hash : {object_hash}")
    return object_size, object_mtime, object_hash


def aws_s3_object_exists(s3_bucket: str, s3_key: str, profile_name: str) -> bool:
    """
    determine if an s3 object exists
    :param s3_bucket: the S3 bucket
    :param s3_key: the S3 object key
    :param profile_name: AWS profile
    :return: True if object exists
    """
    s3_resource = aws_get_resource("s3", profile_name)
    bucket_resource = s3_resource.Bucket(s3_bucket)
    objs = list(bucket_resource.objects.filter(Prefix=s3_key))
    object_exists = len(objs) > 0 and objs[0].key == s3_key
    log.debug(f"{s3_bucket}:{s3_key} : object_exists={object_exists}")
    return object_exists
