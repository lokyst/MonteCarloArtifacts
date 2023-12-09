from numpy.random import choice
import copy
import contextlib
import genshin as g
import filter as f
import check_artifact as c

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
        artifact_rarity=None,
        artifact_max_lines=None,
        artifact_level = None,
        artifact_max_level = None,
        artifact_substat_level_increment = None,
    ):
        self.artifact_type = artifact_type or 'flower'
        self.artifact_set = artifact_set
        self.artifact_mainstat = artifact_mainstat or 'hp'
        self.artifact_rarity = artifact_rarity or '5*'

        if isinstance(artifact_substats, list):
            tempDict = {}
            for item in artifact_substats:
                tempDict.update({item: {'rollCount': 1, 'rollValue': 0}})
            self.artifact_substats = tempDict
        elif isinstance(artifact_substats, dict):
            self.artifact_substats = artifact_substats
        else:
            self.artifact_substats = {}

        self.artifact_max_lines = artifact_max_lines or g.artifact_max_lines
        self.artifact_level = artifact_level or 0
        self.artifact_max_level = artifact_max_level or g.artifact_max_level
        self.artifact_substat_level_increment = artifact_substat_level_increment or g.artifact_substat_level_increment

        # Other internal only variables
        # Starting artifact lines
        if len(self.artifact_substats.keys()) == 0:
            self.artifact_starting_lines = 3
        else:
            self.artifact_starting_lines = len(self.artifact_substats.keys())

        # Exp tracking
        if self.artifact_level > 0:
            self.artifact_exp = sum(g.artifact_exp_by_level[:self.artifact_level])
        else:
            self.artifact_exp = 0       

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

        # Randomly generate substats based on sampling from substat pool without replacement
        for i in range(self.artifact_starting_lines - len(self.artifact_substats.keys())):
            self.Add_Substat()

    def Add_Substat(self):
        # Generate random artifact substat based on slot and mainstat up to maxlines

        if len(self.artifact_substats.keys()) >= self.artifact_max_lines:
            print('Artifact lines exceeds max')
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
        subStat_probabilities = self.SubStat_Probabilities_From_Weights(subStat_Pool)
        artifact_subStat = choice(list(subStat_probabilities.keys()),
                                  p=list(subStat_probabilities.values()))
        # Initialize rollCount and rollValue
        artifact_substats.update(
            {artifact_subStat: {
                'rollCount': 1,
                'rollValue': 0,
            }})

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
            print('Artifact level equal to or greater than max')
            return

        # Record start and end states because we need to count how many substat increments occurred
        start_level = self.artifact_level
        final_level = start_level + increment

        # Increment artifact exp
        exp_consumed = sum(g.exp_level_info[self.artifact_rarity][start_level:final_level])
        self.artifact_exp += exp_consumed

        # Determine how many substat increments occurred
        substat_increments = final_level // self.artifact_substat_level_increment - start_level // self.artifact_substat_level_increment

        for _ in range(substat_increments):
            if len(self.artifact_substats.keys()) < self.artifact_max_lines:
                self.Add_Substat()
            else:
                self.Increment_Substat()

        self.artifact_level = min(final_level, self.artifact_max_level)

        return exp_consumed

    def random(self, slotpool=None):
        # Generate a random artifact

        # Reset level and other defaults
        self.artifact_level = 0
        self.artifact_exp = 0
        self.artifact_rarity = '5*'

        # Randomly choose a slot assuming equal probabilities for all slots
        slot_Pool = slotpool or slotType.copy()
        slot_Probabilities = [1 / len(slot_Pool)] * len(slot_Pool)
        artifact_Slot = choice(slot_Pool, p=slot_Probabilities)
        self.artifact_type = artifact_Slot

        # Randomly choose a set assuming equal probabilities for all sets
        self.artifact_set = None

        # Randomly choose the number of substat lines assuming a 5* artifact
        # TODO: Make this more generic
        self.artifact_starting_lines = choice([3, 4], p=[0.80, 0.20])
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
        for i in self.artifact_substats:
            print('%4s cnt: %i' %
                  (i, self.artifact_substats[i]['rollCount']))     

    def get_substat_lines(self):
        return len(self.artifact_substats.keys())

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

    def fodder(self):
        # return exp from foddered artifact
        return g.base_exp_gain[self.artifact_rarity] + 0.8 * self.artifact_exp
        


