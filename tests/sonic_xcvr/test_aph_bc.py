import pytest
from mock import MagicMock
from sonic_platform_base.sonic_xcvr.mem_maps.public.cmis import CmisMemMap
from sonic_platform_base.sonic_xcvr.xcvr_eeprom import XcvrEeprom
from sonic_platform_base.sonic_xcvr.codes.public.cmis import CmisCodes
from sonic_platform_base.sonic_xcvr.api.amphenol.aph_bc import APH_XCVR_INFO_DEFAULT_DICT, CmisAphBcApi

class TestCmisAphBcApi(object):
    codes = CmisCodes
    mem_map = CmisMemMap(codes)
    reader = MagicMock(return_value=None)
    writer = MagicMock()
    eeprom = XcvrEeprom(reader, writer, mem_map)
    old_read_func = eeprom.read
    api = CmisAphBcApi(eeprom)

    @pytest.mark.parametrize("mock_response, expected", [
        # Case: No transceiver data
        ([None] * 15, None),

        # Case: Valid transceiver data
        (
            [
                {   # EEPROM mocked Data
                    'Extended Identifier': {'Power Class': 'Power Class 8', 'MaxPower': 20.0},
                    'Identifier': 'Backplane Catridge',
                    'Identifier Abbreviation': 'AphBC',
                    'ModuleHardwareMajorRevision': 0,
                    'ModuleHardwareMinorRevision': 0,
                    'VendorSN': '00000000',
                    'VendorName': 'VENDOR_NAME',
                    'VendorPN': 'ABCD',
                    'Connector': 1,
                    'Length Cable Assembly': 0.0,
                    'ModuleMediaType': 'sm_media_interface',
                    'VendorDate': '21010100',
                    'VendorOUI': 'xx-xx-xx',
                    'vdm_supported': True,
                },
                '400GAUI-8 C2M (Annex 120E)',
                '400ZR, DWDM, amplified',
                8, 1, 1, 1,
                {f'ActiveAppSelLane{i}': 1 for i in range(1, 9)},
                '1550 nm DFB',
                '0.0',
                '5.0',
                '0.1',
                '0.0',
                'sm_media_interface',
                {'status': True, 'result': ("0.5.2", 1, 1, 0, "0.2.0", 0, 0, 0, "0.5.2", "0.2.0")}
            ],
            {   # Expected transceiver info
                'type': 'Backplane Catridge',
                'type_abbrv_name': 'AphBC',
                'hardware_rev': '0.0',
                'serial': '00000000',
                'manufacturer': 'VENDOR_NAME',
                'model': 'ABCD',
                'slot_id': 1,
                'encoding': 'N/A',
                'ext_identifier': 'Power Class 8 (20.0W Max)',
                'ext_rateselect_compliance': 'N/A',
                'cable_length': 0.0,
                'nominal_bit_rate': 'N/A',
                'vendor_date': '21010100',
                'vendor_oui': 'xx-xx-xx',
                **{f'active_apsel_hostlane{i}': 1 for i in range(1, 9)},
                'application_advertisement': 'N/A',
                'host_electrical_interface': '400GAUI-8 C2M (Annex 120E)',
                'media_interface_code': '400ZR, DWDM, amplified',
                'host_lane_count': 8,
                'media_lane_count': 1,
                'host_lane_assignment_option': 1,
                'media_lane_assignment_option': 1,
                'cable_type': 'Length Cable Assembly(m)',
                'media_interface_technology': '1550 nm DFB',
                'vendor_rev': '0.0',
                'cmis_rev': '5.0',
                'specification_compliance': 'sm_media_interface',
                'vdm_supported': True,
            }
        )
    ])
    def test_get_transceiver_info(self, mock_response, expected):
        self.api.xcvr_eeprom.read = MagicMock(return_value = mock_response[0])
        self.api.get_host_electrical_interface = MagicMock(return_value = mock_response[1])
        self.api.get_module_media_interface = MagicMock(return_value = mock_response[2])
        self.api.get_host_lane_count = MagicMock(return_value = mock_response[3])
        self.api.get_media_lane_count = MagicMock(return_value = mock_response[4])
        self.api.get_host_lane_assignment_option = MagicMock(return_value = mock_response[5])
        self.api.get_media_lane_assignment_option = MagicMock(return_value = mock_response[6])
        self.api.get_active_apsel_hostlane = MagicMock(return_value = mock_response[7])
        self.api.get_media_interface_technology = MagicMock(return_value = mock_response[8])
        self.api.get_vendor_rev = MagicMock(return_value = mock_response[9])
        self.api.get_cmis_rev = MagicMock(return_value = mock_response[10])
        self.api.get_module_fw_info = MagicMock(return_value = mock_response[14])
        self.api.get_module_media_type = MagicMock(return_value = mock_response[13])
        self.api.get_module_hardware_revision = MagicMock(return_value="0.0")
        self.api.is_flat_memory = MagicMock(return_value=False)
        self.api.is_transceiver_vdm_supported = MagicMock(return_value=True)

        # Run test and validate output
        result = self.api.get_transceiver_info()
        assert result == expected

        if result is not None:
            # Test result is same as default dictionary length
            assert len(APH_XCVR_INFO_DEFAULT_DICT) == len(result)

        # Test negative path
        self.api.get_cmis_rev.return_value = None
        result = self.api.get_transceiver_info()
        assert result == None
