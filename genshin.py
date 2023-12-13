import filter as f
import copy

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
        3000, #1
        3725, #2
        4425, #3
        5150, #4
        5900, #5
        6675, #6
        7500, #7
        8350, #8
        9225, #9
        10125, #10
        11050, #11
        12025, #12
        13025, #13
        15150, #14
        17600, #15
        20375, #16
        23500, #17
        27050, #18
        31050, #19
        35575, #20
    ]
}

base_exp_gain = {
    '1*': 420,
    '2*': 840,
    '3*': 1260,
    '4*': 2520,
    '5*': 3780,
}

rolls_by_level = {
    0: {
        3: 3,
        4: 4,             
    },
    4: {
        3: 4,
        4: 5,             
    },
    8: {
        3: 5,
        4: 6,             
    },
    12: {
        3: 6,
        4: 7,             
    },
    16: {
        3: 7,
        4: 8,             
    },
    20: {
        3: 8,
        4: 9,             
    },
}

artifact_max_level = 20
artifact_substat_level_increment = 4
artifact_max_lines = 4
non_5star_exp_per_run = 3.55*base_exp_gain['3*'] + 2.48*base_exp_gain['4*']
n_5stars_per_run = 1.07

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

debug = False
if debug:
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
filters = {}
filters.update({0: {
    0: {
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
    1: {
        # 1. Keep any circlet, sands, or goblet with mainstat em
        'f': f.Artifact_Accept_Filter,
        'p': {
            'types': ['circlet', 'sands', 'goblet'],
            'mainstats': ['em'],
            'substats': ['cr', 'cd', 'er', 'em', 'atkp'],
            'substat_matches': 0,
        },
    },
    2: {
        # 2. Keep any circlet with mainstat of either CR || CD
        'f': f.Artifact_Accept_Filter,
        'p': {
            'types': ['circlet'],
            'mainstats': ['cr', 'cd'],
            'substats': ['cr', 'cd', 'er', 'em', 'atkp'],
            'substat_matches': 0,
        }
    },
    3: {
        # 3. Keep any sands with atkp or er
        'f': f.Artifact_Accept_Filter,
        'p': {
            'types': ['sands'],
            'mainstats': ['atkp', 'er'],
            'substats': ['cr', 'cd', 'er', 'em', 'atkp'],
            'substat_matches': 0,
        },
    },
    4: {
        # 4. Keep any goblet with dmgp
        'f': f.Artifact_Accept_Filter,
        'p': {
            'types': ['goblet'],
            'mainstats': ['dmgp'],
            'substats': ['cr', 'cd', 'er', 'em', 'atkp'],
            'substat_matches': 0,
        },
    },
    5: {
        # 5. Keep any sand, circlet or goblet with hpp, defp, atkp and at least one crit stat
        'f': f.Artifact_Accept_Filter,
        'p': {
            'types': ['sands', 'goblet', 'circlet'],
            'mainstats': ['hpp', 'defp', 'atkp'],
            'substats': ['cr', 'cd'],
            'substat_matches': 1,
        },
    },
    6: {
        # 6. Keep any flower or feather with at least one crit stat
        'f': f.Artifact_Accept_Filter,
        'p': {
            'types': ['flower', 'feather'],
            'mainstats': ['hp', 'atk'],
            'substats': ['cr', 'cd'],
            'substat_matches': 1,
        },
    },
}})

# Tighten Filters at +4
filters.update({4: copy.deepcopy(filters[0])})
# 0. No change. Let's see if we get lucky at +8
# 1. No change. EM is a rare mainstat and chars built around EM often do not care about other stats
# 2. No change. CR and CD are rare main stats.
# 3. Keep any sands with atkp or er and at least 1 desireable stat
filters[4][3]['p']['substat_matches'] = 1
# 4. Keep any goblet with dmgp and at least 1 crit stat
filters[4][4]['p']['substats'] = ['cr', 'cd']
filters[4][4]['p']['substat_matches'] = 1
# 5. Keep any sand, circlet or goblet with hpp, defp, atkp and 2 rolls into CR or CD
filters[4][5]['p']['substats'] = ['cr', 'cd']
filters[4][5]['p']['substat_matches'] = 2
# 6. Keep any flower or feather with 2 rolls into CR or CD
filters[4][6]['p']['substats'] = ['cr', 'cd']
filters[4][6]['p']['substat_matches'] = 2

'''
Assuming only CR & CD are desireable:
- the absolute best we can get at +20 is 6/8 or 7/9
- therefore the best we can get at +12 is 4/8 or 5/9
- therefore the best we can get at +8 is 3/8 or 4/9
'''
# Rollcount filters
filters.update({12: copy.deepcopy(filters[0])})
for artifact_filter in filters[12].values():
    artifact_filter['f'] = f.Artifact_Rollcount_Filter
    artifact_filter['p'].update({'substats': ['cr', 'cd', 'er', 'em', 'atkp']})
    #filter['p'].update({'substats': ['cr', 'cd']})
    artifact_filter['p'].update({'min_roll_count': 5})

# Rejection filters
filters_exclude = {}
filters_exclude.update({0: {
    0: {
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
}})

filters_exclude.update({4: copy.deepcopy(filters_exclude[0])})
filters_exclude.update({12: copy.deepcopy(filters_exclude[0])})

#filters_exclude = []

# Tiers
tiers = list(filters.keys())