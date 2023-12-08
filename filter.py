import contextlib

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
            break

    if not state:
        if debug:
            print('Rejected: No matches')
        return state

    # Exclusion will always override
    for j in range(len(exclusion_filters)):
        if exclusion_filters[j]['f'](artifact, exclusion_filters[j]['p']):
            state = False
            break

    if debug:
        if state:
            print('Accepted: Rule %i' % i)
        else: 
            print('Rejected: Rule %i' % j)

    return state