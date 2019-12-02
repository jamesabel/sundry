import time
import logging
import os
import pickle

import boto3
from boto3.exceptions import RetriesExceededError
from botocore.exceptions import EndpointConnectionError

from sundry import __title__, mkdirs

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


# todo: remove this after a while
def aws_scan_table(table_name: str, profile_name: str) -> (list, None):
    log.warning("aws_scan_table deprecated - use aws_dynamodb_scan_table")
    return aws_dynamodb_scan_table(table_name, profile_name)


# todo: remove this after a while
def aws_scan_table_cached(table_name: str, profile_name: str, cache_dir: str = "cache", invalidate_cache: bool = False, cache_life: (float, None) = None) -> list:
    log.warning("aws_scan_table_cached deprecated - use aws_dynamodb_scan_table_cached")
    return aws_dynamodb_scan_table_cached(table_name, profile_name, cache_dir, invalidate_cache, cache_life)


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
