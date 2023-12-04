from numpy.random import choice
import contextlib
import copy
import genshin as g

# Get list of equip slot names
slotType = g.slotType
# Get dict of possible mainstats and probabilities for slots
slotInfo = g.slotInfo
# Get list of possible substats
subStats = list(g.subStat_Weights.keys())
# Get dict of substat weights
subStat_Weights = g.subStat_Weights

# Substats are weighted without replacement
def SubStat_Probabilities(subStats):
    subStat_Probabilities = {}
    for subStat in subStats:
        sumOfWeights = 0
        for subStat2 in subStats:
            sumOfWeights += subStat_Weights[subStat2]
        subStat_Probabilities[
            subStat] = subStat_Weights[subStat] / sumOfWeights
    return subStat_Probabilities


##########################################
# Define Artifact class
##########################################
class Artifact:

    def __init__(
        self,
        artifact_type=None,
        artifact_set=None,
        artifact_mainstat=None,
        artifact_substats=None,
        artifact_max_lines=None,
        artifact_level = None,
        artifact_max_level = None,
        artifact_substat_level_increment = None,
    ):
        self.artifact_type = artifact_type or 'flower'
        self.artifact_set = artifact_set
        self.artifact_mainstat = artifact_mainstat or 'hp'

        if isinstance(artifact_substats, list):
            tempDict = {}
            for item in artifact_substats:
                tempDict.update({item: {'rollCount': 1, 'rollValue': 0}})
            self.artifact_substats = tempDict
        elif isinstance(artifact_substats, dict):
            self.artifact_substats = artifact_substats
        else:
            self.artifact_substats = {}

        if len(self.artifact_substats.keys()) == 0:
            self.artifact_lines = 3
        else:
            self.artifact_lines = len(self.artifact_substats.keys())

        self.artifact_max_lines = artifact_max_lines or 4
        self.artifact_level = artifact_level or 0
        self.artifact_max_level = artifact_max_level or 20
        self.artifact_substat_level_increment = artifact_substat_level_increment or 4

    def __str__(self):
        return f"Type: '{self.artifact_type}' Main: '{self.artifact_mainstat}' Lvl : '{self.artifact_level}' Subs: {self.artifact_substats}"

    def Generate_Mainstat(self):
        # Randomly choose a mainstat based on the slot
        # Todo: Add check that artifact type is not None
        artifact_mainstat = choice(
            slotInfo[self.artifact_type]['mainstats'],
            p=slotInfo[self.artifact_type]['mainstat_probabilities'])
        self.artifact_mainstat = artifact_mainstat

    def Generate_Substats(self):
        # Generate random artifact substats based on slot and mainstat

        # Remove mainstat from substat pool if applicable
        subStat_Pool = subStats.copy()
        with contextlib.suppress(ValueError):
            subStat_Pool.remove(self.artifact_mainstat)

        # Randomly generate substats based on sampling from substat pool without replacement
        artifact_substats = {}
        for i in range(self.artifact_lines):
            subStat_probabilities = SubStat_Probabilities(subStat_Pool)
            artifact_subStat = choice(subStat_Pool,
                                      p=list(subStat_probabilities.values()))
            # Initialize rollCount and rollValue
            artifact_substats[artifact_subStat] = {
                'rollCount': 1,
                'rollValue': 0,
            }
            # Remove substat from pool
            subStat_Pool.remove(artifact_subStat)

        # Replace self.artifact_substats
        self.artifact_substats.clear()
        self.artifact_substats.update(artifact_substats)

    def Add_Substat(self):
        # Generate random artifact substat based on slot and mainstat up to maxlines

        if len(self.artifact_substats.keys()) >= self.artifact_max_lines:
            return

        # Remove mainstat from substat pool if applicable
        subStat_Pool = subStats.copy()
        with contextlib.suppress(ValueError):
            subStat_Pool.remove(self.artifact_mainstat)

        # Remove existing substats from the substat pool
        for subStat in self.artifact_substats.keys():
            with contextlib.suppress(ValueError):
                subStat_Pool.remove(subStat)

        # Randomly generate substat based on sampling from substat pool without replacement
        artifact_substats = self.artifact_substats
        subStat_probabilities = SubStat_Probabilities(subStat_Pool)
        artifact_subStat = choice(subStat_Pool,
                                  p=list(subStat_probabilities.values()))
        # Initialize rollCount and rollValue
        artifact_substats.update(
            {artifact_subStat: {
                'rollCount': 1,
                'rollValue': 0,
            }})

        # Remove substat from pool
        subStat_Pool.remove(artifact_subStat)

        # Update self.artifact_substats
        self.artifact_substats.update(artifact_substats)

    def Increment_Substat(self, n_increments=1):
        # Increment a random artifact substat

        for _ in range(n_increments):
            # Randomly select existing substat based on uniform distribution
            substat_Pool = list(self.artifact_substats.keys())
            artifact_subStat = choice(substat_Pool)
            # Increment rollCount and rollValue
            self.artifact_substats[artifact_subStat]['rollCount'] += 1
            self.artifact_substats[artifact_subStat]['rollValue'] += 0

    def Level_Artifact(self, increment):
        # Level artifact by increment up to artifact_max_level

        # Return if already at max level
        if self.artifact_level >= self.artifact_max_level:
            return

        # Record start and end states because we need to count how many substat increments occurred
        start_level = self.artifact_level
        final_level = start_level + increment

        # Fix hardcoded substat level increment
        substat_increments = final_level // self.artifact_substat_level_increment - start_level // self.artifact_substat_level_increment
        self.Increment_Substat(n_increments=substat_increments)

        for _ in range(substat_increments):
            if len(self.artifact_substats.keys()) < self.artifact_max_lines:
                self.Add_Substat()
            else:
                self.Increment_Substat()

        self.artifact_level = min(final_level, self.artifact_max_level)

    def random(self, slotpool=None):
        # Generate a random artifact

        # Randomly choose a slot assuming equal probabilities for all slots
        slot_Pool = slotpool or slotType.copy()
        slot_Probabilities = [1 / len(slot_Pool)] * len(slot_Pool)
        artifact_Slot = choice(slot_Pool, p=slot_Probabilities)
        self.artifact_type = artifact_Slot

        # Randomly choose a set assuming equal probabilities for all sets
        self.artifact_set = None

        # Randomly choose the number of substat lines assuming a 5* artifact
        # TODO: Make this more generic
        self.artifact_lines = choice([3, 4], p=[0.80, 0.20])

        # Generate artifact mainstat and substats
        self.artifact_mainstat = None
        self.artifact_substats.clear()
        self.Generate_Mainstat()
        self.Generate_Substats()

    def print(self):
        print('Set: %s' % self.artifact_set)
        print('Slot: %s' % self.artifact_type)
        print('MainStat: %s ' % self.artifact_mainstat)
        print('Level: %s' % self.artifact_level)
        for i in self.artifact_substats.keys():
            print('SubStat: %s cnt: %s' %
                  (i, self.artifact_substats[i]['rollCount']))
        print('')

    def get_substat_lines(self):
        return self.artifact_lines

    def get_substat_list(self):
        return self.artifact_substats.keys()


