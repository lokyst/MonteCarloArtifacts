import filter as f
import copy

#https://www.reddit.com/r/HonkaiStarRail/comments/15f52to/relics_mainstats_and_substats_probability/

slotType = ['head', 'hands', 'body', 'feet', 'sphere', 'rope']

# Mainstats info for slots
slotInfo = {
    'head': {
        'type': 'head',
        'mainstats': ['hp'],
        'mainstat_probabilities': [1.0],
    },
    'hands': {
        'type': 'hands',
        'mainstats': ['atk'],
        'mainstat_probabilities': [1.0],
    },
    'body': {
        'type': 'body',
        'mainstats': ['hpp', 'atkp', 'defp', 'ehr', 'ohb', 'cr', 'cd'],
        'mainstat_probabilities': [0.1911, 0.2003, 0.1945, 0.1040, 0.0972, 0.1084, 0.1045],
    },
    'feet': {
        'type': 'feet',
        'mainstats': ['hpp', 'atkp', 'defp', 'spd'],
        'mainstat_probabilities': [0.2784, 0.3006, 0.2995, 0.1215],
    },
    'sphere': {
        'type': 'sphere',
        'mainstats': ['hpp', 'atkp', 'defp', 'edmg'],
        'mainstat_probabilities': [0.1180, 0.1267, 0.1168, 0.6385],
    },
    'rope': {
        'type': 'rope',
        'mainstats': ['hpp', 'atkp', 'defp', 'be', 'err'],
        'mainstat_probabilities': [0.2730, 0.2774, 0.2360, 0.1568, 0.0568],
    }
}

# Substat info
subStat_Weights = {
    'hp': 6,
    'atk': 6,
    'def': 6,
    'hpp': 6,
    'atkp': 6,
    'defp': 6,
    'be': 5,
    'ehr': 5,
    'eres': 5,
    'cr': 4,
    'cd': 4,
    'spd': 3,
}

exp_level_info = {
    '5*' : [
        560,
        800,
        1040,
        1360,
        1680,
        2060,
        2640,
        3240,
        4120,
        5120,
        6350,
        8030,
        10320,
        12960,
        15720,
    ]
}

base_exp_gain = {
    '1*': 0,
    '2*': 300,
    '3*': 500,
    '4*': 1000,
    '5*': 1500,
}

artifact_max_level = 15
artifact_substat_level_increment = 3

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
