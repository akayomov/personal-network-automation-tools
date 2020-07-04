#!/opt/bin/sh

counter=0
while [ $counter -lt 60 ]; do
    sleep 5 && echo "$0 $1 ($counter)..."
    counter=$((counter+1))
done
sleep 5 && echo "$1 (Last keep message)..."
