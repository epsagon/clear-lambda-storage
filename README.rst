Clear Lambda code storage
=====================


Motivation
----------
AWS limits the total code storage for Lambda functions to 75GB.
The main reason of reaching such size is because for every deployment of existing function, AWS stores the previous version ("qualifier").
Usually, when you reach that point, you want to remove old version.
This tool will help you to!


Setup
-----
.. code-block:: bash

    git clone https://github.com/epsagon/clear-lambda-storage
    cd clear-lambda-storage/
    pip install -r requirements.txt
    python clear_lambda_storage.py


Advanced usage
-----

Provide credentials:

.. code-block:: bash

    python list_lambdas.py --token_key_id <access_key_id> --token_secret <secret_access_key>
