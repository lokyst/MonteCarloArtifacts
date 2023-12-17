import contextlib

def check_n_substat_lines_is_valid(artifact):
    if len(artifact.get_substats().keys()) > 4:
        print('Artifact has too many substats: %i' % len(artifact.get_substats().keys()))
        return False

    return True

def check_substats_exclude_mainstat(artifact):
    if artifact.get_mainstat() in artifact.get_substats():
        print('Substats include mainstat: %s' % artifact.get_mainstat())
        return False

    return True

def check_roll_count_at_level_is_valid(artifact, level, game):
    rolls_by_level = game.rolls_by_level
    
    roll_count = 0
    for substat in artifact.get_substats():
        roll_count += artifact.get_substats()[substat]['rollCount']

    if roll_count > rolls_by_level[level][artifact.get_n_starting_lines()]:
        print('Too many rolls: %i' % roll_count)
        return False

    return True

def verify_artifact_level(artifact, level):
    if artifact.get_level() != level:
        print('Artifact level is not %i: %i' % (level, artifact.get_level()))
        return False

    return True

def verify_artifact_exp(artifact, level, game):
    expected_exp = sum(game.exp_level_info[artifact.get_rarity()][0:level])
    if artifact.get_exp() != expected_exp:
        print('Artifact exp is not %i at Lvl %i for %s: %i' % 
              (expected_exp, level, artifact.get_rarity(), artifact.get_exp()))
        return False

    return True

def verify_artifact_fodder_exp_return(artifact, level, game):
    expected_exp = game.base_exp_gain[artifact.get_rarity()] + 0.8 * sum(game.exp_level_info[artifact.get_rarity()][0:level])
    if artifact.fodder() != expected_exp:
        print('Artifact fodder exp return is not %.2f at Lvl %i for %s: %.2f' % 
              (expected_exp, level, artifact.get_rarity(), artifact.fodder()))
        return False

    return True

def artifact_is_valid(artifact, level, game):
    state = (
        check_n_substat_lines_is_valid(artifact) and
        check_substats_exclude_mainstat(artifact) and 
        check_roll_count_at_level_is_valid(artifact, level, game) and
        verify_artifact_level(artifact, level) and 
        verify_artifact_exp(artifact, level, game)
    )

    return state

