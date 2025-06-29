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
