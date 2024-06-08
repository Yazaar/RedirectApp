#!/bin/sh

export WEB_PORT="80"
export SECRET="very_secret"
export POSTGRES_CONNECTION_STRING="postgresql://usr:pass@localhost:5432/database"

/path/to/python /path/to/main.py