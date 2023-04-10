from pathlib import Path
from unittest import TestCase

from sigili.subscription import MemorySubscriptionRepository, SubscriptionURL


def test_crud_subscriptions(tmp_path):
    url = Path(tmp_path).resolve().as_uri()
    SubURL = SubscriptionURL(url)
    subscriptions = MemorySubscriptionRepository()
    subscriptions.add_subscription(url)

    assert subscriptions.get_subscription(SubURL.labelId) == SubURL

    test = TestCase()
    test.assertCountEqual([SubURL.labelId], subscriptions.get_subscriptions())
