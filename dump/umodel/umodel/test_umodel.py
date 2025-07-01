from dataclasses import dataclass
from pprint import pprint
import typing
import unittest
from umodel import UItem
from umodel.attrs import UError, UKey, UPrimaryKey, UniqueKey

UID_MUST_BE_AT_LEAST_7 = lambda x : len(str(x)) == 7
VALID_EMAIL = lambda x : "@" in x and not x.startswith("@") and not x.endswith("@")
        
@dataclass
class testx(UItem):
    uid : typing.Union[int, UPrimaryKey, UID_MUST_BE_AT_LEAST_7]
    name : typing.Union[str, UniqueKey]
    age : typing.Union[int, UKey]
    something_random : typing.Union[str, UniqueKey] = None
    somemore_random : typing.Union[str, UniqueKey] = None

class test_modelling(unittest.TestCase):
    def testpoc_1(self):
        @dataclass
        class test(UItem):
            uid : typing.Union[int, UPrimaryKey, UID_MUST_BE_AT_LEAST_7]
            name : typing.Union[str, UniqueKey]
            age : typing.Union[int, UKey]
            address : typing.Union[str, UKey]
            phone : typing.Union[int, UniqueKey]
            email : typing.Union[str, UniqueKey, VALID_EMAIL]

        pprint(test.get_stats())

    def test_1(self):
        x = testx(
            uid=1234555,
            name="hello",
            age=12,
        )
        # test if primary key has been casted to str
        self.assertEqual(x.uid, 1234555)

        # test if primary key can't be changed
        with self.assertRaises(UError):
            x.uid = "12345"
        # test cannot create an item with same primary key
        with self.assertRaises(UError):
            testx(
                uid=1234555,
                name="pass",
                age=12,
            )
        # test cannot create an item with same unique key name
        with self.assertRaises(UError):
            testx(
                uid=1234566,
                name="hello",
                age=12,
            )
        # test
        testx(
            uid=1234566,
            name="pass",
            age=12,
        )
        data =testx.export_all()
        pprint(data)
        self.assertEqual(len(data), 2)
        
        # test remove
        testx.remove(uid=1234566)
        data =testx.export_all()
        pprint(data)
        self.assertEqual(len(data), 1)

    def test_2(self):
        x = testx(
            uid="1234555",
            name="hello",
            age=12,
        )
        y = testx(
            uid=1234566,
            name="pass",
            age=12,
        )
        z = testx(
            uid=1234577,
            name="someone",
            age=12,
        )

        zz = testx(
            uid=1234578,
            name="some1",
            age=21,
        )

        pulled = testx.get(uid=1234566)
        self.assertIsNotNone(pulled)
        self.assertEqual(pulled.name, "pass")