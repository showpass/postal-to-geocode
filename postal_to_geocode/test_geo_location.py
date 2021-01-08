from .postal_to_area import lookup_postal_code
from unittest import TestCase


class LookUpTests(TestCase):
    def test_lookup_address_found(self):
        postal_data = lookup_postal_code('CA', 'T2Y0G4')
        self.assertEqual('CA', postal_data['country'])
        self.assertEqual('Calgary (Millrise / Somerset / Bridlewood / Evergreen)', postal_data['community'])
        self.assertEqual('Alberta', postal_data['province'])
        self.assertEqual('AB', postal_data['short_province'])
        self.assertEqual('Calgary', postal_data['city'])
        self.assertEqual(50.9093, postal_data['latitude'])
        self.assertEqual(-114.1028, postal_data['longitude'])