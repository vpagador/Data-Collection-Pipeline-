from TPW_scraper import *
import unittest


class TpwTestCase(unittest.TestCase):

    def setUp(self):
        self.test = TPW()
        self.test.product_urls_list = ['https://www.theproteinworks.com/upgrade']
        self.test.generate_product_dict()
        
    def test_get_pages(self):
        self.test.get_pages()
        expected_value= ['https://www.theproteinworks.com/products/page/1',
        'https://www.theproteinworks.com/products/page/2',
        'https://www.theproteinworks.com/products/page/3',
        'https://www.theproteinworks.com/products/page/4',
        'https://www.theproteinworks.com/products/page/5',
        'https://www.theproteinworks.com/products/page/6',
        'https://www.theproteinworks.com/products/page/7']
        actual_value = self.test.page_urls_list
        self.assertEqual(expected_value, actual_value)

    def test_generate_product_dict_name(self):
        expected_value = "Upgrade Multi-Protein"
        actual_value = self.test.product_list[0]['contents']['Product Name'][0]
        self.assertEqual(expected_value, actual_value)

    def test_scrape_day(self):
        days = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
        day = self.test.product_list[0]['time'][0:3]
        self.assertTrue(day in days)

    def test_pound_sign(self):
        price = self.test.product_list[0]['contents']['Price'][0]
        self.assertRegex('£', price[0])
    
    def test_key_values_type(self):
        for k in self.test.product_list[0]['contents']:
            value = self.test.product_list[0]['contents'][k][0]
            self.assertIsInstance(value, str)

    def tearDown(self):
        del self.test
        