##########################################
# Simulation
##########################################
nSuccess_T0 = 0
nSuccess_T1 = 0
nSuccess_T2 = 0
debug = False
trials = 1000
slot_counter = {
    'flower': 0,
    'feather': 0,
    'sands': 0,
    'goblet': 0,
    'circlet': 0,
}

artifact_exp_consumed = 0
artifact_exp_gained = 0
artifacts_by_starting_lines = {
    3: 0,
    4: 0,    
}

# Generate Random Artifact
artifact = Artifact(artifact_max_level=g.artifact_max_level, artifact_substat_level_increment=g.artifact_substat_level_increment)

for i in range(trials):
    artifact.random()
    if debug:
        #artifact = Artifact('goblet', None, 'dmgp', ['cr', 'hpp', 'def'])
        #artifact.Generate_Substats()
        print('')
        artifact.print()
        pass

    if not c.artifact_is_valid(artifact, 0, g):
        artifact.print()

    # Lvl0 Filter
    if f.Keep_Artifact(artifact, g.filters_T0, g.filters_exclude, debug):
        nSuccess_T0 += 1

        # +4
        artifact_exp_consumed += artifact.Level_Artifact(artifact.artifact_substat_level_increment)
        if not c.artifact_is_valid(artifact, 4, g):
            artifact.print()

        if debug:
            artifact.print()
            print('exp required: %s' % artifact_exp_consumed)
            pass

        # Lvl4 Filter
        if f.Keep_Artifact(artifact, g.filters_T1, g.filters_exclude, debug):
            nSuccess_T1 += 1

            # +8
            artifact_exp_consumed += artifact.Level_Artifact(artifact.artifact_substat_level_increment)
            if not c.artifact_is_valid(artifact, 8, g):
                artifact.print()

            # +12
            artifact_exp_consumed += artifact.Level_Artifact(artifact.artifact_substat_level_increment)
            if not c.artifact_is_valid(artifact, 12, g):
                artifact.print()

            if debug:
                artifact.print()
                print('exp required: %s' % artifact_exp_consumed)
                pass

            # Lvl12 Filter
            if f.Keep_Artifact(artifact, g.filters_T2, [], debug):
                nSuccess_T2 += 1

                # +16
                artifact_exp_consumed += artifact.Level_Artifact(artifact.artifact_substat_level_increment)

                # +20
                artifact_exp_consumed += artifact.Level_Artifact(artifact.artifact_substat_level_increment)
                if not c.artifact_is_valid(artifact, 20, g):
                    artifact.print()

                if debug:
                    artifact.print()
                    print('exp required: %s' % artifact_exp_consumed)
                    pass
 
                slot_counter[artifact.artifact_type] += 1
                artifacts_by_starting_lines[artifact.artifact_starting_lines] += 1
            
            else:
                artifact_exp_gained += artifact.fodder()
                c.verify_artifact_fodder_exp_return(artifact, 12, g)

        else:
            artifact_exp_gained += artifact.fodder()
            c.verify_artifact_fodder_exp_return(artifact, 4, g)

    else:
        artifact_exp_gained += artifact.fodder()
        c.verify_artifact_fodder_exp_return(artifact, 0, g)

print('')
print('T0: %s %s' % (nSuccess_T0, nSuccess_T0 / trials))
print('T1: %s %s' % (nSuccess_T1, nSuccess_T1 / trials))
print('T2: %s %s' % (nSuccess_T2, nSuccess_T2 / trials))

n_runs = trials/g.n_5stars_per_run
non_5star_exp_gained = n_runs * g.non_5star_exp_per_run
exp_surplus = non_5star_exp_gained + artifact_exp_gained - artifact_exp_consumed

print('')
print('Artifact Exp Used: %i' % artifact_exp_consumed)
print('Artifact Exp Gained (5stars only): %i' % artifact_exp_gained)
print('Non 5 Star Exp Gained: %i' % non_5star_exp_gained)
print('Total Exp Gained: %i' % (non_5star_exp_gained + artifact_exp_gained))
print('Exp Surplus: %i' % exp_surplus)
print('Exp lost if foddering Lvl_0: %i' % ((trials-nSuccess_T0)*g.base_exp_gain['5*']))
print('')
print('L20 Artifacts Summary: ')
print(artifacts_by_starting_lines)
print(slot_counter)