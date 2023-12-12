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

rolls_by_level = {
    0: {
        3: 3,
        4: 4,             
    },
    3: {
        3: 4,
        4: 5,             
    },
    6: {
        3: 5,
        4: 6,             
    },
    9: {
        3: 6,
        4: 7,             
    },
    12: {
        3: 7,
        4: 8,             
    },
    15: {
        3: 8,
        4: 9,             
    },
}

artifact_max_level = 15
artifact_substat_level_increment = 3
artifact_max_lines = 4
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
# Mainstats
# ['hp', 'atk', 'hpp', 'atkp', 'defp', 'ehr', 'ohb', 'cr', 'cd', 'spd', 'edmg', 'be', 'err']
# Substats
# ['hp', 'atk', 'def', 'hpp', 'atkp', 'defp', 'be', 'ehr', 'eres', 'cr', 'cd', 'spd',]
# Filters at +0
filters = {}
filters.update({0: {
    '0': {
        # 0. Keep any artifact with 2 of CR || CD || SPD
        'f': f.Artifact_Accept_Filter,
        'p': {
            'types': ['head', 'hands', 'body', 'feet', 'sphere', 'rope'],
            'mainstats': [
                'hp', 'atk', 
                'hpp', 'atkp', 'defp', 
                'ehr', 'ohb', 'cr', 'cd', 
                'spd', 
                'edmg', 
                'be', 'err',
            ],
            'substats': ['cr', 'cd', 'spd'],
            'substat_matches': 2,
        }
    },
    '1.0': {
        # 1.0 Keep any feet with mainstat spd
        'f': f.Artifact_Accept_Filter,
        'p': {
            'types': ['feet'],
            'mainstats': ['spd'],
            'substats': ['cr', 'cd', 'atkp'],
            'substat_matches': 0,
        },
    },
    '1.1': {
        # 1.1 Keep any feet with mainstat spd
        'f': f.Artifact_Accept_Filter,
        'p': {
            'types': ['feet'],
            'mainstats': ['spd'],
            'substats': ['ehr', 'atkp', 'be'],
            'substat_matches': 0,
        },
    },
    '1.2': {
        # 1.1 Keep any feet with mainstat spd
        'f': f.Artifact_Accept_Filter,
        'p': {
            'types': ['feet'],
            'mainstats': ['spd'],
            'substats': ['eres', 'hpp', 'defp'],
            'substat_matches': 0,
        },
    },
    '2': {
        # 2. Keep any ropes with mainstat err
        'f': f.Artifact_Accept_Filter,
        'p': {
            'types': ['rope'],
            'mainstats': ['err'],
            'substats': [],
            'substat_matches': 0,
        },
    },
    '3': {
        # 3.0 Keep any ropes with mainstat be
        'f': f.Artifact_Accept_Filter,
        'p': {
            'types': ['rope'],
            'mainstats': ['be'],
            'substats': ['ehr', 'spd', 'atkp'],
            'substat_matches': 0,
        },
    },
    '4.0': {
        # 4.0 Keep any body with mainstat of either CR, CD
        'f': f.Artifact_Accept_Filter,
        'p': {
            'types': ['body'],
            'mainstats': ['cr', 'cd'],
            'substats': ['cr', 'cd', 'atkp', 'spd'],
            'substat_matches': 0,
        }
    },
    '4.1': {
        # 4.1 Keep any body with mainstat of EHR
        'f': f.Artifact_Accept_Filter,
        'p': {
            'types': ['body'],
            'mainstats': ['ehr'],
            'substats': ['spd', 'atkp', 'be'],
            'substat_matches': 0,
        }
    },
    '4.2': {
        # 4.2 Keep any body with mainstat of OHB
        'f': f.Artifact_Accept_Filter,
        'p': {
            'types': ['body'],
            'mainstats': ['ohb'],
            'substats': ['spd', 'eres'],
            'substat_matches': 0,
        }
    },
    '5.0': {
        # 5.0 Keep any feet with atkp
        'f': f.Artifact_Accept_Filter,
        'p': {
            'types': ['feet'],
            'mainstats': ['atkp'],
            'substats': ['cr', 'cd', 'spd'],
            'substat_matches': 0,
        },
    },
    '5.1': {
        # 5.1 Keep any feet with atkp
        'f': f.Artifact_Accept_Filter,
        'p': {
            'types': ['feet'],
            'mainstats': ['atkp'],
            'substats': ['spd', 'ehr', 'be'],
            'substat_matches': 0,
        },
    },
    '6.0': {
        # 6.0 Keep any sphere with edmg
        'f': f.Artifact_Accept_Filter,
        'p': {
            'types': ['sphere'],
            'mainstats': ['edmg'],
            'substats': ['cr', 'cd', 'spd'],
            'substat_matches': 0,
        },
    },
    '7.0': {
        # 7.0 Keep any body, feet, sphere, or rope with hpp, defp, atkp and at least one crit stat or spd stat
        'f': f.Artifact_Accept_Filter,
        'p': {
            'types': ['body', 'feet', 'sphere', 'rope'],
            'mainstats': ['hpp', 'defp', 'atkp'],
            'substats': ['cr', 'cd', 'spd'],
            'substat_matches': 1,
        },
    },
    '7.1': {
        # 7.1 Keep any body, feet, sphere, or rope with atkp and ehr or spd stat
        'f': f.Artifact_Accept_Filter,
        'p': {
            'types': ['body', 'feet', 'sphere', 'rope'],
            'mainstats': ['atkp'],
            'substats': ['spd', 'ehr'],
            'substat_matches': 1,
        },
    },
    '7.2': {
        # 7.2 Keep any body, feet, sphere, or rope with hpp or defp and eres or spd stat
        'f': f.Artifact_Accept_Filter,
        'p': {
            'types': ['body', 'feet', 'sphere', 'rope'],
            'mainstats': ['hpp', 'defp'],
            'substats': ['spd', 'eres'],
            'substat_matches': 1,
        },
    },
    '8.0': {
        # 8.0 Keep any hat or hands with at least one crit stat or spd stat
        'f': f.Artifact_Accept_Filter,
        'p': {
            'types': ['head', 'hands'],
            'mainstats': ['hp', 'atk'],
            'substats': ['cr', 'cd', 'spd'],
            'substat_matches': 1,
        },
    },
    '8.1': {
        # 8.1 Keep any hat or hands  with spd or ehr
        'f': f.Artifact_Accept_Filter,
        'p': {
            'types': ['head', 'hands'],
            'mainstats': ['hp', 'atk'],
            'substats': ['spd', 'ehr'],
            'substat_matches': 1,
        },
    },
    '8.2': {
        # 8.2 Keep any hat or hands with spd or eres
        'f': f.Artifact_Accept_Filter,
        'p': {
            'types': ['head', 'hands'],
            'mainstats': ['hp', 'atk'],
            'substats': ['spd', 'eres'],
            'substat_matches': 1,
        },
    },
}})

