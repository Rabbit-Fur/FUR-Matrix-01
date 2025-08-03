import pytest

import utils.oauth_utils as mod


def test_generate_code_verifier_length_default():
    verifier = mod.generate_code_verifier()
    assert 43 <= len(verifier) <= 128


def test_generate_code_verifier_custom_length():
    verifier = mod.generate_code_verifier(50)
    assert len(verifier) == 50


def test_generate_code_verifier_invalid():
    with pytest.raises(ValueError):
        mod.generate_code_verifier(42)
    with pytest.raises(ValueError):
        mod.generate_code_verifier(129)


def test_generate_code_challenge_known_value():
    verifier = "test_verifier_string"
    challenge = mod.generate_code_challenge(verifier)
    expected = "ktZu5ELbnUnx97HKaZsNZbfVaXdT1D2IdagpxxtQEI0"
    assert challenge == expected


def test_exchange_code_for_token_payload_includes_client_secret(monkeypatch):
    def fake_post(url, data=None, timeout=10):
        fake_post.called_data = data

        class Resp:
            def raise_for_status(self):
                pass

            def json(self):  # noqa: D401 - dummy
                return {}

        return Resp()

    monkeypatch.setattr(mod.requests, "post", fake_post)
    mod.exchange_code_for_token(
        code="abc",
        code_verifier="ver",
        client_id="cid",
        redirect_uri="uri",
        client_secret="secret",
    )
    assert fake_post.called_data["client_secret"] == "secret"