##########################################
# Evaluate generated Artifacts against a filter and see how many meet criteria
##########################################
def Artifact_Accept_Filter(artifact, filter):
    # Returns True if artifact matches filter

    s_isect = set(filter['substats']).intersection(
        set(artifact.get_substat_list()))

    if artifact.artifact_type in filter[
            'types'] and artifact.artifact_mainstat in filter[
                'mainstats'] and len(s_isect) >= filter['substat_matches']:
        return True

    return False


def Artifact_Reject_Filter(artifact, filter):
    # Returns True if artifact matches filter

    s_isect = set(filter['substats']).intersection(
        set(artifact.get_substat_list()))

    if artifact.artifact_type in filter[
            'types'] and artifact.artifact_mainstat in filter[
                'mainstats'] and len(s_isect) >= filter['substat_matches']:
        return True

    return False


def Artifact_Rollcount_Filter(artifact, filter):
    # Returns True if total roll count for specified stats meets or exceeds minimum

    rcnt = 0

    for s in filter['substats']:
        with contextlib.suppress(KeyError):
            rcnt += artifact.artifact_substats[s]['rollCount']

    if artifact.artifact_type in filter[
            'types'] and artifact.artifact_mainstat in filter[
                'mainstats'] and rcnt >= filter['min_roll_count']:
        return True

    return False


