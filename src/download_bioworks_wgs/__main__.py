import os
import argparse
from dotenv import dotenv_values
from tqdm import tqdm
import dropbox
from dropbox import DropboxOAuth2FlowNoRedirect

def oath_flow(config_f="/home/tim/.dropbox"):
    config = dotenv_values(config_f)
    try:
        key, secret = (config["DROPBOX_KEY"], config["DROPBOX_SECRET"])
    except(KeyError):
        raise ValueError(f"Please set DROPBOX_KEY and DROPBOX_SECRET in {config_f}")
    auth_flow = DropboxOAuth2FlowNoRedirect(key, secret)

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
    return oauth_result.access_token


def download_reads_from_dropbox(url):

    access_token = oath_flow()

    with dropbox.Dropbox(oauth2_access_token = access_token) as dbx:

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
            print(entry.name)
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
    args = parser.parse_args()

    if not url:
        url = args.url

    if not url:
        url = input("Url to reads: ")
    
    download_reads_from_dropbox(url)


if __name__ == "__main__":
    main()
