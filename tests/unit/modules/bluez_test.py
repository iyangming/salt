# -*- coding: utf-8 -*-
'''
    :codeauthor: :email:`Rahul Handay <rahulha@saltstack.com>`
'''

# Import Python libs
from __future__ import absolute_import

# Import Salt Testing Libs
from salttesting import TestCase, skipIf
from salttesting.mock import (
    MagicMock,
    patch,
    NO_MOCK,
    NO_MOCK_REASON
)

# Import Salt Libs
from salt.modules import bluez
from salt.exceptions import CommandExecutionError
import salt.utils.validate.net


# Globals
bluez.__salt__ = {}


class MockBluetooth(object):
    '''
        Mock class for bluetooth
    '''
    def __init__(self):
        pass

    @staticmethod
    def discover_devices(lookup_names):
        '''
            Mock method to return all Discoverable devices
        '''
        return [['a', 'b', 'c'], ['d', 'e', 'f']]

bluez.bluetooth = MockBluetooth


@skipIf(NO_MOCK, NO_MOCK_REASON)
class BluezTestCase(TestCase):
    '''
        Test cases for salt.modules.bluez
    '''
    def test_version(self):
        '''
            Test if return bluetooth version
        '''
        mock = MagicMock(return_value="5.7")
        with patch.dict(bluez.__salt__, {'cmd.run': mock}):
            self.assertEqual(bluez.version(),
                             {'PyBluez': '<= 0.18 (Unknown, but installed)',
                                                'Bluez': '5.7'})

    def test_address_(self):
        '''
            Test of getting address of bluetooth adapter
        '''
        mock = MagicMock(return_value='hci : hci0')
        with patch.dict(bluez.__salt__, {'cmd.run': mock}):
            self.assertEqual(bluez.address_(),
                             {'hci ':
                              {'device': 'hci ', 'path':
                               '/sys/class/bluetooth/hci '}})

    def test_power(self):
        '''
            Test of getting address of bluetooth adapter
        '''
        mock = MagicMock(return_value={})
        with patch.object(bluez, 'address_', mock):
            self.assertRaises(CommandExecutionError, bluez.power, "hci0", "on")

        mock = MagicMock(return_value={'hci0':
                                        {'device': 'hci0', 'power': 'on'}})
        with patch.object(bluez, 'address_', mock):
            mock = MagicMock(return_value="")
            with patch.dict(bluez.__salt__, {'cmd.run': mock}):
                self.assertEqual(bluez.power("hci0", "on"), True)

        mock = MagicMock(return_value={'hci0':
                                       {'device': 'hci0', 'power': 'on'}})
        with patch.object(bluez, 'address_', mock):
            mock = MagicMock(return_value="")
            with patch.dict(bluez.__salt__, {'cmd.run': mock}):
                self.assertEqual(bluez.power("hci0", "off"), False)

    def test_discoverable(self):
        '''
            Test of enabling bluetooth device
        '''
        mock = MagicMock(side_effect=[{}, {'hci0':
                                       {'device': 'hci0', 'power': 'on'}},
                                       {'hci0':{'device': 'hci0',
                                               'power': 'on'}}])
        with patch.object(bluez, 'address_', mock):
            self.assertRaises(CommandExecutionError,
                              bluez.discoverable, "hci0")

            mock = MagicMock(return_value="UP RUNNING ISCAN")
            with patch.dict(bluez.__salt__, {'cmd.run': mock}):
                self.assertEqual(bluez.discoverable("hci0"), True)

            mock = MagicMock(return_value="")
            with patch.dict(bluez.__salt__, {'cmd.run': mock}):
                self.assertEqual(bluez.discoverable("hci0"), False)

    def test_noscan(self):
        '''
            Test of turning off of scanning modes
        '''
        mock = MagicMock(side_effect=[{}, {'hci0':
                                       {'device': 'hci0', 'power': 'on'}},
                                       {'hci0':{'device': 'hci0',
                                               'power': 'on'}}])
        with patch.object(bluez, 'address_', mock):
            self.assertRaises(CommandExecutionError, bluez.noscan, "hci0")

            mock = MagicMock(return_value="SCAN")
            with patch.dict(bluez.__salt__, {'cmd.run': mock}):
                self.assertEqual(bluez.noscan("hci0"), False)

            mock = MagicMock(return_value="")
            with patch.dict(bluez.__salt__, {'cmd.run': mock}):
                self.assertEqual(bluez.noscan("hci0"), True)

    def test_scan(self):
        '''
            Test of scanning of bluetooth devices
        '''
        self.assertEqual(bluez.scan(), [{'a': 'b'}, {'d': 'e'}])

    def test_block(self):
        '''
            Test of blocking specific bluetooth device
        '''
        mock = MagicMock(side_effect={False, True})
        with patch.object(salt.utils.validate.net, 'mac', mock):
            self.assertRaises(CommandExecutionError,
                              bluez.block, "DE:AD:BE:EF:CA:ZE")

            mock = MagicMock(return_value="")
            with patch.dict(bluez.__salt__, {'cmd.run': mock}):
                self.assertEqual(bluez.block("DE:AD:BE:EF:CA:FE"), None)

    def test_unblock(self):
        '''
            Test to unblock specific bluetooth device
        '''
        mock = MagicMock(side_effect={False, True})
        with patch.object(salt.utils.validate.net, 'mac', mock):
            self.assertRaises(CommandExecutionError,
                              bluez.block, "DE:AD:BE:EF:CA:ZE")

            mock = MagicMock(return_value="")
            with patch.dict(bluez.__salt__, {'cmd.run': mock}):
                self.assertEqual(bluez.unblock("DE:AD:BE:EF:CA:FE"), None)


    def test_pair(self):
        '''
            Test to pair bluetooth adapter with a device
        '''
        mock = MagicMock(side_effect=[False, True, True])
        with patch.object(salt.utils.validate.net, 'mac', mock):
            self.assertRaises(CommandExecutionError,
                              bluez.pair, "DE:AD:BE:EF:CA:FE", "1234")

            self.assertRaises(CommandExecutionError,
                              bluez.pair, "DE:AD:BE:EF:CA:FE", "abcd")

            mock = MagicMock(return_value={'device': 'hci0'})
            with patch.object(bluez, 'address_', mock):
                mock = MagicMock(return_value="Ok")
                with patch.dict(bluez.__salt__, {'cmd.run': mock}):
                    self.assertEqual(bluez.
                                     pair("DE:AD:BE:EF:CA:FE", "1234"), ["Ok"])

    def test_unpair(self):
        '''
            Test to unpair bluetooth adaptor with a device
        '''
        mock = MagicMock(side_effect={False, True})
        with patch.object(salt.utils.validate.net, 'mac', mock):
            self.assertRaises(CommandExecutionError,
                              bluez.unpair, "DE:AD:BE:EF:CA:FE")

            mock = MagicMock(return_value="Ok")
            with patch.dict(bluez.__salt__, {'cmd.run': mock}):
                self.assertEqual(bluez.unpair("DE:AD:BE:EF:CA:FE"), ["Ok"])

    def test_start(self):
        '''
            Test to start bluetooth service
        '''
        mock = MagicMock(return_value="Ok")
        with patch.dict(bluez.__salt__, {'service.start': mock}):
            self.assertEqual(bluez.start(), "Ok")

    def test_stop(self):
        '''
            Test to stop bluetooth service
        '''
        mock = MagicMock(return_value="Ok")
        with patch.dict(bluez.__salt__, {'service.stop': mock}):
            self.assertEqual(bluez.stop(), "Ok")

if __name__ == '__main__':
    from integration import run_tests
    run_tests(BluezTestCase, needs_daemon=False)
