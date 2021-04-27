"""
Removes old versions of Lambda functions.
"""
from __future__ import print_function
import argparse
import boto3
try:
    import queue
except ImportError:
    import Queue as queue
from boto3.session import Session
from botocore.exceptions import ClientError


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
    elif args.profile:
        session = boto3.session.Session(profile_name=args.profile)
        boto_client = session.client(client_name, region_name=region)
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
    try:
        response = lambda_client.list_functions()
    except Exception:
        print('Could not scan region')
        return iter([])

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
    regions = args.regions or list_available_lambda_regions()
    total_deleted_code_size = 0
    total_deleted_functions = {}
    num_to_keep = args.num_to_keep
    print('Keeping {} versions for functions'.format(num_to_keep))
    if args.function_names:
        print('Will only delete lambda versions for functions: {}'.format(" ,".join(args.function_names)))

    for region in regions:
        print('Scanning {} region'.format(region))

        lambda_client = init_boto_client('lambda', region, args)
        try:
            function_generator = lambda_function_generator(lambda_client)
        except Exception as exception:
            print('Could not scan region: {}'.format(str(exception)))
            continue

        for lambda_function in function_generator:
            # Verify if function name is provided and in case it is, skips all lambdas which name does not match
            if args.function_names and lambda_function['FunctionName'] not in args.function_names:
                continue

            versions_to_keep = queue.Queue(maxsize=num_to_keep)

            for version in lambda_version_generator(lambda_client, lambda_function):

                if version['Version'] in (lambda_function['Version'], '$LATEST'):
                    continue

                if versions_to_keep.full():
                    version_to_delete = versions_to_keep.get()
                    print('Detected {} with an old version {}'.format(
                        version_to_delete['FunctionName'],
                        version_to_delete['Version'])
                    )
                    total_deleted_functions.setdefault(version_to_delete['FunctionName'], 0)
                    total_deleted_functions[version_to_delete['FunctionName']] += 1
                    total_deleted_code_size += (version_to_delete['CodeSize'] / (1024 * 1024))

                    # DELETE OPERATION!
                    if args.dry_run:
                        print('Dry-Run: This process would delete function: {}'.format(version_to_delete["FunctionArn"]))
                    else:
                        try:
                            lambda_client.delete_function(
                                FunctionName=version_to_delete['FunctionArn']
                            )
                        except ClientError as exception:
                            print('Could not delete function: {}'.format(str(exception)))
                versions_to_keep.put(version)

    print('-' * 10)
    print('Deleted {} versions from {} functions'.format(
        sum(total_deleted_functions.values()),
        len(total_deleted_functions.keys())
    ))
    print('Freed {} MBs'.format(int(total_deleted_code_size)))


def main():
    parser = argparse.ArgumentParser(
        description='Removes old versions of Lambda functions.'
    )

    parser.add_argument(
        '--token-key-id',
        type=str,
        help=(
            'AWS access key id. Must provide AWS secret access key as well '
            '(default: from local configuration).'
        ),
        metavar='token-key-id'
    )
    parser.add_argument(
        '--token-secret',
        type=str,
        help=(
            'AWS secret access key. Must provide AWS access key id '
            'as well (default: from local configuration.'
        ),
        metavar='token-secret'
    )
    parser.add_argument(
        '--profile',
        type=str,
        help=(
            'AWS profile. Optional '
            '(default: "default" from local configuration).'
        ),
        metavar='profile'
    )

    parser.add_argument(
        '--regions',
        nargs='+',
        help='AWS region to look for old Lambda versions',
        metavar='regions'
    )

    parser.add_argument(
        '--num-to-keep',
        type=int,
        default=2,
        help=(
            'Number of latest versions to keep. Older versions will be deleted. Optional '
            '(default: 2).'
        ),
        metavar='num-to-keep'
    )

    parser.add_argument(
        '--function-names',
        nargs='+',
        help=(
            'Clear the storage of a single application. Optional '
            '(default: None).'
        ),
        metavar='function-names'
    )

    parser.add_argument(
        '--dry-run',
        type=bool,
        default=False,
        help=(
            'Run the function without deleting anything. Optional '
            '(default: False).'
        ),
        metavar='dry-run'
    )
    remove_old_lambda_versions(parser.parse_args())


if __name__ == '__main__':
    main()
