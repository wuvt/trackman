#!/bin/bash

echo "\
-------------------------------------------------------------------------------
Trackman development environment
Do not use in production!
-------------------------------------------------------------------------------"

if [[ "$USE_EMBEDDED_DB" == "1" ]]; then
    export SQLALCHEMY_DATABASE_URI=sqlite:////tmp/trackman.db

    echo "Embedded database enabled."
    if [[ ! -f /tmp/trackman.db ]]; then
        echo "No database found; a new one will be created."
        su www-data -s /bin/sh -c 'flask init_embedded_db'
    fi

    echo "-------------------------------------------------------------------------------"
fi

exec $@
