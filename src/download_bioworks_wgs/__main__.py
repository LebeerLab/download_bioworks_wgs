import os
import argparse
from dotenv import dotenv_values, set_key
from tqdm import tqdm
import dropbox
from dropbox import DropboxOAuth2FlowNoRedirect
from http.client import RemoteDisconnected

def oath_flow(config_f):
    config = dotenv_values(config_f)
    key, secret = (config.get("DROPBOX_KEY"), config.get("DROPBOX_SECRET"))
    if not key:
        raise ValueError(f"Please set DROPBOX_KEY and DROPBOX_SECRET in {config_f}")
    auth_flow = DropboxOAuth2FlowNoRedirect(
      key, 
      consumer_secret=secret, 
      token_access_type="offline", 
      use_pkce=True
    )

    authorize_url = auth_flow.start()
    print("1. Go to: " + authorize_url)
    print("2. Click \"Allow\" (you might have to log in first).")
    print("3. Copy the authorization code.")
    auth_code = input("Enter the authorization code here: ").strip()

    try:
        oauth_result = auth_flow.finish(auth_code)
    except Exception as e:
        print('Error: %s' % (e,))
        exit(1)

    set_key(config_f, "DROPBOX_REFRESH_TOKEN", oauth_result.refresh_token)

    return oauth_result.refresh_token


def download_reads_from_dropbox(url, config_f):


    config = dotenv_values(config_f)
    refresh_token, key = (config.get("DROPBOX_REFRESH_TOKEN"), config.get("DROPBOX_KEY"))
    if not refresh_token:
        refresh_token = oath_flow(config_f)

    with dropbox.Dropbox(oauth2_refresh_token = refresh_token, app_key=key) as dbx:

        shared_link = dropbox.files.SharedLink(url=url)

        result = dbx.files_list_folder(
            path="",
            shared_link=shared_link
        )

        entries = result.entries

        while result.has_more:	
            result = dbx.files_list_folder_continue(result.cursor)
            entries.extend(result.entries)

        for entry in [e for e in entries if ".gz" in e.name]:
            #print(entry.name)
            if os.path.exists(entry.name):
                print(f"File {entry.name} already downloaded")
                continue
            metadata, response = dbx.sharing_get_shared_link_file(
                    url=url,
                    path="/" + entry.name
            )
            total = int(response.headers.get("Content-Length", 0))
            with open(entry.name, "wb") as f:
                with tqdm(total=total, unit="B", unit_scale=True, desc=entry.name) as pbar:
                    for chunk in response.iter_content(chunk_size=1024 * 1024):
                        if chunk:
                            f.write(chunk)
                            pbar.update(len(chunk))
            response.close()


def main(url=None):

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "url",
        nargs="?",
        type=str,
        default=None,
        help="Optional url"
    )

    parser.add_argument(
        "-d","--debug", action="store_true"
    )
    parser.add_argument(
        "-c", "--config", default="/home/tim/.dropbox"
    )

    args = parser.parse_args()

    if not url:
        url = args.url

    if not url:
        url = input("Url to reads: ")
    tries = 1
    while True:
        try:
            download_reads_from_dropbox(url, args.config)
        except Exception as e:
            print(f"Failure {n}: {e}")
        return None
    


if __name__ == "__main__":
    main()
