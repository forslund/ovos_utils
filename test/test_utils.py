import unittest
from ovos_utils import rotate_list, camel_case_split


class TestHelpers(unittest.TestCase):

    def test_utils(self):
        self.assertEqual(camel_case_split("MyAwesomeSkill"),
                         "My Awesome Skill")

        self.assertEqual(rotate_list([1, 2, 3]), [2, 3, 1])
        self.assertEqual(rotate_list([1, 2, 3], 2), [3, 1, 2])
        self.assertEqual(rotate_list([1, 2, 3], 3), [1, 2, 3])

        self.assertEqual(rotate_list([1, 2, 3], -1), [3, 1, 2])
        self.assertEqual(rotate_list([1, 2, 3], -2), [2, 3, 1])
        self.assertEqual(rotate_list([1, 2, 3], -3), [1, 2, 3])

