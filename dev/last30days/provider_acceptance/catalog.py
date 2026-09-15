"""Closed catalog of the eight acquisition adapters in WI-010."""

from .contracts import AcceptanceCatalog, AdapterCase


_ROOT = "tests/provider_acceptance/fixtures"


def default_catalog() -> AcceptanceCatalog:
    return AcceptanceCatalog(
        (
            AdapterCase("x-browser", "x_agent_browser", "x", "browser", f"{_ROOT}/x.json", accounting_confidence="opaque_request_equivalent"),
            AdapterCase("facebook-browser", "facebook_agent_browser", "facebook", "browser", f"{_ROOT}/facebook.json", accounting_confidence="opaque_request_equivalent"),
            AdapterCase("linkedin-post-browser", "linkedin_agent_browser", "linkedin", "browser", f"{_ROOT}/linkedin_post.json", accounting_confidence="opaque_request_equivalent"),
            AdapterCase("linkedin-profile-browser", "linkedin_profile_agent_browser", "linkedin", "browser", f"{_ROOT}/linkedin_profile.json", accounting_confidence="opaque_request_equivalent"),
            AdapterCase("youtube-command", "youtube_ytdlp", "youtube", "command", f"{_ROOT}/youtube.json", accounting_confidence="opaque_request_equivalent"),
            AdapterCase("reddit-keyless-http", "reddit_keyless", "reddit", "http", f"{_ROOT}/reddit_keyless.json"),
            AdapterCase("reddit-browser", "reddit_agent_browser", "reddit", "browser", f"{_ROOT}/reddit_browser.json", accounting_confidence="opaque_request_equivalent"),
            AdapterCase("reddit-scrapecreators-http", "reddit_scrapecreators", "reddit", "http", f"{_ROOT}/reddit_scrapecreators.json"),
        )
    )
