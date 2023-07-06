docker build -t eu.gcr.io/avian-volt-391821/annabel_trading:v1 --rm .
docker push eu.gcr.io/avian-volt-391821/annabel_trading:v1
gcrane cp -r eu.gcr.io/avian-volt-391821 europe-docker.pkg.dev/avian-volt-391821/eu.gcr.io