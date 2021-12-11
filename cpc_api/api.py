# -*- coding: utf-8 -*-
"""
Main module of CPC-API containing access classes to the API.
"""
from io import BytesIO
import numpy as np

import imageio
import requests
import warnings

with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=UserWarning)
    from fuzzywuzzy.process import extractBests


__all__ = ['CPCApi', 'Parliamentarian', 'Vote', 'Balloting']


def memoize(f):
    def aux(*args, **kargs):
        k = (args, tuple(sorted(kargs.items())))
        if k not in CPCApi.cache:
            CPCApi.cache[k] = f(*args, **kargs)
        return CPCApi.cache[k]
    return aux

class CPCApi(object):
    """
    Main access point to the API.

    """
    format = 'json'
    cache = {}

    def __init__(self, ptype='depute', legislature=None):
        """
        :param ptype: depute or senateur
        :param legislature: 2007-2012 or None
        """

        assert(ptype in ['depute', 'senateur'])
        assert(legislature in ['2007-2012', '2012-2017', '2017-2022', None])
        self.legislature = legislature
        self.ptype = ptype
        self.ptype_plural = ptype + 's'
        self.base_url = 'https://%s.nos%s.fr' % (legislature or 'www', self.ptype_plural)
        self.dct_all_ballotings = dict()

    def synthese(self, month=None):
        """
        month format: YYYYMM
        """
        if month is None and self.legislature == '2012-2017':
            raise AssertionError('Global Synthesis on legislature does not work, see https://github.com/regardscitoyens/nosdeputes.fr/issues/69')

        if month is None:
            month = 'data'

        url = '%s/synthese/%s/%s' % (self.base_url, month, self.format)

        data = requests.get(url).json()
        return [depute[self.ptype] for depute in data[self.ptype_plural]]

    def parliamentarian(self, slug_name):
        url = '%s/%s/%s' % (self.base_url, slug_name, self.format)
        return requests.get(url).json()[self.ptype]

    def picture(self, slug_name, pixels='60') -> np.ndarray:

        return imageio.imread(BytesIO(requests.get(self.picture_url(slug_name, pixels=pixels)).content))

    def picture_url(self, slug_name, pixels='60') -> str:
        """
        Return the url to the picture of parliamentarian specified by `slug_name` and with size

        :param slug_name:
        :param pixels:
        :return:
        """
        return '%s/%s/photo/%s/%s' % (self.base_url, self.ptype, slug_name, pixels)

    def search(self, q, page=1):
        # XXX : the response with json format is not a valid json :'(
        # Temporary return csv raw data
        # url = '%s/recherche/%s?page=%s&format=%s' % (self.base_url, q, page, 'csv')
        url = '%s/recherche/%s?page=%s&format=%s' % (self.base_url, q, page, self.format)
        return requests.get(url).json()

    def parliamentarian_votes(self, p_slug):
        """
        Return the votes of parliamentarian specified by `p_slug`

        :param p_slug: slug of paralimentarian.
        :return: list of Votes objects.
        """
        url = '%s/%s/%s/%s' % (self.base_url, p_slug, "votes", self.format)
        data = requests.get(url).json()  # todo error may happen here

        lst_votes = []
        for dict_vote in data["votes"]:
            dict_vote = dict_vote["vote"]
            dict_balloting = dict_vote["scrutin"]
            balloting = self.dct_all_ballotings[dict_balloting["numero"]] = self.dct_all_ballotings.get(dict_balloting["numero"], Balloting(dict_balloting))
            vote_obj = Vote(dict_vote, balloting)
            lst_votes.append(vote_obj)

        return lst_votes



    @memoize
    def parlementarians(self, active=None):
        """
        Return list of parliamentarians.

        :param active: If True, return only "enmandat" parliamentarians. (default: None)
        :return: list of Parliamentarian objects.
        """
        if active is None:
            url = '%s/%s/%s' % (self.base_url, self.ptype_plural, self.format)
        else:
            url = '%s/%s/enmandat/%s' % (self.base_url, self.ptype_plural, self.format)

        data = requests.get(url).json()
        return [Parliamentarian(depute[self.ptype], self) for depute in data[self.ptype_plural]]

    def search_parliamentarians(self, q: str, field: str = 'nom', limit: int = None, no_score: bool = True):
        """
        Find a parliamentary based on query `q` on field `field` in the list of parliamentarians.


        :param q: A string close to a substring of `field`
        :param field: A field in the Parliamentarian objects returned by function self.parliamentarians().
        :param limit: If None, return only the first parliamentarian. Number of parliamentarians to return. (default: None)
        :param no_score: If True: Do not return the score of each parliamentarian in the search function.
        :return:
        """

        extracted = extractBests(q, self.parlementarians(),
                                 processor=lambda x: x.__dict__[field] if isinstance(x, Parliamentarian) else x,
                                 limit=limit or 1)
        if limit is None:
            if no_score:
                return extracted[0][0]
            else:
                return extracted[0]
        if no_score:
            return [elm[0] for elm in extracted]
        else:
            return extracted


class Vote:
    """
    Vote class.
    """
    def __init__(self, dct_vote, balloting):
        self.__dict__.update(dct_vote)  # todo explicit attributes: sqlalchemy
        self.balloting = balloting
        self.number_vote = self.balloting.numero
        self.balloting.add_vote(self)

    def __hash__(self):
        return hash(f"{self.number_vote}{self.parlementaire_slug}")

    def __repr__(self):
        return f"<{self.__class__.__name__}: ({self.number_vote}) {self.parlementaire_slug} [{self.position}]>"


class Balloting:
    """
    Balloting class contains a set of votes. It correspond to the pull of all votes made by all parliamentarian
    who voted at a single balloting.
    """
    def __init__(self, dct_balloting):
        """ salut """
        self.__dict__.update(dct_balloting)  # todo explicit attributes: sqlalchemy
        self.set_votes = set()

    def add_vote(self, vote: Vote):
        """
        Add Vote object to the set of votes in balloting. Each vote can appear only once.

        :param vote: Vote object.
        :return: None
        """
        self.set_votes.add(vote)

    def __repr__(self):
        """ salut """
        nb_displayed_chars = 50
        return f"<Balloting: ({self.numero}) '{self.titre[:nb_displayed_chars]}'[{self.sort}]>"


class Parliamentarian:
    """
    Parliamentarian interfaces CPCApi
    """
    def __init__(self, dict_parl, api: CPCApi):
        self.__dict__.update(dict_parl)  # todo explicit attributes: sqlalchemy
        self.api = api

    def get_votes(self):
        """
        Return list of votes of parliamentarian.

        :return: list of Vote objects
        """
        return self.api.parliamentarian_votes(self.slug)

    def __repr__(self):
        str_repr = f"<{self.__class__.__name__}: {self.nom} {self.groupe_sigle} {self.nom_circo}({self.num_circo}); ID={self.id_an}>"
        return str_repr