import unittest
import update_province as UP

class ProvinceUpdated(unittest.TestCase):
    def test_download_bad_url(self):
        """ValueError"""
        data = UP.get_data_from_github("sasda")
        self.assertEqual("bad_url", data)
    def test_download_wrong_url(self):
        """UnicodeDecodeError"""
        data = UP.get_data_from_github("https://google.com")
        self.assertEqual("bad_url", data)
