from requests import Session
import json
import singer
import singer.metrics as metrics

LOGGER = singer.get_logger()

_session = Session()
# wrapper to make mocking easier


def get_session():
    return _session


LOGGER = singer.get_logger()


def add_authorization_header(token: str) -> None:
    """
    Adds authorization header
    """
    get_session().headers.update({'Circle-Token': token})


def add_next_page_to_url(url: str, next_page_token: str) -> str:
    """
    Adds token to header to pull next page
    """
    return url + '?page-token=' + next_page_token


class AuthException(Exception):
    pass


class NotFoundException(Exception):
    pass


def get_single_entry(source: str, url: str, headers: dict = {}):
    """
    Get a single entryp from the provided url
    """

    with metrics.http_request_timer(source) as timer:
        get_session().headers.update(headers)
        resp = get_session().request(method='get', url=url)

        details = {
            'args': {'source': source, 'url': url, 'headers': headers},
            'response.text': resp.text
        }

        if resp.status_code == 401:
            raise AuthException(json.dumps(details))
        if resp.status_code == 403:
            raise AuthException(json.dumps(details))
        if resp.status_code == 404:
            raise NotFoundException(json.dumps(details))

        timer.tags[metrics.Tag.http_status_code] = resp.status_code
        return resp


def get_all_pages(source: str, url: str, headers: dict = {}):
    counter = 0
    temp_url = str(url)
    while True:
        LOGGER.info(f'get_all_pages: Paginating({counter}): {source}')
        counter += 1

        r = get_single_entry(source, temp_url, headers)
        r.raise_for_status()
        data = r.json()
        yield data
        if data.get('next_page_token') is not None:
            temp_url = add_next_page_to_url(url, data.get('next_page_token'))
        else:
            get_session().headers.pop("next_page_token", None)
            break


def get_all_items(source: str, url: str, headers: dict = {}):
    """
    Each page contains a bunch of items, so this function extracts the items one by one
    """
    for page in get_all_pages(source, url, headers):
        for item in page.get("items", [page]):
            yield item
