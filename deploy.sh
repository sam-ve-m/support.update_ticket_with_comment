#!/bin/bash
fission spec init
fission env create --spec --name update-comment-ticket-env --image nexus.sigame.com.br/python-env-3.8:0.0.5 --builder nexus.sigame.com.br/python-builder-3.8:0.0.2
fission fn create --spec --name update-comment-fn --env update-comment-ticket-env --src "./func/*" --entrypoint main.update_ticket_comments --executortype newdeploy --minscale 1 --maxscale 1
fission route create --spec --method PUT --url /update_comments --function update-comment-fn --createingress
