RETAIN_EXT_CLIENT_ID=${{ secrets.RETAIN_EXT_CLIENT_ID }}
RETAIN_EXT_CLIENT_SECRET=${{ secrets.RETAIN_EXT_CLIENT_SECRET }}
RETAIN_EXT_REFRESH_TOKEN=${{ secrets.RETAIN_EXT_REFRESH_TOKEN }}
APP_ID=afblekficpcnoabgcdekljjfeekgjddp

ACCESS_TOKEN=$(curl "https://accounts.google.com/o/oauth2/token" -d "client_id=${RETAIN_EXT_CLIENT_ID}&client_secret=${RETAIN_EXT_CLIENT_SECRET}&refresh_token=${RETAIN_EXT_REFRESH_TOKEN}&grant_type=refresh_token&redirect_uri=urn:ietf:wg:oauth:2.0:oob" | jq -r .access_token)

curl -H "Authorization: Bearer ${ACCESS_TOKEN}" -H "x-goog-api-version: 2" -X PUT -T pointless.zip -v "https://www.googleapis.com/upload/chromewebstore/v1.1/items/${APP_ID}"

curl -H "Authorization: Bearer ${ACCESS_TOKEN}" -H "x-goog-api-version: 2" -H "Content-Length: 0" -X POST -v "https://www.googleapis.com/chromewebstore/v1.1/items/${APP_ID}/publish"
