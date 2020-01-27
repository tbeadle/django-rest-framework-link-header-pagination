class MockObject:
    def __init__(self, idx):
        self.created = idx
        self.value = idx


class MockQuerySet:
    def __init__(self, items):
        self.items = items

    def filter(self, created__gt=None, created__lt=None):
        if created__gt is not None:
            return MockQuerySet(
                [item for item in self.items if item.created > int(created__gt)]
            )

        assert created__lt is not None
        return MockQuerySet(
            [item for item in self.items if item.created < int(created__lt)]
        )

    def order_by(self, *ordering):
        if ordering[0].startswith("-"):
            return MockQuerySet(list(reversed(self.items)))
        return self

    def __getitem__(self, sliced):
        return self.items[sliced]