def Keep_Artifact(artifact, inclusion_filters, exclusion_filters, debug=False):
    # Returns True if artifact matches any inclusion filter, and does not match any exclusion filter
    # Rejection filters will override inclusion

    state = False
    for i in range(len(inclusion_filters)):
        if inclusion_filters[i]['f'](artifact, inclusion_filters[i]['p']):
            state = True
            if debug:
                print('Accepted: Rule %i' % i)
            break

    if not state and debug:
        print('Rejected: No matches')

    # Exclusion will always override
    for j in range(len(exclusion_filters)):
        if exclusion_filters[j]['f'](artifact, exclusion_filters[j]['p']):
            state = False
            if debug:
                print('Rejected: Rule %i' % j)
            break

    return state


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
filters_0 = [
    {
        # 0. Keep any artifact with CR && CD
        'f': Artifact_Accept_Filter,
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
        'f': Artifact_Accept_Filter,
        'p': {
            'types': ['circlet', 'sands', 'goblet'],
            'mainstats': ['em'],
            'substats': [],
            'substat_matches': 0,
        },
    },
    {
        # 2. Keep any circlet with mainstat of either CR || CD
        'f': Artifact_Accept_Filter,
        'p': {
            'types': ['circlet'],
            'mainstats': ['cr', 'cd'],
            'substats': [],
            'substat_matches': 0,
        }
    },
    {
        # 3. Keep any sands with atkp or er
        'f': Artifact_Accept_Filter,
        'p': {
            'types': ['sands'],
            'mainstats': ['atkp', 'er'],
            'substats': ['cr', 'cd', 'er', 'em', 'atkp'],
            'substat_matches': 0,
        },
    },
    {
        # 4. Keep any goblet with dmgp
        'f': Artifact_Accept_Filter,
        'p': {
            'types': ['goblet'],
            'mainstats': ['dmgp'],
            'substats': ['cr', 'cd', 'er', 'em', 'atkp'],
            'substat_matches': 0,
        },
    },
    {
        # 5. Keep any sand, circlet or goblet with hpp, defp, atkp and at least one crit stat
        'f': Artifact_Accept_Filter,
        'p': {
            'types': ['sands', 'goblet', 'circlet'],
            'mainstats': ['hpp', 'defp', 'atkp'],
            'substats': ['cr', 'cd'],
            'substat_matches': 1,
        },
    },
    {
        # 6. Keep any flower or feather with at least one crit stat
        'f': Artifact_Accept_Filter,
        'p': {
            'types': ['flower', 'feather'],
            'mainstats': ['hp', 'atk'],
            'substats': ['cr', 'cd'],
            'substat_matches': 1,
        },
    },
]

# Tighten Filters at +4
filters_4 = copy.deepcopy(filters_0)
# 0. No change. Let's see if we get lucky at +8
# 1. No change. EM is a rare mainstat and chars built around EM often do not care about other stats
# 2. No change. CR and CD are rare main stats.
# 3. Keep any sands with atkp or er and at least 1 desireable stat
filters_4[3]['p']['substat_matches'] = 1
# 4. Keep any goblet with dmgp and at least 1 crit stat
filters_4[4]['p']['substats'] = ['cr', 'cd']
filters_4[4]['p']['substat_matches'] = 1
# 5. Keep any sand, circlet or goblet with hpp, defp, atkp and CR && CD
filters_4[6]['p']['substats'] = ['cr', 'cd']
filters_4[5]['p']['substat_matches'] = 2
# 6. Keep any flower or feather with CR && CD
filters_4[6]['p']['substats'] = ['cr', 'cd']
filters_4[6]['p']['substat_matches'] = 2

# Rollcount filters
filters_12 = copy.deepcopy(filters_0)
for filter in filters_12:
    filter.update({'f': Artifact_Rollcount_Filter})
    filter['p'].update({'substats': ['atkp', 'er', 'em', 'cr', 'cd']})
    filter['p'].update({'min_roll_count': 3})

