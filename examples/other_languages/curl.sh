#!/bin/sh
# Terminal 1:  jeeg --serve-api        (prints a token; also saved in ~/.jeeg/api_token)
# Terminal 2:  sh curl.sh
TOKEN=$(jeeg --api-token)
curl -s -H "Authorization: Bearer $TOKEN" -d '{"query":"gst 2500 18"}' http://127.0.0.1:8766/v1/run
echo
curl -s -H "Authorization: Bearer $TOKEN" "http://127.0.0.1:8766/v1/find?q=open%20youtube&limit=2"
echo
