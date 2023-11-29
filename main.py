from numpy.random import choice
import contextlib
import copy

slotType = ['flower', 'feather', 'sands', 'goblet', 'circlet']

# Mainstats info for slots
slotInfo = {
    'flower': {
        'type': 'flower',
        'mainstats': ['hp'],
        'mainstat_probabilities': [1],
    },
    'feather': {
        'type': 'feather',
        'mainstats': ['atk'],
        'mainstat_probabilities': [1],
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
subStats = ['hp', 'atk', 'def', 'hpp', 'atkp', 'defp', 'er', 'em', 'cr', 'cd']
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


# Substats are weighted without replacement
def SubStat_Probabilities(subStats):
  subStat_Probabilities = {}
  for subStat in subStats:
    sumOfWeights = 0
    for subStat2 in subStats:
      sumOfWeights += subStat_Weights[subStat2]
    subStat_Probabilities[subStat] = subStat_Weights[subStat] / sumOfWeights
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
      artifact_maxlines=None,
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

    if artifact_maxlines is None:
      self.artifact_maxlines = 4
    else:
      self.artifact_maxlines = artifact_maxlines

  def __str__(self):
    return f"Type: '{self.artifact_type}' Main: '{self.artifact_mainstat}' Subs: {self.artifact_substats.keys()}"

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

    if len(self.artifact_substats.keys()) >= self.artifact_maxlines:
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

  def random(self):
    # Generate a random artifact

    # Randomly choose a slot assuming equal probabilities for all slots
    slot_Pool = slotType.copy()
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
    for i in self.artifact_substats.keys():
      print('SubStat: %s' % i)
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
      'types'] and artifact.artifact_mainstat in filter['mainstats'] and len(
          s_isect) >= filter['substat_matches']:
    return True

  return False


def Artifact_Reject_Filter(artifact, filter):
  # Returns True if artifact matches filter

  s_isect = set(filter['substats']).intersection(
      set(artifact.get_substat_list()))

  if artifact.artifact_type in filter[
      'types'] and artifact.artifact_mainstat in filter['mainstats'] and len(
          s_isect) >= filter['substat_matches']:
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
            'starting_substat_lines': 3,
            'substat_matches':2,
        }
    },
    {
        # 1. Keep any circlet, sands, or goblet with mainstat em
        'f': Artifact_Accept_Filter,
        'p': {
            'types': ['circlet', 'sands', 'goblet'],
            'mainstats': ['em'],
            'substats': [],
            'starting_substat_lines': 3,
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
            'starting_substat_lines': 3,
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
            'starting_substat_lines': 3,
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
            'starting_substat_lines': 3,
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
            'starting_substat_lines': 3,
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
            'starting_substat_lines': 3,
            'substat_matches': 1,
        },
    },
]

# Tighten Filters at +4
filters_4 = copy.deepcopy(filters_0)
# 3. Keep any sands with atkp or er and at least 1 crit stat
filters_4[3]['p']['substats'] = ['cr', 'cd']
filters_4[3]['p']['substat_matches'] = 1
# 4. Keep any goblet with dmgp and at least 1 crit stat
filters_4[4]['p']['substats'] = ['cr', 'cd']
filters_4[4]['p']['substat_matches'] = 1
# 5. Keep any sand, circlet or goblet with hpp, defp, atkp and CR && CD
filters_4[6]['p']['substats'] = ['cr', 'cd']
filters_4[5]['p']['substat_matches'] = 2
# 6. Keep any flower or feather with atk and CR && CD
filters_4[6]['p']['substats'] = ['cr', 'cd']
filters_4[6]['p']['substat_matches'] = 2

filters_4[6]['p']['substat_matches'] = 3

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

##########################################
# Simulation
##########################################
nSuccess_0 = 0
nSuccess_4 = 0
trials = 1000

# Generate Random Artifact
artifact = Artifact()

for i in range(trials):
  artifact.random()
  #artifact = Artifact('feather', None, 'atk', ['hp', 'cr', 'hpp'])
  #print(artifact)
  #artifact.print()

  if Keep_Artifact(artifact, filters_0, filters_exclude):
    nSuccess_0 += 1

    artifact.Add_Substat()
    #artifact.print()
    if Keep_Artifact(artifact, filters_4, filters_exclude):
      nSuccess_4 += 1

print('0: %s %s' % (nSuccess_0, nSuccess_0 / trials))
print('4: %s %s' % (nSuccess_4, nSuccess_4 / trials))
