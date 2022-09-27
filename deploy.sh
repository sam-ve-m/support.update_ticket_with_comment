#!/bin/bash
fission spec init
fission env create --spec --name update-ticket-env --image nexus.sigame.com.br/python-env-3.8:0.0.5 --builder nexus.sigame.com.br/fission-builder-3.8:0.0.1
fission fn create --spec --name update-ticket-fn --env update-ticket-env --src "./func/*" --entrypoint main.update_ticket_comments --executortype newdeploy --maxscale 1
fission route create --spec --name update-ticket-rt --method PUT --url /support/update-ticket --function update-ticket-fn
