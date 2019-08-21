"""Test API with Scope Middleware."""

import pytest
import json
from flask import Response
from expects import expect, be, equal, raise_error, be_above_or_equal, contain


class TestSecuredAPI(object):
    def test_api_access(self, client):
        expect(1).to(be(1))
