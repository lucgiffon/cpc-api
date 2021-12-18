# -*- coding: utf-8 -*-
"""
Main module of CPC-API containing access classes to the API.
"""
from io import BytesIO
import numpy as np
from functools import wraps
import imageio
import requests
import warnings
from typing import List

with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=UserWarning)
    from fuzzywuzzy.process import extractBests


__all__ = ['CPCApi', 'Parliamentarian', 'Vote', 'Balloting']


def memoize(f):
    @wraps(f)
    def aux(*args, **kargs):
        k = (args, tuple(sorted(kargs.items())))
        if k not in CPCApi.cache:
            CPCApi.cache[k] = f(*args, **kargs)
        return CPCApi.cache[k]
    return aux


class CPCApi(object):
    """
    The `CPCApi` objects provide access points to the API.

    Methods of this class make calls to the web API and return data objects.
    """
    format = 'json'
    cache = {}

    def __init__(self, ptype='depute', legislature=None):
        """
        Parameters
        ----------
        ptype: Choice(['depute', 'senateur'])
             This string will be part of the urls when requesting the API. It allows to specify
             which kind of parliamentarians you are interested into. (default: None)
        legislature: Choice(['2007-2012', '2012-2017', '2017-2022', None])
            This string will be part of the urls when requesting the API. It allows to specify what legislature
            period you are interested into.
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
        Returns a global synthesis of all parliamentarians on the given month.

        .. deprecated:: 0.1.5
            This function doesn't return data Object but a simple dict. Its returned values will be changed in the
            future.

        Parameters
        ----------
        month: str
         The month of the requested synthesis in format: YYYYMM.

        Returns
        -------
        A list of dict objects corresponding to the parliamentarians.
        """
        if month is None and self.legislature == '2012-2017':
            raise AssertionError('Global Synthesis on legislature does not work, '
                                 'see https://github.com/regardscitoyens/nosdeputes.fr/issues/69')

        if month is None:
            month = 'data'

        url = '%s/synthese/%s/%s' % (self.base_url, month, self.format)

        data = requests.get(url).json()
        # todo should return a list of Parliamentarian objects
        return [depute[self.ptype] for depute in data[self.ptype_plural]]

    @memoize
    def parliamentarian(self, slug_name):
        """
        Returns parliamentarian data object from its slug.

        Parameters
        ----------
        slug_name: str
            The slug of the parliamentarian. Usually its first and last name with a dash.

        Returns
        -------
        Parliamentarian
            Requested parliamentarian data object.
        """
        url = '%s/%s/%s' % (self.base_url, slug_name, self.format)
        # todo there should be a mecanism to handle errors in case of bad slug name.
        return Parliamentarian(requests.get(url).json()[self.ptype], self)

    @memoize
    def picture(self, slug_name, pixels='60') -> np.ndarray:
        """
        Returns the picture of the parliamentarian specified by `slug_name` and with `pixels` height.

        Parameters
        ----------
        slug_name: str
            The slug of the parliamentarian.
        pixels: int
            The height (number of rows) of the picture.

        Returns
        -------
        np.ndarray
            A 3D array representing the picture of the parliamentarian.
        """
        return imageio.imread(BytesIO(requests.get(self.picture_url(slug_name, pixels=pixels)).content))

    def picture_url(self, slug_name, pixels='60') -> str:
        """
        Returns the url to the picture of parliamentarian specified by `slug_name` and with height `pixels`.

        Parameters
        ----------
        slug_name: str
            The slug of the parliamentarian.
        pixels: int
            The height (number of rows) of the picture.

        Returns
        -------
        str
            The url of the picture.
        """
        return '%s/%s/photo/%s/%s' % (self.base_url, self.ptype, slug_name, pixels)

    @memoize
    def search(self, q: str, page: int = 1) -> dict:
        """
        Runs the search function of the website (nosdeputes.fr or nossenateurs.fr)
        and returns the search result as a dictionary.

        Parameters
        ----------
        q: str
            The query for the search.
        page: int
            The number of the page to display.

        Returns
        -------
        dict
            A dictionary representing the search result.
        """
        # url = '%s/recherche/%s?page=%s&format=%s' % (self.base_url, q, page, 'csv')
        # not necessary because now the returned format is a valid json
        url = '%s/recherche/%s?page=%s&format=%s' % (self.base_url, q, page, self.format)
        return requests.get(url).json()

    @memoize
    def parliamentarian_votes(self, p_slug: str) -> List:
        """
        Returns the votes of parliamentarian specified by `p_slug`.

        Parameters
        ----------
        p_slug: str
            The slug of the parliamentarian.

        Returns
        -------
        List[Vote]
            List of Vote objects from the parliamentarian.
        """
        url = '%s/%s/%s/%s' % (self.base_url, p_slug, "votes", self.format)
        data = requests.get(url).json()  # todo handle the error that may happen here

        lst_votes = []
        for dict_vote in data["votes"]:
            dict_vote = dict_vote["vote"]
            dict_balloting = dict_vote["scrutin"]
            balloting = self.dct_all_ballotings[dict_balloting["numero"]] = \
                self.dct_all_ballotings.get(dict_balloting["numero"], Balloting(dict_balloting))
            vote_obj = Vote(dict_vote, balloting)
            lst_votes.append(vote_obj)

        return lst_votes

    @memoize
    def parlementarians(self, active: bool = None) -> List:
        """
        Returns list of parliamentarians.

        Parameters
        ----------
        active: bool
            If True, return only "enmandat" parliamentarians. (default: None)

        Returns
        -------
        List[Parliamentarian]
            list of Parliamentarian objects.
        """
        if active is None:
            url = '%s/%s/%s' % (self.base_url, self.ptype_plural, self.format)
        else:
            url = '%s/%s/enmandat/%s' % (self.base_url, self.ptype_plural, self.format)

        data = requests.get(url).json()
        return [Parliamentarian(depute[self.ptype], self) for depute in data[self.ptype_plural]]

    @memoize
    def search_parliamentarians(self, q: str, field: str = 'nom', limit: int = None, no_score: bool = True):
        """
        Finds a parliamentarian based on query `q` and attribute `field` in the list of parliamentarians.

        Parameters
        ----------
        q: str
            A string close to a substring of `field`.
        field: str
            A field (attribute) in the Parliamentarian objects returned by function self.parliamentarians().
            (default: nom)
        limit: Choice([int, None])
             If None, return only the first parliamentarian. Number of parliamentarians to return. (default: None)
        no_score: bool
            If True: Do not return the score of each parliamentarian in the search function. (default: True)

        Returns
        -------
        List[Parliamentarian] or Parliamentarian
            Depending on the `limit` parameter, returns a list of Parliamentarian objects with size `limit` or just
            one Parliamentarian object.
        """
        # extractBests applies distortions on q to see if it can match some elements in parliamentarians
        # based on their `field` attribute. It also returns a score to each result
        # that tells how bad the distortion was to get that result.
        extracted = extractBests(q, self.parlementarians(),
                                 processor=lambda x: x.__dict__[field] if isinstance(x, Parliamentarian) else x,
                                 limit=limit or 1)
        # extracted is a list of couples (Parliamentarian, score)
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