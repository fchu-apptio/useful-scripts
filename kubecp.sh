#!/bin/bash

function usage() {
    echo "Usage: kubecp.sh [-n] -p [-d] -f"
    echo "Example: kubecp.sh [-n] -p studio-bff-110-r12-fchu-oom-testing-5655c74dd5-fk792 -f heap-dump-1611772461582.hprof"
    echo "Copies into current folder"
    echo
    echo " -n Namespace, defaults to flagship-ui"
    echo " -d Absolute path to directory, defaults to /apptio/service/var/"
    echo " -f Name of the file you want to copy out"
    echo " -p Name of the pod you are copying from"
}

DIR="/apptio/service/var"
NAMESPACE="flagship-ui"
PADDING=".x"

while getopts "h?n:p:d:f:" opt; do
    case ${opt} in
    h|\?)
        usage
        exit 0
        ;;
    n) 
        NAMESPACE=$OPTARG
        ;;
    f) 
        FILE=$OPTARG
        ;;
    p) 
        POD=$OPTARG
        ;;
    d)
        DIR=$OPTARG
    esac
done

# Query the folder
kubectl -n flagship-ui exec $POD -- ls $DIR

# Split the file
kubectl -n flagship-ui exec $POD -- split -b 5M $DIR/$FILE $DIR/$FILE.x

# Copy the pieces into your local directory
for alpha in $(echo {a..z}{a..z})
do 
  fileName=${FILE}${PADDING}${alpha}
  file=`kubectl -n $NAMESPACE exec $POD -- find "$DIR" -name "$fileName"`
  if [  -n "$file" ]; then
    echo "$file";
    kubectl cp -n $NAMESPACE $POD:$DIR/$fileName $fileName
    kubectl -n $NAMESPACE exec $POD -- rm $DIR/$fileName
  else
    break;
  fi
done

# Put the pieces back together
cat ${FILE}${PADDING}* > ${FILE}

# Validate checksums
sha256sum ${FILE}
kubectl -n $NAMESPACE exec $POD -- sha256sum $DIR/$FILE

# Delete the copied portions
rm -f ${FILE}${PADDING}*