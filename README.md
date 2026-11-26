# Installation

`pip install git+https://github.com/LebeerLab/download_bioworks_wgs`

## Dependencies

You'll need the dropbox python package and set up a Dropbox API app (with key and secret) in a config file. An example can be found in `.dropbox.example`

# Usage

`download_bioworks_wgs -c <config_file>` will prompt you to paste a url to the sample page in the dropbox; responds with a link that you need to follow to authorize access.
