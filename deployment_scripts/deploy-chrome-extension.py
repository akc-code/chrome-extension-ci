import requests
import sys
from typing import Any


def report_failure_and_exit(msg: str, response_object: requests.Response) -> None:
    print(msg)
    print(f"The request returned a {response_object.status_code} status.")
    print(f'Reason: {response_object.reason}')
    response_object.raise_for_status()
    sys.exit(-1)


def get_access_token(client_id: str, client_secret: str, refresh_token: str) -> str:
    url = 'https://accounts.google.com/o/oauth2/token'
    payload = {
        'client_id': client_id,
        'client_secret': client_secret,
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token',
        'redirect_uri': 'urn:ietf:wg:oauth:2.0:oob'
    }
    access_token_response = requests.post(url, data=payload)
    if 200 <= access_token_response.status_code < 300:
        print("Retrieved access token successfully.")
        return access_token_response.json().get('access_token')
    else:
        report_failure_and_exit("Request to access token wasn't successful!", access_token_response)


def upload_zip_file_to_chrome_webstore(access_token: str, app_id: str, zip_file_path: str, zip_file_name: str) -> Any:
    fileobj = open(zip_file_path, 'rb')

    url = f'https://www.googleapis.com/upload/chromewebstore/v1.1/items/{app_id}'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'x-goog-api-version': '2'
    }
    upload_response = requests.put(url, headers=headers, files={"archive": (zip_file_name, fileobj, 'application/zip')})
    if 200 <= upload_response.status_code < 300:
        print("Uploaded zip file successfully.")
        return upload_response.json().get('status_code')
    else:
        report_failure_and_exit("Request to upload zip file wasn't successful!", upload_response)


def publish_chrome_app(access_token: str, app_id: str):
    url = f'https://www.googleapis.com/chromewebstore/v1.1/items/{app_id}/publish'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'x-goog-api-version': '2'
    }
    publish_response = requests.post(url, headers=headers)
    if 200 <= publish_response.status_code < 300:
        print(f"Published the app - {app_id} successfully.")
        return publish_response.json().get('status_code')
    else:
        report_failure_and_exit(f"Request to publish the app - {app_id} wasn't successful!", publish_response)


def get_app_published_version(access_token: str, app_id: str):
    url = f'https://www.googleapis.com/chromewebstore/v1.1/items/{app_id}?projection=DRAFT'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'x-goog-api-version': '2'
    }
    published_version_response = requests.get(url, headers=headers)

    # TODO: Remove this line before deployment
    print(f'Published version={published_version_response.json().get("crxVersion")}')

    return published_version_response.json().get('crxVersion')


def is_app_updated(access_token: str, app_id: str, current_version: str) -> bool:
    return get_app_published_version(access_token, app_id) != current_version


def get_release_info():

    # TODO: Send this message to extension-update channel on Slack!
    from datetime import datetime
    day = datetime.today().strftime('%A')
    version = '2.17.1'
    message = f"""
    I am a bot and I am trying to impersonate Logan!

    Happy {day} Everyone!
    We released a Dev Build ({version}) today with the changes below.

    """
    print(message)


def post_release_message_to_slack(channel: str, message: str):
    pass


if __name__ == '__main__':
    import sys
    _, client_id, client_secret, refresh_token, app_id, current_app_version, zip_file_path = sys.argv
    
    access_token = get_access_token(client_id, client_secret, refresh_token)
    
    # # TODO: Remove this line before deployment
    # print(f'{access_token=}')

    # # TODO: Remove this line before deployment
    # print(f'{current_app_version=}')

    zip_file_name = ''.join(current_app_version.split('.')) + '-chrome.zip'
    # # TODO: Remove this line before deployment
    # print(f'{zip_file_name=}')

    if not is_app_updated(access_token, app_id, current_app_version):
        print("The app version is the same as the one in the webstore. Cancelling update. Bump up the app version to deploy.")
        exit(0)

    zip_file_name = ''.join(current_app_version.split('.')) + '-chrome.zip'
    
    upload_zip_file_to_chrome_webstore(access_token, app_id, zip_file_path, zip_file_name)
    publish_chrome_app(access_token, app_id)