# Rejection filters
filters_exclude = [
    {
        # 0. Reject any artifact with two flat stats
        'f': Artifact_Reject_Filter,
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

##########################################
# Simulation
##########################################
nSuccess_0 = 0
nSuccess_4 = 0
nSuccess_12 = 0
trials = 1000

artifact_exp_consumed = 0
artifact_exp_gained = 0
artifact_exp_by_level = g.exp_level_info['5*']

lvl_0_exp_gained = g.base_exp_gain['5*']
lvl_4_exp_gained = lvl_0_exp_gained + sum(artifact_exp_by_level[:4]) * 0.8
lvl_12_exp_gained = lvl_0_exp_gained + sum(artifact_exp_by_level[:12]) * 0.8

# Generate Random Artifact
artifact = Artifact(artifact_max_level=g.artifact_max_level, artifact_substat_level_increment=g.artifact_substat_level_increment)

for i in range(trials):
    artifact.random()
    #artifact = Artifact('feather', None, 'atk', ['hp', 'cr', 'hpp'])
    #print(artifact)
    #artifact.print()
    lvl_start = 0
    lvl_end = 0

    if Keep_Artifact(artifact, filters_0, filters_exclude):
        nSuccess_0 += 1

        # +4
        artifact.Level_Artifact(artifact.artifact_substat_level_increment)
        #artifact.print()
        lvl_end = lvl_start + artifact.artifact_substat_level_increment
        artifact_exp_consumed += sum(artifact_exp_by_level[lvl_start:lvl_end])
        lvl_start = lvl_end

        if Keep_Artifact(artifact, filters_4, filters_exclude):
            nSuccess_4 += 1

            # +8
            artifact.Level_Artifact(artifact.artifact_substat_level_increment)
            lvl_end = lvl_start + artifact.artifact_substat_level_increment
            artifact_exp_consumed += sum(artifact_exp_by_level[lvl_start:lvl_end])
            lvl_start = lvl_end

            # +12
            artifact.Level_Artifact(artifact.artifact_substat_level_increment)
            #artifact.print()
            lvl_end = lvl_start + artifact.artifact_substat_level_increment
            artifact_exp_consumed += sum(artifact_exp_by_level[lvl_start:lvl_end])
            lvl_start = lvl_end

            if Keep_Artifact(artifact, filters_12, []):
                nSuccess_12 += 1

                # +16
                artifact.Level_Artifact(artifact.artifact_substat_level_increment)
                lvl_end = lvl_start + artifact.artifact_substat_level_increment
                artifact_exp_consumed += sum(artifact_exp_by_level[lvl_start:lvl_end])
                lvl_start = lvl_end

                # +20
                artifact.Level_Artifact(artifact.artifact_substat_level_increment)
                #artifact.print()
                lvl_end = lvl_start + artifact.artifact_substat_level_increment
                artifact_exp_consumed += sum(artifact_exp_by_level[lvl_start:lvl_end])
                lvl_start = lvl_end
            
            else:
                artifact_exp_gained += lvl_12_exp_gained

        else:
            artifact_exp_gained += lvl_4_exp_gained

    else:
        artifact_exp_gained += lvl_0_exp_gained

print('0: %s %s' % (nSuccess_0, nSuccess_0 / trials))
print('4: %s %s' % (nSuccess_4, nSuccess_4 / trials))
print('12: %s %s' % (nSuccess_12, nSuccess_12 / trials))
print('Artifact Exp Used: %i' % artifact_exp_consumed)
print('Artifact Exp Gained (5stars only): %i' % artifact_exp_gained)

non_5star_exp_per_run = 10722.6
n_5stars_per_run = 1.07
n_runs = trials/n_5stars_per_run
non_5star_exp_gained = n_runs * non_5star_exp_per_run
print('Non 5 Star Exp Gained: %i' % non_5star_exp_gained)
print('Total Exp Gained: %i' % (non_5star_exp_gained + artifact_exp_gained))
exp_surplus = non_5star_exp_gained + artifact_exp_gained - artifact_exp_consumed
print('Exp Surplus: %i' % exp_surplus)
print('Exp lost from foddering Lvl_0: %i' % ((trials-nSuccess_0)*lvl_0_exp_gained))