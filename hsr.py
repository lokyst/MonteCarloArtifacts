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
non_5star_exp_per_run = 5.00*base_exp_gain['4*']
n_5stars_per_run = 2.1

##########################################
# Sanity Checks
##########################################
def SubStat_Probabilities(subStats):
    subStat_Probabilities = {}
    for subStat in subStats:
        sumOfWeights = 0
        for subStat2 in subStats:
            sumOfWeights += subStat_Weights[subStat2]
        subStat_Probabilities[subStat] = subStat_Weights[subStat] / sumOfWeights
    return subStat_Probabilities

# Must sum to 1
for key in slotInfo:
    print(key, sum(slotInfo[key]['mainstat_probabilities']))

subStat_Probabilities = SubStat_Probabilities(subStat_Weights)
for key in subStat_Probabilities:
    print('%4s %.4f' % (key, subStat_Probabilities[key]))


##########################################
# Filter Sets
##########################################
# Inspired by this post
'''
Personally, I think the strategy should be divided into 3 groups:
Flower/Plume
For these pieces, it’s okay to be have higher expectations since their main stats are 
guaranteed.
Sand/Goblet
These can have lower expectations since it’s already difficult to get the main stats 
that we want.
Circlet
This is where expectations should be the lowest.
I also stopped counting crit value and go with roll value instead.
How I calculate roll value:
If it starts with 3 substats, assign 0/8. If it starts with 4 substats, assign 0/9.
Then I calculate how many substats at +0 rolled into stats that I want. E.g. I want crit
rate, crit dmg, atk% and ER. The artifact has crit rate, ER, and HP%. This would be 2/8 
roll value.
If 1/8, level it up to +4.
Trash every 0/8, 1/8, 0/9, and 1/9 plume/flower at this stage. For sand/goblet/circlet, 
I’ll keep it if the main stats matches.
Then I’ll compare it with my existing piece.
If I don’t have existing piece, level it up all the way to +20. If I have existing 
piece, I’ll judge how likely the new piece will have higher roll value compared to the 
existing piece. E.g. if I have a +20 2/8 and +4 2/8, I’ll level the +4 all the way to 
+20. Worst case scenario I’ll have a second piece with the same roll value. Then 
whichever has lesser number can be a fodder.
This way I can upgrade my char little by little. From 2/8 to 3/8, 4/8, then 5/8.
Most of the time, I stop at 3/8 for circlet, 4/8 for sand/goblet, and 5/8 for 
flower/plume. They’re good enough to clear spiral abyss.

From <https://www.reddit.com/r/GenshinImpactTips/comments/xwbvrb/guide_to_choose_which_artifact_keep_and_level_up/> 
'''

# Filters at +0
filters_T0 = [
    {
        # 0. Keep any artifact with CR && CD
        'f': f.Artifact_Accept_Filter,
        'p': {
            'types': ['flower', 'feather', 'sands', 'goblet', 'circlet'],
            'mainstats': [
                'hp', 'atk', 'def', 'hpp', 'atkp', 'defp', 'er', 'em', 'cr',
                'cd', 'dmgp', 'hb'
            ],
            'substats': ['cr', 'cd'],
            'substat_matches': 2,
        }
    },
    {
        # 1. Keep any circlet, sands, or goblet with mainstat em
        'f': f.Artifact_Accept_Filter,
        'p': {
            'types': ['circlet', 'sands', 'goblet'],
            'mainstats': ['em'],
            'substats': [],
            'substat_matches': 0,
        },
    },
    {
        # 2. Keep any circlet with mainstat of either CR || CD
        'f': f.Artifact_Accept_Filter,
        'p': {
            'types': ['circlet'],
            'mainstats': ['cr', 'cd'],
            'substats': [],
            'substat_matches': 0,
        }
    },
    {
        # 3. Keep any sands with atkp or er
        'f': f.Artifact_Accept_Filter,
        'p': {
            'types': ['sands'],
            'mainstats': ['atkp', 'er'],
            'substats': ['cr', 'cd', 'er', 'em', 'atkp'],
            'substat_matches': 0,
        },
    },
    {
        # 4. Keep any goblet with dmgp
        'f': f.Artifact_Accept_Filter,
        'p': {
            'types': ['goblet'],
            'mainstats': ['dmgp'],
            'substats': ['cr', 'cd', 'er', 'em', 'atkp'],
            'substat_matches': 0,
        },
    },
    {
        # 5. Keep any sand, circlet or goblet with hpp, defp, atkp and at least one crit stat
        'f': f.Artifact_Accept_Filter,
        'p': {
            'types': ['sands', 'goblet', 'circlet'],
            'mainstats': ['hpp', 'defp', 'atkp'],
            'substats': ['cr', 'cd'],
            'substat_matches': 1,
        },
    },
    {
        # 6. Keep any flower or feather with at least one crit stat
        'f': f.Artifact_Accept_Filter,
        'p': {
            'types': ['flower', 'feather'],
            'mainstats': ['hp', 'atk'],
            'substats': ['cr', 'cd'],
            'substat_matches': 1,
        },
    },
]

# Tighten Filters at +4
filters_T1 = copy.deepcopy(filters_T0)
# 0. No change. Let's see if we get lucky at +8
# 1. No change. EM is a rare mainstat and chars built around EM often do not care about other stats
# 2. No change. CR and CD are rare main stats.
# 3. Keep any sands with atkp or er and at least 1 desireable stat
filters_T1[3]['p']['substat_matches'] = 1
# 4. Keep any goblet with dmgp and at least 1 crit stat
filters_T1[4]['p']['substats'] = ['cr', 'cd']
filters_T1[4]['p']['substat_matches'] = 1
# 5. Keep any sand, circlet or goblet with hpp, defp, atkp and CR && CD
filters_T1[6]['p']['substats'] = ['cr', 'cd']
filters_T1[5]['p']['substat_matches'] = 2
# 6. Keep any flower or feather with CR && CD
filters_T1[6]['p']['substats'] = ['cr', 'cd']
filters_T1[6]['p']['substat_matches'] = 2

# Rollcount filters
filters_T2 = copy.deepcopy(filters_T0)
for filter in filters_T2:
    filter.update({'f': f.Artifact_Rollcount_Filter})
    filter['p'].update({'substats': ['atkp', 'er', 'em', 'cr', 'cd']})
    filter['p'].update({'min_roll_count': 3})

# Rejection filters
filters_exclude = [
    {
        # 0. Reject any artifact with two flat stats
        'f': f.Artifact_Reject_Filter,
        'p': {
            'types': ['flower', 'feather', 'sands', 'goblet', 'circlet'],
            'mainstats': [
                'hp', 'atk', 'def', 'hpp', 'atkp', 'defp', 'er', 'em', 'cr',
                'cd', 'dmgp', 'hb'
            ],
            'substats': ['hp', 'def', 'atk'],
            'starting_substat_lines': 3,
            'substat_matches': 2,
        }
    },
]

#filters_exclude = []