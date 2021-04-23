#!/bin/bash

if test -f ".env"; then
    echo "Loading .env"
    export $(cat .env)
fi

if [ -z "$PROJECT" ]; then
  PROJECT="$1"
  if [ -z "$PROJECT" ]; then
    echo "You must specify GCP project name as argument or in environment"
    exit 1
  fi
fi

docker build -t rsibot:local .

docker tag rsibot:local gcr.io/${PROJECT}/rsibot

docker push gcr.io/${PROJECT}/rsibot