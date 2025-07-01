from time import sleep
import typing
import unittest
from uuid import UUID, uuid4
from habil.base import HabilElement
from habil.base.elementMeta import HabilElementMeta

class tcls(HabilElement):
    name : str

class tcls2(HabilElement):
    x : tcls
    y : typing.List[tcls]

class t_habil_abcbase(unittest.TestCase):
    def test_1(self):
        u1 = uuid4()
        u2 = uuid4()
        u3 = uuid4()
        u4 = uuid4()
        ins = tcls2(
            **{
                "id": u1,
                "name" : "test",
                "x" : {
                    "id" : u2,
                    "name" : "test2"
                },
                "y" : [
                    {
                        "id" : u3,
                        "name" : "test3"
                    },
                    {
                        "id" : u4,
                        "name" : "test4"
                    }
                ]
            }
        )

        sleep(1)

        t = tcls(
            **{
                "id" : u3,
                "name" : "i changed"
            }
        )

        t = tcls(
            **{
                "id" : u3,
                "name" : "i didnt changed",
                "__no_update" : True
            }
        )

        self.assertEqual(ins.y[0].name, "i changed")
