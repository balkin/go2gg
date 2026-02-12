from go2gg.payloads import map_snake_keys, snake_to_camel


def test_snake_to_camel() -> None:
    assert snake_to_camel("destination_url") == "destinationUrl"
    assert snake_to_camel("utm_source") == "utmSource"


def test_map_snake_keys_drops_none_and_converts() -> None:
    payload = {
        "destination_url": "https://example.com",
        "utm_source": "email",
        "click_limit": None,
    }
    mapped = map_snake_keys(payload)
    assert mapped == {
        "destinationUrl": "https://example.com",
        "utmSource": "email",
    }
