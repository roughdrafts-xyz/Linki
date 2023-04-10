from unittest import TestCase

from sigili.subscription import MemorySubscriptionRepository, SubscriptionURL


def test_crud_subscriptions():
    url = 'test_location'
    SubURL = SubscriptionURL(url)
    subscriptions = MemorySubscriptionRepository()
    subscriptions.add_subscription(url)

    test = TestCase()
    test.assertCountEqual([SubURL.labelId], subscriptions.get_subscriptions())
