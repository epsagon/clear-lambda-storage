"""
Removes old versions of Lambda functions.
"""
from __future__ import print_function
import argparse
import boto3
from boto3.session import Session


LATEST = '$LATEST'


def list_available_lambda_regions():
    """
    Enumerates list of all Lambda regions
    :return: list of regions
    """
    session = Session()
    return session.get_available_regions('lambda')


def init_boto_client(client_name, region, args):
    """
    Initiates boto's client object
    :param client_name: client name
    :param region: region name
    :param args: arguments
    :return: Client
    """
    if args.token_key_id and args.token_secret:
        boto_client = boto3.client(
            client_name,
            aws_access_key_id=args.token_key_id,
            aws_secret_access_key=args.token_secret,
            region_name=region
        )
    else:
        boto_client = boto3.client(client_name, region_name=region)

    return boto_client


def lambda_function_generator(lambda_client):
    """
    Iterates over Lambda functions in a specific region
    :param lambda_client: Client
    :return: Generator
    """
    next_marker = None
    response = lambda_client.list_functions()

    while next_marker != '':
        next_marker = ''
        functions = response['Functions']
        for lambda_function in functions:
            yield lambda_function

        # Verify if there is next marker
        if 'NextMarker' in response:
            next_marker = response['NextMarker']
            response = lambda_client.list_functions(Marker=next_marker)


def lambda_version_generator(lambda_client, lambda_function):
    """
    Iterates over Lambda function versions for a specific function
    :param lambda_client: Client
    :param lambda_function: Lambda dict
    :return: Generator
    """
    next_marker = None
    response = lambda_client.list_versions_by_function(
        FunctionName=lambda_function['FunctionArn']
    )

    while next_marker != '':
        next_marker = ''
        versions = response['Versions']
        for version in versions:
            yield version

        # Verify if there is next marker
        if 'NextMarker' in response:
            next_marker = response['NextMarker']
            response = lambda_client.list_versions_by_function(
                FunctionName=lambda_function['FunctionArn'],
                Marker=next_marker
            )


def remove_old_lambda_versions(args):
    """
    Removes old versions of Lambda functions
    :param args: arguments
    :return: None
    """
    regions = list_available_lambda_regions()
    total_deleted_code_size = 0
    total_deleted_functions = {}

    for region in regions:
        print('Scanning {} region'.format(region))

        lambda_client = init_boto_client('lambda', region, args)
        function_generator = lambda_function_generator(lambda_client)

        for lambda_function in function_generator:
            for version in lambda_version_generator(
                    lambda_client,
                    lambda_function
            ):
                if version['Version'] in (lambda_function['Version'], LATEST):
                    continue

                print('Deleting {} version {}'.format(
                    version['FunctionName'],
                    version['Version'])
                )
                total_deleted_functions.setdefault(version['FunctionName'], 0)
                total_deleted_functions[version['FunctionName']] += 1
                total_deleted_code_size += (version['CodeSize'] / (1024 * 1024))

                # DELETE OPERATION!
                lambda_client.delete_function(
                    FunctionName=version['FunctionArn']
                )

    print('-' * 10)
    print('Deleted {} versions from {} functions'.format(
        sum(total_deleted_functions.values()),
        len(total_deleted_functions.keys())
    ))
    print('Freed {} MBs'.format(int(total_deleted_code_size)))


if __name__ == '__main__':
    PARSER = argparse.ArgumentParser(
        description='Removes old versions of Lambda functions.'
    )

    PARSER.add_argument(
        '--token-key-id',
        type=str,
        help=(
            'AWS access key id. Must provide AWS secret access key as well '
            '(default: from local configuration).'
        ),
        metavar='token-key-id'
    )
    PARSER.add_argument(
        '--token-secret',
        type=str,
        help=(
            'AWS secret access key. Must provide AWS access key id '
            'as well (default: from local configuration.'
        ),
        metavar='token-secret'
    )

    remove_old_lambda_versions(PARSER.parse_args())
