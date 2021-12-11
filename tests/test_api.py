# -*- coding: utf-8 -*-

import unittest

from cpc_api import CPCApi


class SearchQuestionServiceTest(unittest.TestCase):
    def test_deputes(self):
        api = CPCApi(legislature='2012-2017')
        self.assertGreater(len(api.parlementarians()), 1)
        self.assertEqual(api.search_parliamentarians('Cope')[0][0].nom_de_famille, u'Copé')

    def test_senateurs(self):
        api = CPCApi(ptype='senateur')
        self.assertGreater(len(api.parlementarians()), 1)
        self.assertEqual(api.search_parliamentarians('Larcher')[0][0].nom_de_famille, u'Larcher')

    def test_2007_2012(self):
        api = CPCApi(legislature='2007-2012')
        self.assertGreater(len(api.parlementarians()), 1)
        self.assertEqual(api.search_parliamentarians('Morano')[0][0].nom_de_famille, u'Morano')

    def test_2017_2022(self):
        api = CPCApi(legislature='2017-2022')
        parlementaires = api.parlementarians()
        self.assertGreater(len(parlementaires), 1)
        self.assertEqual(api.search_parliamentarians('Melenchon')[0][0].nom_de_famille, u'Mélenchon')

    def test_search(self):
        api = CPCApi(legislature='2017-2022')
        result = api.search("Melenchon")
        self.assertEqual(len(result), 4)


class ParliamentarianTest(unittest.TestCase):
    def setUp(self) -> None:
        self.api = CPCApi(legislature='2017-2022')
        self.parlementarians = self.api.parlementarians()

    def test_get_vote_from_depute(self):
        for parl in self.parlementarians[:10]:
            _ = parl.get_votes()
        print(len(self.api.dct_all_ballotings))
