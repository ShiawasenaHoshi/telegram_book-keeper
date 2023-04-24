import os

import matplotlib.pyplot as plt
import numpy as np

from config import Config


def expenses_pie(expenses):
    y = np.array([e["percentage"] if e["percentage"] >= 1.2 else 1.2 for e in expenses.values()])
    mylabels = [f"{e['percentage'] if e['percentage'] > 0 else '<0.1'}% {e['description']}" for e in expenses.values()]

    cmap = plt.get_cmap('Paired')
    colors = cmap(np.linspace(0, 1, len(expenses.values())))
    myexplode = [0.1 for i in range(len(mylabels))]

    plt.pie(y, labels=mylabels, explode=myexplode, colors=colors, normalize=True)
    ax = plt.gca()
    # plt.legend(bbox_to_anchor=(1.0, 1.1), bbox_transform=ax.transAxes, title="Траты")
    file_path = os.path.join(Config.TEMP_FOLDER, f'expenses_chart.png')
    plt.savefig(file_path)
    plt.close()
    return file_path
