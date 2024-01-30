import inspect
import sys
from dataclasses import dataclass
from typing import Any, Dict, List, Set

import requests

from brainglobe_utils.citation.fetch import fetch_from_github, yaml_str_to_dict


@dataclass
class Repository:
    """
    Static class for representing GitHub repositories, in particular
    when needing to fetch CITATION information from them.

    Parameters
    ----------
    See attributes.

    Attributes
    ----------
    name : str
        The name of the repository.
    tool_aliases: List[str]
        Names by which the tool the repository provides might be called.
    cff_branch: str, default = "main"
        Branch on which the citation file can be found.
    cff_loc: str, default = "CITATION.cff"
        Location of the citation file on the appropriate branch.
    org: str, default = "brainglobe"
        Organisation or user to which the repository belongs.
    """

    name: str
    tool_aliases: List[str]
    cff_branch: str = "main"
    cff_loc: str = "CITATION.cff"
    org: str = "brainglobe"

    @property
    def url(self) -> str:
        """
        URL to the repository as hosted on GitHub.
        """
        return f"https://github.com/{self.org}/{self.name}"

    def __contains__(self, alias: str) -> bool:
        """
        Syntactic sugar to allow the use of
        if alias in Repository,
        when asking if a Repository is known by the given alias.

        Comparison is case-insensitive for added protection.
        """
        return alias.lower() in [name.lower() for name in self.tool_aliases]

    def __eq__(self, other: "Repository") -> bool:
        """
        Repositories are identical if they point to the same repository.
        """
        return self.url == other.url

    def __hash__(self) -> int:
        """
        Repositories are hashable by their GitHub url.
        """
        return hash(self.url)

    def __lt__(self, other: "Repository") -> bool:
        """
        Repositories are compared by name, alphabetically.
        """
        return self.name < other.name

    def __post_init__(self) -> None:
        """
        Validate the repository actually exists and is reachable,
        before attempting to fetch content later.

        Also ensure that a tool can be referred to by its repository
        name.
        """
        ping_site = requests.get(self.url)
        if not ping_site.ok:
            if ping_site.status_code == 404:
                # Site not found, so repository does not exist
                raise ValueError(
                    f"Repository {self.org}/{self.name} does not exist"
                    " (got 404 response)"
                )
            else:
                raise ValueError(
                    f"Could not reach {self.url} successfully (non 404 status)"
                )

        # Can always refer to yourself by repository name
        if self.name not in self.tool_aliases:
            self.tool_aliases.append(self.name)
        return

    def __str__(self) -> str:
        """
        Repositories are represented by their GitHub url.
        """
        return self.url

    def read_citation_info(self) -> Dict[str, Any]:
        """
        Read citation information from the repository into a dictionary.
        """
        cff_response = fetch_from_github(
            self.org, self.name, self.cff_loc, self.cff_branch
        )

        return yaml_str_to_dict(cff_response.text)


def unique_repositories_from_tools(
    *tools: str, report_duplicates: bool = False
) -> Set[Repository]:
    """
    Given a list of tool aliases, return a set of the unique repositories
    that they correspond to.

    Repositories that are referred to by more than one tool in the list
    provided can be reported by flagging the appropriate input.
    These duplicates are then removed from the output.

    Parameters
    ----------
    tools: str
        Tool names or aliases whose repositories should be looked up and
        filtered for duplicates.
    report_duplicates: bool, default = False
        If True, a printout will be sent to the console when a repository
        is referenced more than once in the tool list.

    Returns
    -------
    Set[Repository]
        A set containing the unique repositories that are referenced by the
        tool list.

    Raises
    ------
    RuntimeError
        If one of the tool names provides does not correspond to one of our
        (brainglobe) repositories.
    """
    unique_repos: Set[Repository] = set()

    # Infer the unique repositories from the list of tools
    for tool in tools:
        repo_to_cite: Repository = None
        for repo in all_citable_repositories():
            if tool in repo:
                if repo_to_cite:
                    # We have already found this alias in another repository,
                    # Flag error
                    raise ValueError(
                        f"Multiple repositories match tool {tool}: "
                        f"{repo_to_cite.name}, {repo.name}"
                    )
                else:
                    # This is the first repository that might match the tool
                    repo_to_cite = repo
        if repo_to_cite is None:
            # No repository matches this tool, throw error.
            raise RuntimeError(
                f"No citable repository found for tool {tool}. "
                "If you think this option is missing, please report it: "
                "https://github.com/brainglobe/brainglobe-meta/issues"
            )
        elif (repo_to_cite in unique_repos) and report_duplicates:
            # We already added this repository, so print out a record
            # of the duplication
            print(f"{tool} is already being cited by {repo_to_cite.name}")
        else:
            # Add first occurrence of the repository to the unique list
            unique_repos.add(repo_to_cite)

    return unique_repos


# Static instances for each of our repositories
# that we provide citation information for.
bg_atlasapi = Repository(
    "bg-atlasapi",
    [
        "bg_atlasapi",
        "BrainGlobe AtlasAPI",
        "BrainGlobe AtlasAPI",
        "AtlasAPI",
        "Atlas API",
    ],
    cff_branch="add-citation-file",
)
brainglobe_meta = Repository(
    "brainglobe-meta",
    [
        "brainglobe",
        "meta-package",
        "meta package",
        "meta",
        "toolsuite",
        "tool suite",
    ],
    cff_branch="add-citation-function",
)
brainglobe_utils = Repository(
    "brainglobe-utils",
    [
        "brainglobe_utils",
        "utils",
        "brainglobe utils",
        "brainglobe utilities",
    ],
)


def all_citable_repositories() -> List[Repository]:
    """
    Return a list of all citable brainglobe repositories.

    That is, a list of all static repository instances defined in
    this submodule.
    """
    return set(
        obj
        for _, obj in inspect.getmembers(
            sys.modules[__name__], lambda x: isinstance(x, Repository)
        )
    )
