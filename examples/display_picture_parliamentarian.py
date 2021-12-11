
from cpc_api.api import CPCApi
import matplotlib.pyplot as plt


def main():
    api = CPCApi(legislature='2017-2022')
    meluche = api.search_parliamentarians('Melenchon')
    arr_face_de_meluche = api.picture(meluche.slug, pixels=512)
    plt.imshow(arr_face_de_meluche)
    plt.show()


if __name__ == "__main__":
    main()