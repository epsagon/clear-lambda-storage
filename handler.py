from argparse import Namespace
from clear_lambda_storage import remove_old_lambda_versions


def clear_lambda_storage(event, context):
    remove_old_lambda_versions(Namespace(token_key_id=None, token_secret=None))
    return "Successful clean! 🗑 ✅"
