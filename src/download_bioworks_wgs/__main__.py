import os
from dotenv import dotenv_values
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
            #print(dir(entry))
            if os.path.exists(entry.name):
                print(f"File {entry.name} already downloaded")
                continue
            with stopwatch('download'):
                dbx.sharing_get_shared_link_file_to_file(
                    download_path="./" + entry.name,
                    url=url,
                    path="/" + entry.name
                )

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
