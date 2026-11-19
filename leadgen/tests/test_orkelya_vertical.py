from leadgen import get_vertical


def test_orkelya_logistics_never_promotes_directory_fit_to_buying_intent():
    score, tier, reason = get_vertical("orkelya_logistics").score(
        {"name": "Example Transport", "website": "https://example.test"}
    )

    assert score == 0
    assert tier == "C"
    assert "need" in reason
    assert "do not contact" in reason


def test_orkelya_logistics_has_only_public_osm_directory_tags():
    vertical = get_vertical("orkelya_logistics")

    assert vertical.osm_tags == [
        "office=logistics",
        "office=transport",
        "industrial=warehouse",
    ]
    assert vertical.enrich_fn is None
    assert vertical.opener_fn is None
