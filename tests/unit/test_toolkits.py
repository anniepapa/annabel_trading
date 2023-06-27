from toolkits import utc_to_cet


def test_utc_to_cet():
    actual_cet = utc_to_cet("2023-06-26T12:50:01.718021Z")
    assert actual_cet == "2023-06-26T14:50:01"
