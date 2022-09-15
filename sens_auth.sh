#!/bin/bash

auth=$(curl -X POST "https://api.sensorpush.com/api/v1/oauth/authorize" \
-H "accept: application/json" \
-H "Content-Type:application/json" \
-d @- <<BODY
{
   "email": "ops@altius.org",
   "password": "67#QppWF2V"
}
BODY)

echo "$auth" > step1_auth_raw.txt

python3 step1_auth.py

auth1=$(<step1_trimmed_auth.txt)

#echo $auth1

access=$(curl -X POST "https://api.sensorpush.com/api/v1/oauth/accesstoken" \
-H "accept: application/json" \
-H "Content-Type: application/json" \
-d @- <<BODY
{
   "authorization": $auth1
}
BODY)

echo "$access" > step2_auth_raw.txt

python3 step2_auth.py

auth2=$(<step2_trimmed_auth.txt)

curl -X POST "https://api.sensorpush.com/api/v1/devices/sensors" \
-H "accept: application/json" \
-H "Authorization: $auth2" \
-d @- <<BODY
{
   "authorization": $auth2
}
BODY















