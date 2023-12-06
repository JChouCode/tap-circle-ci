import mock
import pytest
import requests

from tap_circle_ci.client import *

def test_get():
    with mock.patch('tap_circle_ci.client.get_session') as gs, \
            mock.patch('singer.metrics.log'):

        resp1 = mock.Mock()
        resp1.status_code = 200
        resp1.text = 'success'

        resp2 = mock.Mock()
        resp2.status_code = 401
        resp2.text = 'bad request'

        resp3 = mock.Mock()
        resp3.status_code = 404
        resp3.text = 'not found'

        fake_session = mock.create_autospec(requests.Session())
        fake_session.headers = {}
        fake_session.request.side_effect = [resp1, resp2, resp3]
        gs.return_value = fake_session

        r = get_single_entry('pipelines', 'https://circleci.com/api/v2/project/project1/pipeline')
        assert r.text == 'success'
        assert r.status_code == 200
        with pytest.raises(AuthException):
            get_single_entry('pipelines', 'https://circleci.com/api/v2/project/project1/pipeline')
        with pytest.raises(NotFoundException):
            get_single_entry('pipelines', 'https://circleci.com/api/v2/project/project1/pipeline')


def test_get_all_items():
    with mock.patch('tap_circle_ci.client.get_session') as gs, \
            mock.patch('singer.metrics.log'):

        resp1 = mock.Mock()
        resp1.status_code = 200
        resp1.text = 'success'
        resp1.json.return_value = {'next_page_token': 'qwertyuiop', 'items': ['a', 'b', 'c']}

        resp2 = mock.Mock()
        resp2.status_code = 200
        resp2.text = 'success'
        resp2.json.return_value = {'next_page_token': 'asdfghjkl', 'items': ['d', 'e', 'f']}

        resp3 = mock.Mock()
        resp3.status_code = 200
        resp3.text = 'not found'
        resp3.json.return_value = {'next_page_token': None, 'items': ['g', 'h', 'i', 'j', 'k', 'l']}

        fake_session = mock.create_autospec(requests.Session())
        fake_session.headers = {}
        fake_session.request.side_effect = [resp1, resp2, resp3]
        gs.return_value = fake_session

        data = list(get_all_items('pipelines', 'https://circleci.com/api/v2/project/project1/pipeline'))
        assert data == ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l']
