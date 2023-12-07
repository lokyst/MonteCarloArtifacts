from numpy.random import choice
import copy
import contextlib
import genshin as g
import filter as f

# Get list of equip slot names
slotType = g.slotType
# Get dict of possible mainstats and probabilities for slots
slotInfo = g.slotInfo
# Get list of possible substats
subStats = list(g.subStat_Weights.keys())
# Get dict of substat weights
subStat_Weights = g.subStat_Weights



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
        for i in range(self.artifact_lines):
            self.Add_Substat()

    def Add_Substat(self):
        # Generate random artifact substat based on slot and mainstat up to maxlines

        if len(self.artifact_substats.keys()) >= self.artifact_max_lines:
            return

        # Remove mainstat from substat pool if applicable
        subStat_Pool = copy.deepcopy(subStat_Weights)
        with contextlib.suppress(KeyError):
            subStat_Pool.pop(self.artifact_mainstat)

        # Remove existing substats from the substat pool
        for subStat in self.artifact_substats.keys():
            with contextlib.suppress(KeyError):
                subStat_Pool.pop(subStat)

        # Randomly generate substat based on sampling from substat pool without replacement
        artifact_substats = self.artifact_substats
        subStat_probabilities = self.SubStat_Probabilities_From_Weights(subStat_Weights)
        artifact_subStat = choice(list(subStat_probabilities.keys()),
                                  p=list(subStat_probabilities.values()))
        # Initialize rollCount and rollValue
        artifact_substats.update(
            {artifact_subStat: {
                'rollCount': 1,
                'rollValue': 0,
            }})

        # Remove substat from pool
        with contextlib.suppress(KeyError):
            subStat_Pool.pop(artifact_subStat)

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

    # Weighted substats without replacement
    def SubStat_Probabilities_From_Weights(self, substat_weights):
        subStat_Probabilities = {}
        substats = list(substat_weights.keys())
        for subStat in substats:
            sumOfWeights = 0
            for subStat2 in substats:
                sumOfWeights += substat_weights[subStat2]
            subStat_Probabilities[subStat] = substat_weights[subStat] / sumOfWeights
        return subStat_Probabilities



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

    if f.Keep_Artifact(artifact, g.filters_0, g.filters_exclude):
        nSuccess_0 += 1

        # +4
        artifact.Level_Artifact(artifact.artifact_substat_level_increment)
        #artifact.print()
        lvl_end = lvl_start + artifact.artifact_substat_level_increment
        artifact_exp_consumed += sum(artifact_exp_by_level[lvl_start:lvl_end])
        lvl_start = lvl_end

        if f.Keep_Artifact(artifact, g.filters_4, g.filters_exclude):
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

            if f.Keep_Artifact(artifact, g.filters_12, []):
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