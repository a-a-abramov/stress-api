# Stress-API

This project aims to provide Kubernetes cluster operators with means to stress test newly built clusters with arbitrary workload. Project tries to be as simple as possible - it's basically just an API over [Stress-ng](https://github.com/ColinIanKing/stress-ng) with simple key authentication.

## Basic usage

Add helm repo:
```
    $ helm repo add a-a-abramov https://a-a-abramov.github.io/stress-api
    $ helm repo update
```

**Application needs a non empty apiSecret to work!** Please set it during installation. Here we don't create an Ingress resource for our ClusterIP service. But if your cluster already has an Ingress Controller you're free to create one - [values.yaml](charts/stress-api/values.yaml) has an example.

```
    $ helm install --namespace <ns> --set apiSecret=<apikey> <name> a-a-abramov/stress-api
```

In case your cluster doens't have any ingress yet you may just `kubectl proxy` to access Stress-API:

```
    $ kubectl proxy &
    $ export ep=http://localhost:8001/api/v1/namespaces/<ns>/services/<name>-stress-api:80/proxy/v1.0/runjob
    $ curl -s -X 'POST' $ep -H 'Accept: application/json' -H 'X-Auth-Key: <apiKey>'  -H 'Content-Type: text/plain'  --data-binary $'cpu 1\ntimeout 1s' | jq
```

This request runs 1 CPU stressor for 1 second. Successful output:
```
    {
        "info": {
            "system-info": {
            "bufferram": 42872832,
            "cpus": 4,
            "cpus-online": 4,
            "date-yyyy-mm-dd": 7279455,
            "epoch-secs": 1650058434,
            "freeram": 6009737216,
            "freeswap": 1072676864,
            "hostname": "snga-stress-api-779866b64d-6rlzk",
            "machine": "x86_64",
            "nodename": "snga-stress-api-779866b64d-6rlzk",
            "pagesize": 4096,
            "release": "5.10.104-linuxkit",
            "run-by": "uwsgi",
            "sharedram": 351858688,
            "stress-ng-version": "0.13.05",
            "sysname": "Linux",
            "ticks-per-second": 100,
            "time-hh-mm-ss": 77634,
            "totalram": 8346984448,
            "totalswap": 1073737728,
            "uptime": 2417,
            "version": "#1 SMP Wed Mar 9 19:05:23 UTC 2022"
            }
        },
        "retcode": 0
    }
```

## Stressors format
There are a couple of [examples](jobs/) in the repo, but for any advanced use you have to familiarize yourself with [stress-ng job file format](https://github.com/ColinIanKing/stress-ng/tree/master/example-jobs) from the tool's repository.

In order to run a job you should either define it inline:
```
    $ curl ... --data-binary $'cpu 1\ntimeout 1s'
```
Or specify absolute or relative path to job file:
```
    $ curl ... --data-binary '@jobs/cpu-0-15s.job'
```


## Sample linear RAM workload generator

This example will start a new [job](jobs/ram-1-24M-300s.job) that just maps 24M of memory and waits for 5 minutes (300 seconds) each 30 seconds for an hour. Simple dummy workloads like this can be used to test Horizontal Pod Autoscaler and/or Cluster Autoscaler.

```
    for i in `seq 1 120`
    do
        echo "Job $i"

        curl -X 'POST' <Cluster URI>/v1.0/runjob \
        -H "Accept: application/json" \
        -H "X-Auth-Key: <apikey>" \
        -H "Content-Type: text/plain" \
        --data-binary "@stress-api/jobs/ram-1-24M-300s.job" &

        sleep 30
    done
```
