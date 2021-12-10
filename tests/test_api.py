# -*- coding: utf-8 -*-

import unittest

from cpc_api import CPCApi


class SearchQuestionServiceTest(unittest.TestCase):
    def test_deputes(self):
        api = CPCApi(legislature='2012-2017')
        self.assertGreater(len(api.parlementaires()), 1)
        self.assertEqual(api.search_parlementaires('Cope')[0][0].nom_de_famille, u'Copé')

    def test_senateurs(self):
        api = CPCApi(ptype='senateur')
        self.assertGreater(len(api.parlementaires()), 1)
        self.assertEqual(api.search_parlementaires('Larcher')[0][0].nom_de_famille, u'Larcher')

    def test_2007_2012(self):
        api = CPCApi(legislature='2007-2012')
        self.assertGreater(len(api.parlementaires()), 1)
        self.assertEqual(api.search_parlementaires('Morano')[0][0].nom_de_famille, u'Morano')

    def test_2017_2022(self):
        api = CPCApi(legislature='2017-2022')
        parlementaires = api.parlementaires()
        self.assertGreater(len(parlementaires), 1)
        self.assertEqual(api.search_parlementaires('Melenchon')[0][0].nom_de_famille, u'Mélenchon')


class ParliamentarianTest(unittest.TestCase):
    def setUp(self) -> None:
        self.api = CPCApi(legislature='2017-2022')

    def test_get_vote_from_depute(self):
        parlementarians = self.api.parlementaires()
        for parl in parlementarians[:10]:
            votes_parl = parl.get_votes()
        print(len(self.api.dct_all_ballotings))

