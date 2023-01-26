fission spec init
fission env create --spec --name sup-tckt-comment-env --image nexus.sigame.com.br/fission-support-ticket-add-comment:0.1.0-0 --poolsize 2 --graceperiod 3 --version 3 --imagepullsecret "nexus-v3" --spec
fission fn create --spec --name sup-tckt-comment-fn --env sup-tckt-comment-env --code fission.py --executortype poolmgr --requestsperpod 10000 --spec
fission route create --spec --name sup-tckt-comment-rt --method PUT --url /support/update-ticket --function sup-tckt-comment-fn