"""POST recipes_partial.ttl into the Fuseki `recipes` dataset.

Fuseki accepts a Turtle payload at the `/<dataset>/data` endpoint when the
request body is the TTL bytes and `Content-Type: text/turtle` is set.

Auth: docker-compose.yml starts Fuseki with `ADMIN_PASSWORD: admin`, which
locks write endpoints (including POST `/recipes/data`) behind HTTP Basic
Auth. The defaults below match the docker-compose credentials; override
via FUSEKI_USER / FUSEKI_PASSWORD env vars if you change the compose file.
"""

import os
import sys

import requests

FUSEKI_DATA_URL = "http://localhost:3030/recipes/data"
TTL_FILE = "recipes_partial.ttl"
FUSEKI_USER = os.getenv("FUSEKI_USER", "admin")
FUSEKI_PASSWORD = os.getenv("FUSEKI_PASSWORD", "admin")


def main():
    """POST TTL_FILE to FUSEKI_DATA_URL.

    Reads the TTL file as bytes, POSTs it with Content-Type text/turtle and
    HTTP Basic Auth (FUSEKI_USER, FUSEKI_PASSWORD), and raises a non-zero
    exit on any non-2xx response.
    """
    # TODO: open TTL_FILE in binary mode and POST its bytes to FUSEKI_DATA_URL
    # TODO: include the header Content-Type: text/turtle
    # TODO: include HTTP Basic Auth — auth=(FUSEKI_USER, FUSEKI_PASSWORD)
    # TODO: raise on non-2xx (response.raise_for_status())
    raise NotImplementedError("Complete the POST in load_dataset.main")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"load_dataset failed: {exc}", file=sys.stderr)
        sys.exit(1)
