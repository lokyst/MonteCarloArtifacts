import contextlib

def check_n_substat_lines_is_valid(artifact):
    if len(artifact.artifact_substats.keys()) > 4:
        print('Artifact has too many substats: %i' % len(artifact.artifact_substats.keys()))
        return False

    return True

def check_substats_exclude_mainstat(artifact):
    if artifact.artifact_mainstat in artifact.artifact_substats:
        print('Substats include mainstat: %s' % artifact.artifact_mainstat)
        return False

    return True

def check_roll_count_at_level_is_valid(artifact, level):
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

def verify_artifact_level(artifact, level):
    if artifact.artifact_level != level:
        print('Artifact level is not %i: %i' % (level, artifact.artifact_level))
        return False

    return True

def verify_artifact_exp(artifact, level, game):
    expected_exp = sum(game.exp_level_info[artifact.artifact_rarity][0:level])
    if artifact.artifact_exp != expected_exp:
        print('Artifact exp is not %i at Lvl %i for %s: %i' % 
              (expected_exp, level, artifact.artifact_rarity, artifact.artifact_exp))
        return False

    return True

def verify_artifact_fodder_exp_return(artifact, level, game):
    expected_exp = game.base_exp_gain[artifact.artifact_rarity] + 0.8 * sum(game.exp_level_info[artifact.artifact_rarity][0:level])
    if artifact.fodder() != expected_exp:
        print('Artifact fodder exp return is not %.2f at Lvl %i for %s: %.2f' % 
              (expected_exp, level, artifact.artifact_rarity, artifact.fodder()))
        return False

    return True

def artifact_is_valid(artifact, level, game):
    state = True
    state = state and check_n_substat_lines_is_valid(artifact)
    state = state and check_substats_exclude_mainstat(artifact)
    state = state and check_roll_count_at_level_is_valid(artifact, level)
    state = state and verify_artifact_level(artifact, level)
    state = state and verify_artifact_exp(artifact, level, game)

    return state