# Tighten Filters at +3 except 0, 1, 2 
filters.update({3: copy.deepcopy(filters[0])})
for artifact_filter in filters[3].values():
    artifact_filter['p']['substat_matches'] += 1
# Revert 0, 1, 2
filters[3]['0']['p']['substat_matches'] = 0    # 2 of CR | CD | SPD
filters[3]['2']['p']['substat_matches'] = 0    # ERR rope

# 1. No change. ERR/BE/SPD is a rare mainstat and chars built around ERR often do not care about other stats
# 2. No change. CR, CD and EHR are rare main stats.
# 3. Keep any feet with atkp and at least 1 desireable stat
#filters[3][3]['p']['substat_matches'] = 1
# 4. Keep any goblet with dmgp and at least 1 crit stat or spd
#filters[3][4]['p']['substat_matches'] = 1
# 5. Keep any sand, circlet or goblet with hpp, defp, atkp and CR && CD
#filters[3][5]['p']['substat_matches'] = 2
# 6. Keep any flower or feather with CR && CD
#filters[3][6]['p']['substats'] = ['cr', 'cd', 'spd']
#filters[3][6]['p']['substat_matches'] = 2
# 9. Atk% body or feet with 2 of spd/ehr/be at 3
#10. hp or def body or feet with 2 of spd/eres at 3
#11. ohb with 1 of spd or eres
#13. Orbs 1 of spd/cr/cd (eres not reqd since it's for a specific planar orb  set)
#14. HP ATK DEF rope 2 of spd/cr/cd
#15. BE rope 1 of spd/cr/cd/ehr/atk



'''
Assuming only CR & CD are desireable:
- the absolute best we can get at +15 is 6/8 or 7/9
- therefore the best we can get at +9 is 4/8 or 5/9
- therefore the best we can get at +6 is 3/8 or 4/9
'''
# Rollcount filters
filters.update({9: copy.deepcopy(filters[0])})
for artifact_filter in filters[9].values():
    artifact_filter.update({'f': f.Artifact_Rollcount_Filter})
    artifact_filter['p'].update({'min_roll_count': 5})

# Exceptions and extensions
filters[9]['2']['p']['substats'] = ['spd', 'eres', 'ehr', 'cr', 'cd'] # ERR rope
filters[9]['4.2']['p']['substats'] = ['spd', 'eres', 'hpp']  # OHB body
filters[9]['6.0']['p']['substats'] = ['cr', 'cd', 'spd', 'atkp']  # EDMG sphere
filters[9]['7.1']['p']['substats'] = ['spd', 'ehr', 'be']  # ATKP body/feet/sphere/rope
filters[9]['7.2']['p']['substats'] = ['spd', 'eres', 'hpp']  # HPP/DEFP body/feet/sphere/rope
filters[9]['8.2']['p']['substats'] = ['spd', 'eres', 'hpp']  # hat/hands

# Rejection filters
filters_exclude = {}
filters_exclude.update({0: {
    0: {
        # 0. Reject any artifact with two flat stats
        'f': f.Artifact_Reject_Filter,
        'p': {
            'types': ['head', 'hands', 'body', 'feet', 'sphere', 'rope'],
            'mainstats': [
                'hp', 'atk', 
                'hpp', 'atkp', 'defp', 
                'ehr', 'ohb', 'cr', 'cd', 
                'spd', 
                'edmg', 
                'be', 'err',
            ],
            'substats': ['hp', 'def', 'atk'],
            'starting_substat_lines': 3,
            'substat_matches': 2,
        }
    },
}})

filters_exclude.update({3: copy.deepcopy(filters_exclude[0])})
filters_exclude.update({9: copy.deepcopy(filters_exclude[0])})

#filters_exclude = []

# Tiers
tiers = list(filters.keys())