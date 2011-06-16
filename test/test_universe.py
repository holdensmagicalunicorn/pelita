import unittest
from pelita.universe import *

class TestLayoutChecks(unittest.TestCase):

    def test_strip_layout(self):
        test_layout = (
        """ #######
            #c    #
            #  .  #
            #    o#
            ####### """)
        stripped = [c for c in strip_layout(test_layout)]
        target = ['#', '#', '#', '#', '#', '#', '#', '\n',
                  '#', 'c', ' ', ' ', ' ', ' ', '#', '\n',
                  '#', ' ', ' ', '.', ' ', ' ', '#', '\n',
                  '#', ' ', ' ', ' ', ' ', 'o', '#', '\n',
                  '#', '#', '#', '#', '#', '#', '#', '\n']
        self.assertEqual(stripped, target)

    def test_illegal_character(self):
        illeagal_layout = (
        """ #######
            #c    #
            #  f  #
            #    o#
            ####### """)
        self.assertRaises(LayoutEncodingException, check_layout,
                strip_layout(illeagal_layout), 0)

    def test_not_enough_bots(self):
        not_enough_bots = (
        """#######
           #1    #
           #  2  #
           #    3#
           #######""")
        self.assertRaises(LayoutEncodingException, check_layout,
                strip_layout(not_enough_bots), 5)

    def test_too_many_bots(self):
        too_many_bots = (
        """ #######
            #1    #
            #  1  #
            #    3#
            ####### """)
        self.assertRaises(LayoutEncodingException, check_layout,
                strip_layout(too_many_bots), 3)

    def test_wrong_shape(self):
        wrong_shape = (
        """ #######
            #  #
            #   #
            #    #
            ###### """)
        self.assertRaises(LayoutEncodingException, check_layout,
                strip_layout(wrong_shape), 3)

if __name__ == '__main__':
    unittest.main()

