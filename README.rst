Clear Lambda code storage
===========================


Motivation
-----------
AWS limits the total code storage for Lambda functions to `75GB <https://docs.aws.amazon.com/lambda/latest/dg/limits.html#limits-list>`_.

The main reason of reaching such size is because for every deployment of existing function, AWS stores the previous version ("qualifier").

Usually, when you reach that point, you want to remove old version.
This tool will help you to!


Setup
-----
Install via pip

.. code-block:: bash

    pip install clear-lambda-storage
    clear_lambda_storage

Install via source

.. code-block:: bash

    git clone https://github.com/epsagon/clear-lambda-storage
    cd clear-lambda-storage/
    pip install -r requirements.txt
    python clear_lambda_storage.py


Advanced usage
---------------

Provide credentials:

.. code-block:: bash

    python clear_lambda_storage.py --token-key-id <access_key_id> --token-secret <secret_access_key>

Alternate usage:
.. code-block:: bash

    python clear_lambda_storage.py --profile-id <profile_id> --num-to-keep 2

⚡️ `Serverless Framework <https://serverless.com>`_ usage
----------------------------------------------------------
.. code-block:: bash

    npm i -g serverless
    git clone https://github.com/epsagon/clear-lambda-storage
    cd clear-lambda-storage/
    serverless deploy

You can schedule this Lambda code storage clean to run every period you want:

.. code-block:: yaml

    functions:
      clear_lambda_storage:
        handler: handler.clear_lambda_storage
        memorySize: 128
        timeout: 120
        events:
          - schedule: cron(0 12 ? * SUN *) # Run every sunday at 12:00pm UTC
