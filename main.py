from numpy.random import choice
import copy
import contextlib
import genshin2 as g
import filter as f
import check_artifact as c
import numpy.random as rnd
import json

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
        self.artifact_type = artifact_type or g.slotType[0]
        self.artifact_set = artifact_set
        self.artifact_mainstat = artifact_mainstat or g.slotInfo[self.artifact_type]['mainstats'][0]
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

    def get_level(self):
        return self.artifact_level

    def get_substat_level_increment(self):
        return self.artifact_substat_level_increment

    def get_slot(self):
        return self.artifact_type

    def get_n_starting_lines(self):
        return self.artifact_starting_lines

    def get_max_level(self):
        return self.artifact_max_level

    def get_mainstat(self):
        return self.artifact_mainstat

    def get_substats(self):
        return self.artifact_substats

    def get_rarity(self):
        return self.artifact_rarity

    def get_exp(self):
        return self.artifact_exp

    def to_dict(self):
        return {
            'type': self.artifact_type,
            'set': self.artifact_set,
            'mainstat': self.artifact_mainstat,
            'level': self.artifact_level,
            'substats': self.artifact_substats,
            'max_lines': self.artifact_max_lines,
            'max_level': self.artifact_max_level,
            'substat_level_increment': self.artifact_substat_level_increment,
            'exp': self.artifact_exp,
        }
        


##########################################
# Generate All Artifacts at All Levels
##########################################
def Generate_All_Artifacts(trials=1000, seed=1234, debug=False):
    # debug = False
    # trials = 1000
    rnd.seed(seed)
    artifacts = {}
    artifact = Artifact()
    
    for i in range(trials):
        artifacts.update({i: {}})
        # Generate Random Artifact
        artifact.random()
        if debug:
            # artifact = Artifact('goblet', None, 'dmgp', ['cr', 'hpp', 'er'])
            # artifact = Artifact('rope', None, 'err', ['atkp', 'cd', 'hpp'])
            # artifact.Generate_Substats()
            print('')
            artifact.print()
            pass
        if not c.artifact_is_valid(artifact, 0, g):
            artifact.print()
    
        lvl = 0
        artifacts[i].update({lvl: copy.deepcopy(artifact)})
        while lvl < artifact.get_max_level():
            artifact.Level_Artifact(artifact.get_substat_level_increment())
            lvl += artifact.get_substat_level_increment()
            artifacts[i].update({lvl: copy.deepcopy(artifact)})

    return artifacts



##########################################
# Simulation
##########################################
temp = Generate_All_Artifacts(1000)
debug = False

artifacts = {}
if debug:
    artifacts.update({0: temp[168]})
else:
    artifacts = temp
trials = len(artifacts)

results = {}

# Initialize counters
successes_by_tier = {}
for tier in g.tiers:
    successes_by_tier.update({tier: 0})
slot_counter = {}
for slot in g.slotType:
    slot_counter.update({slot: {'total': 0}})
    for mainstat in g.slotInfo[slot]['mainstats']:
        slot_counter[slot].update({mainstat: 0})

artifact_exp_consumed = 0
artifact_exp_gained = 0
artifacts_by_starting_lines = {
    3: 0,
    4: 0,    
}

artifact = None
kept_artifacts = {}
for i in artifacts:
    lvl = 0
    tiers = g.tiers.copy()
    tiers.sort()
    tiers.reverse()
    artifact = artifacts[i][lvl]

    if debug:
        artifact.print()

    # Filter by tiers or take to max level
    while len(tiers) > 0:
        tier = tiers.pop()

        if f.Keep_Artifact(artifact, g.filters[tier], g.filters_exclude[tier], debug):
            successes_by_tier[tier] += 1

            # Check if next increment is another tier level or max level
            next_tier = tiers[-1] if len(tiers) > 0 else artifact.get_max_level()

            # Level in increments until next tier level or max level
            while artifact.get_level() < next_tier:
                start_exp = artifact.get_exp()
                lvl += artifact.get_substat_level_increment()
                artifact = artifacts[i][lvl]
                end_exp = artifact.get_exp()
                artifact_exp_consumed += end_exp - start_exp

                if not c.artifact_is_valid(artifact, lvl, g):
                    artifact.print()

                if debug:
                    artifact.print()
                    pass
    
                if artifact.get_level() == artifact.get_max_level():
                    slot_counter[artifact.get_slot()]['total'] += 1
                    slot_counter[artifact.get_slot()][artifact.get_mainstat()] += 1
                    artifacts_by_starting_lines[artifact.get_n_starting_lines()] += 1
                    kept_artifacts[i] = artifact.to_dict()
                    # results[i] = True
                    break

        else:
            artifact_exp_gained += artifact.fodder()
            c.verify_artifact_fodder_exp_return(artifact, tier, g)
            # kept_artifacts[i] = artifact.to_dict()
            # results[i] = False
            break


# Output to JSON
with open('results.json', 'w') as outfile:
    json.dump({'artifacts': kept_artifacts, 
            'results': results}, outfile)



##########################################
# Summarize Results
##########################################
print('')
for i in successes_by_tier:
    print('%3s: %4i  %.3f' % (('T'+str(i)), successes_by_tier[i], successes_by_tier[i] / trials))

n_runs = trials/g.n_5stars_per_run
non_5star_exp_gained = n_runs * g.non_5star_exp_per_run
exp_surplus = non_5star_exp_gained + artifact_exp_gained - artifact_exp_consumed

print('')
print('Artifact Exp Used: %i' % artifact_exp_consumed)
print('Artifact Exp Gained (5stars only): %i' % artifact_exp_gained)
print('Non 5 Star Exp Gained: %i' % non_5star_exp_gained)
print('Total Exp Gained: %i' % (non_5star_exp_gained + artifact_exp_gained))
print('Exp Surplus: %i' % exp_surplus)

tier = 0
print('Exp lost if foddering Lvl_%i: %i' % (tier, (trials-successes_by_tier[tier])*g.base_exp_gain['5*']))

print('')
print('L%i Artifacts Summary: %i Trial(s)' % (g.artifact_max_level, trials))
print('starting lines:', artifacts_by_starting_lines)
for slot in slot_counter.keys():
    print(slot, slot_counter[slot])
