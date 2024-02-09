from typing import Dict

import requests
from yaml import safe_load

BASE_URL = "https://raw.githubusercontent.com"


def fetch_from_github(
    user: str,
    repo: str,
    file: str = "CITATION.cff",
    branch: str = "main",
) -> requests.Response:
    """
    Fetches the content of a file hosted on GitHub,
    returning the request object.

    Content is fetched from user/repository/file on github.com.

    Parameters
    ----------
    user : str
        Username or organisation the repository can be found under.
    repository : str
        Name of the repository.
    file : str, default = CITATION.cff
        Path to the file from the repository root.
    branch : str, default = main
        Branch to fetch the file from.

    Returns
    -------
    requests.Response
        The response containing the file contents as text.

    Raises
    ------
    RuntimeError
        If the request returns with a bad status code,
        indicating fetch failure.
    """
    url = f"{BASE_URL}/{user}/{repo}/{branch}/{file}"

    r = requests.get(url)

    if not r.ok:
        raise RuntimeError(
            "Bad request or response, got status code "
            f"{r.status_code} when fetching from {url}"
        )

    return r


def yaml_str_to_dict(text: str) -> Dict[str, str]:
    """
    Cast a string of text in yaml syntax to a Python dictionary.
    """
    return safe_load(text)
