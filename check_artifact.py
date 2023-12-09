import contextlib

def check_n_substat_lines_is_valid(artifact):
    if len(artifact.artifact_substats.keys()) > 4:
        print('Artifact has too many substats: %i' % len(artifact.artifact_substats.keys()))
        return False

    return True

def check_substats_exclude_mainstat(artifact):
    if artifact.artifact_mainstat in artifact.artifact_substats.keys():
        print('Substats include mainstat: %s' % artifact.artifact_mainstat)
        return False

    return True

def check_roll_count_at_level_is_valid(artifact, level=20):
    rolls_by_level = {
        '0': {
            '3': 3,
            '4': 4,             
        },
        '4': {
            '3': 4,
            '4': 5,             
        },
        '8': {
            '3': 5,
            '4': 6,             
        },
        '12': {
            '3': 6,
            '4': 7,             
        },
        '16': {
            '3': 7,
            '4': 8,             
        },
        '20': {
            '3': 8,
            '4': 9,             
        },
    }

    roll_count = 0
    for substat in artifact.artifact_substats:
        roll_count += artifact.artifact_substats[substat]['rollCount']

    if roll_count > rolls_by_level[str(level)]['4']:
        print('Too many rolls: %i' % roll_count)
        return False

    return True


def artifact_is_valid(artifact, level):
    state = True
    state = state and check_n_substat_lines_is_valid(artifact)
    state = state and check_substats_exclude_mainstat(artifact)
    state = state and check_roll_count_at_level_is_valid(artifact, level)

    return state


        
    
        
    
