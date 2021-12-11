[![Build Status](https://travis-ci.org/regardscitoyens/cpc-api.svg)](https://travis-ci.org/regardscitoyens/cpc-api)

# CPC-API
A python client to make calls to the API from http://nosdeputes.fr and http://nossenateurs.fr. These websites
contain activity information of the French National Assembly parliamentarians (votes, etc.). 
Results are formatted as relational objects. See this example, requesting votes of our *Mélenchon national*... and we can even show his face!
:

```python
from cpc_api import CPCApi
import matplotlib.pyplot as plt  # this is to show Meluche's face

api = CPCApi(legislature='2017-2022')
meluche = api.search_parliamentarians('Melenchon')
lst_votes_meluche = meluche.get_votes()
print(lst_votes_meluche[0].balloting.titre)

arr_face_de_meluche = api.picture(meluche.slug, pixels=512)
plt.imshow(arr_face_de_meluche)
plt.show()
```

## Features

- Request Parliamentarians, Votes, Balloting, etc. and manipulate them as relational objects;
- (todo) Store locally the database for faster API interactions and less bandwidth consumption;

## Installation


Clone the current repository then go in the root directory and simply run

    pip install .

## Contribute


- If you find any issue, just raise one on the github repo! (or contact me directly here: https://discord.gg/BhruTKKx93)
- Contributions to the documentation are very welcome;
- Any other contribution is also welcome.

## Credits

- This code have been forked from https://github.com/regardscitoyens/cpc-api.
- All the data comes from the API provided by **Regards Citoyens**. See full API documentation here: https://github.com/regardscitoyens/nosdeputes.fr/blob/master/doc/api.md


## Examples

 * Députes

```python
from cpc_api import CPCApi

api = CPCApi(legislature='2012-2017')
# synthese of legislature
synthese = api.synthese()
# search for a depute
cope = api.search_parliamentarians('Cope')
# get all info of cope
all_info = api.parliamentarian(cope['slug'])
```

 * Sénateurs & députés legislature 2007-2012...

```python
from cpc_api import CPCApi

# do the same with senateurs
api = CPCApi(ptype='senateur')
larcher = api.search_parliamentarians('larcher')
# 'or with legislature 2007-2012'
api = CPCApi(ptype='depute', legislature='2007-2012')
morano = api.search_parliamentarians('morano')
# ...
```
