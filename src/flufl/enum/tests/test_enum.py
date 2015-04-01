# Copyright (C) 2011-2012 by Barry A. Warsaw
#
# This file is part of flufl.enum.
#
# flufl.enum is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# flufl.enum is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License
# for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with flufl.enum.  If not, see <http://www.gnu.org/licenses/>.

"""Additional package tests."""

from __future__ import absolute_import, print_function, unicode_literals

__metaclass__ = type
__all__ = [
    'TestEnum',
    ]


import unittest
import warnings

from flufl.enum import Enum, make, make_enum



class TestEnum(unittest.TestCase):
    """Additional unit tests."""

    def test_deprecations(self):
        # Enum.enumclass and Enum.enumname are deprecated.
        class Animals(Enum):
            ant = 1
            bee = 2
            cat = 3
        with warnings.catch_warnings(record=True) as seen:
            # Cause all warnings to always be triggered.
            warnings.simplefilter('always')
            Animals.ant.enumclass
        self.assertEqual(len(seen), 1)
        self.assertTrue(issubclass(seen[0].category, DeprecationWarning))
        self.assertEqual(seen[0].message.args[0],
                         '.enumclass is deprecated; use .enum instead')
        with warnings.catch_warnings(record=True) as seen:
            # Cause all warnings to always be triggered.
            warnings.simplefilter('always')
            Animals.ant.enumname
        self.assertEqual(len(seen), 1)
        self.assertTrue(issubclass(seen[0].category, DeprecationWarning))
        self.assertEqual(seen[0].message.args[0],
                         '.enumname is deprecated; use .name instead')

    def test_make_enum_identifiers_bug_803570(self):
        # LP: #803570 describes that make_enum() allows non-identifiers as
        # enum value names.
        try:
            make_enum('Foo', '1 2 3')
        except ValueError as exc:
            self.assertEqual(exc.args[0], 'non-identifiers: 1 2 3')
        else:
            raise AssertionError('Expected a ValueError')

    def test_make_enum_deprecated(self):
        # LP: #839529: deprecate the make_enum() API and use the much better
        # make() API.
        with warnings.catch_warnings(record=True) as seen:
            # Cause all warnings to always be triggered.
            warnings.simplefilter('always')
            make_enum('Foo', 'a b c')
        self.assertEqual(len(seen), 1)
        self.assertTrue(issubclass(seen[0].category, DeprecationWarning))
        self.assertEqual(seen[0].message.args[0],
                         'make_enum() is deprecated; use make() instead')

    def test_enum_make_not_all_2_tuples(self):
        # If 2-tuples are used, all items must be 2-tuples.
        self.assertRaises(ValueError, make, 'Animals', (
            ('ant', 1),
            ('bee', 2),
            'cat',
            ('dog', 4),
            ))
        self.assertRaises(ValueError, make, 'Animals', (
            ('ant', 1),
            ('bee', 2),
            ('cat',),
            ('dog', 4),
            ))
        self.assertRaises(ValueError, make, 'Animals', (
            ('ant', 1),
            ('bee', 2),
            ('cat', 3, 'oops'),
            ('dog', 4),
            ))

    def test_make_identifiers(self):
        # Ensure that the make() interface also enforces identifiers.
        try:
            make('Foo', ('1', '2', '3'))
        except ValueError as exc:
            self.assertEqual(exc.args[0], 'non-identifiers: 1 2 3')
        else:
            raise AssertionError('Expected a ValueError')
        try:
            make('Foo', (('ant', 1), ('bee', 2), ('3', 'cat')))
        except ValueError as exc:
            self.assertEqual(exc.args[0], 'non-identifiers: 3')
        else:
            raise AssertionError('Expected a ValueError')
