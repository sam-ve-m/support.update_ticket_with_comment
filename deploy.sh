#!/bin/bash
fission spec init
fission env create --spec --name update-comment-ticket-env --image nexus.sigame.com.br/python-env-3.8:0.0.4 --builder nexus.sigame.com.br/python-builder-3.8:0.0.1
fission fn create --spec --name update-comment-fn --env update-comment-ticket-env --src "./func/*" --entrypoint main.fn
fission route create --spec --method PUT --url /update_comment --function update-comment-fn
