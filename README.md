
# Router
Router functions in `router/README.md`

# Troubleshoot
```
./troubleshoot.sh -v
```

# Kill Forticlient
```
./killfort.sh
```

# Copy file form kubernetes
Used to copy files from kubernetes pods. This is needed because of 
https://github.com/kubernetes/kubernetes/issues/60140. It is a temporary solution, the long term solution should be to send the file to S3.
```
# See options
kubecp.sh -h

# Example. Gets heap dump file from flagship-ui pod service/var file
kubecp.sh -p studio-bff-110-r12-fchu-oom-testing-5655c74dd5-fk792 -f heap-dump-1611772461582.hprof
```