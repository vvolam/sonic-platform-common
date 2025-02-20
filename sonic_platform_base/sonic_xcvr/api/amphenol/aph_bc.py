"""
    aph_bc.py

    Implementation of Amphenol Backplane Catridge specific transceiver info in addition
    to the CMIS specification.
"""

import copy
from ...fields import consts
from ..public.cmis import CmisApi

APH_XCVR_INFO_DEFAULT_DICT = {
        "type": "N/A",
        "type_abbrv_name": "N/A",
        "hardware_rev": "N/A",
        "serial": "N/A",
        "manufacturer": "N/A",
        "model": "N/A",
        "slot_id": "N/A",
        "encoding": "N/A",
        "ext_identifier": "N/A",
        "ext_rateselect_compliance": "N/A",
        "cable_length": "N/A",
        "nominal_bit_rate": "N/A",
        "vendor_date": "N/A",
        "vendor_oui": "N/A",
        **{f"active_apsel_hostlane{i}": "N/A" for i in range(1, 9)},
        "application_advertisement": "N/A",
        "host_electrical_interface": "N/A",
        "media_interface_code": "N/A",
        "host_lane_count": "N/A",
        "media_lane_count": "N/A",
        "host_lane_assignment_option": "N/A",
        "media_lane_assignment_option": "N/A",
        "cable_type": "N/A",
        "media_interface_technology": "N/A",
        "vendor_rev": "N/A",
        "cmis_rev": "N/A",
        "specification_compliance": "N/A",
        "vdm_supported": "N/A"
        }

class CmisAphBcApi(CmisApi):
    def _get_xcvr_info_default_dict(self):
        return APH_XCVR_INFO_DEFAULT_DICT

    def get_transceiver_info(self):
        admin_info = self.xcvr_eeprom.read(consts.ADMIN_INFO_FIELD)
        if admin_info is None:
            return None

        ext_id = admin_info[consts.EXT_ID_FIELD]
        power_class = ext_id[consts.POWER_CLASS_FIELD]
        max_power = ext_id[consts.MAX_POWER_FIELD]
        xcvr_info = copy.deepcopy(self._get_xcvr_info_default_dict())
        xcvr_info.update({
            "type": admin_info[consts.ID_FIELD],
            "type_abbrv_name": admin_info[consts.ID_ABBRV_FIELD],
            "hardware_rev": self.get_module_hardware_revision(),
            "serial": admin_info[consts.VENDOR_SERIAL_NO_FIELD],
            "manufacturer": admin_info[consts.VENDOR_NAME_FIELD],
            "model": admin_info[consts.VENDOR_PART_NO_FIELD],
            "slot_id": admin_info[consts.CONNECTOR_FIELD],
            "ext_identifier": "%s (%sW Max)" % (power_class, max_power),
            "cable_length": float(admin_info[consts.LENGTH_ASSEMBLY_FIELD]),
            "vendor_date": admin_info[consts.VENDOR_DATE_FIELD],
            "vendor_oui": admin_info[consts.VENDOR_OUI_FIELD],
            "application_advertisement": str(self.get_application_advertisement()) if len(self.get_application_advertisement()) > 0 else 'N/A',
            "host_electrical_interface": self.get_host_electrical_interface(),
            "media_interface_code": self.get_module_media_interface(),
            "host_lane_count": self.get_host_lane_count(),
            "media_lane_count": self.get_media_lane_count(),
            "host_lane_assignment_option": self.get_host_lane_assignment_option(),
            "media_lane_assignment_option": self.get_media_lane_assignment_option(),
            "cable_type": self.get_cable_length_type(),
            "media_interface_technology": self.get_media_interface_technology(),
            "vendor_rev": self.get_vendor_rev(),
            "cmis_rev": self.get_cmis_rev(),
            "specification_compliance": self.get_module_media_type(),
            "vdm_supported": self.is_transceiver_vdm_supported()
        })
        apsel_dict = self.get_active_apsel_hostlane()
        for lane in range(1, self.NUM_CHANNELS + 1):
            xcvr_info["%s%d" % ("active_apsel_hostlane", lane)] = \
            apsel_dict["%s%d" % (consts.ACTIVE_APSEL_HOSTLANE, lane)]

        # In normal case will get a valid value for each of the fields. If get a 'None' value
        # means there was a failure while reading the EEPROM, either because the EEPROM was
        # not ready yet or experiencing some other issues. It shouldn't return a dict with a
        # wrong field value, instead should return a 'None' to indicate to XCVRD that retry is
        # needed.
        if None in xcvr_info.values():
            return None
        else:
            return xcvr_info
