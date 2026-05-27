command = 'docker run'

docker run --name pyt -it -v $PWD/distr:/tmp/distr python:3.11.15 pip install onec_dtools && python3