"""POST recipes_partial.ttl into the Fuseki `recipes` dataset.

Fuseki accepts a Turtle payload at the `/<dataset>/data` endpoint when the
request body is the TTL bytes and `Content-Type: text/turtle` is set.
"""

import sys

import requests

FUSEKI_DATA_URL = "http://localhost:3030/recipes/data"
TTL_FILE = "recipes_partial.ttl"


def main():
    """POST TTL_FILE to FUSEKI_DATA_URL.

    Reads the TTL file as bytes, POSTs it with Content-Type text/turtle,
    and raises a non-zero exit on any non-2xx response.
    """
    # TODO: open TTL_FILE in binary mode and POST its bytes to FUSEKI_DATA_URL
    # TODO: include the header Content-Type: text/turtle; raise on non-2xx
    raise NotImplementedError("Complete the POST in load_dataset.main")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"load_dataset failed: {exc}", file=sys.stderr)
        sys.exit(1)
