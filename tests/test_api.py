from backend.api_interactions.cello_requests import CelloAPI

import pytest

# Please don't dox me.
USERNAME = 'jax@0x174.io'
PASSWORD = 'test'


@pytest.fixture
def instantiate_cello_api():
    return CelloAPI(username=USERNAME, password=PASSWORD)


def test_cello_auth_context_manager(instantiate_cello_api):
    cello_api = instantiate_cello_api
    with cello_api.auth as authentication_mechanism:
        pass
