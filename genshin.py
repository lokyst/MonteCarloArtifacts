slotType = ['flower', 'feather', 'sands', 'goblet', 'circlet']

# Mainstats info for slots
slotInfo = {
    'flower': {
        'type': 'flower',
        'mainstats': ['hp'],
        'mainstat_probabilities': [1.0],
    },
    'feather': {
        'type': 'feather',
        'mainstats': ['atk'],
        'mainstat_probabilities': [1.0],
    },
    'sands': {
        'type': 'sands',
        'mainstats': ['hpp', 'atkp', 'defp', 'er', 'em'],
        'mainstat_probabilities': [0.2668, 0.2666, 0.2666, 0.1, 0.1],
    },
    'goblet': {
        'type': 'goblet',
        'mainstats': ['hpp', 'atkp', 'defp', 'em', 'dmgp'],
        'mainstat_probabilities': [0.1925, 0.1925, 0.19, 0.025, 0.4],
    },
    'circlet': {
        'type': 'circlet',
        'mainstats': ['hpp', 'atkp', 'defp', 'em', 'cr', 'cd', 'hb'],
        'mainstat_probabilities': [0.22, 0.22, 0.22, 0.04, 0.10, 0.10, 0.10],
    }
}

# Substat info
subStat_Weights = {
    'hp': 6,
    'atk': 6,
    'def': 6,
    'hpp': 5,
    'atkp': 5,
    'defp': 5,
    'er': 4,
    'em': 4,
    'cr': 3,
    'cd': 3
}

exp_level_info = {
    '5*' : [
        3000,
        3725,
        4425,
        5150,
        5900,
        6675,
        7500,
        8350,
        9225,
        10125,
        11050,
        12025,
        13025,
        15150,
        17600,
        20375,
        23500,
        27050,
        31050,
        35575,
        
    ]
}

base_exp_gain = {
    '1*': 420,
    '2*': 840,
    '3*': 1260,
    '4*': 2520,
    '5*': 3780,
}

artifact_max_level = 20
artifact_substat_level_increment = 4

def SubStat_Probabilities(subStats):
    subStat_Probabilities = {}
    for subStat in subStats:
        sumOfWeights = 0
        for subStat2 in subStats:
            sumOfWeights += subStat_Weights[subStat2]
        subStat_Probabilities[subStat] = subStat_Weights[subStat] / sumOfWeights
    return subStat_Probabilities

for key in slotInfo:
    print(key, sum(slotInfo[key]['mainstat_probabilities']))

subStat_Probabilities = SubStat_Probabilities(subStat_Weights)
for key in subStat_Probabilities:
    print('%4s %.4f' % (key, subStat_Probabilities[key]))

