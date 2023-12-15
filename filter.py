import contextlib

##########################################
# Evaluate generated Artifacts against a filter and see how many meet criteria
##########################################
def Artifact_Accept_Filter(artifact, filter):
    # Returns True if artifact matches filter

    if len(filter['substats']) == 0:
        return True

    s_isect = set(filter['substats']).intersection(
        set(artifact.get_substat_list()))

    if artifact.get_slot() in filter['types'] and artifact.get_mainstat() in filter[
                'mainstats'] and len(s_isect) >= filter['substat_matches']:
        return True

    return False


def Artifact_Reject_Filter(artifact, filter):
    # Returns True if artifact matches filter

    s_isect = set(filter['substats']).intersection(
        set(artifact.get_substat_list()))

    if artifact.get_slot() in filter['types'] and artifact.get_mainstat() in filter[
                'mainstats'] and len(s_isect) >= filter['substat_matches']:
        return True

    return False

def Artifact_Reject_Rollcount_Early_Filter(artifact, filter):
    # Returns True if artifact will not be able to reach the target substat rolls by 
    # the target level

    rcnt = 0
    level_increment = artifact.get_substat_level_increment()
    current_level = artifact.get_level()
    target_level = filter['target_level'] or 3*artifact.get_substat_level_increment()
    
    # Determine how many substat increments are left
    remaining_substat_increments = (target_level // level_increment - 
                                    current_level // level_increment)

    # Reduce the rcnt target by the number of the substats remaining
    target_rcnt = filter['min_roll_count'] - remaining_substat_increments

    # Count number of substat rolls into desired substats
    for s in filter['substats']:
        with contextlib.suppress(KeyError):
            rcnt += artifact.get_substats()[s]['rollCount']

    if (artifact.get_slot() in filter['types'] and 
        artifact.get_mainstat() in filter['mainstats'] and 
        rcnt < target_rcnt):
        return True

    return False


def Artifact_Rollcount_Filter(artifact, filter):
    # Returns True if total roll count for specified stats meets or exceeds minimum

    if len(filter['substats']) == 0:
        return True

    rcnt = 0

    for s in filter['substats']:
        with contextlib.suppress(KeyError):
            rcnt += artifact.get_substats()[s]['rollCount']

    if (artifact.get_slot() in filter['types'] and 
        artifact.get_mainstat() in filter['mainstats'] and 
        rcnt >= filter['min_roll_count']):
        return True

    return False


def All_Of(artifact, filter):
    # Returns True if artifact matches all of the filters

    return all(fs['f'](artifact, fs['p']) for fs in filter['fs'])


def None_Of(artifact, filter):
    # Returns True if artifact matches none of the filters
    
    return all(not fs['f'](artifact, fs['p']) for fs in filter['fs'])


def Any_Of(artifact, filter):
    # Returns True if artifact matches any of the filters
    
    return any(fs['f'](artifact, fs['p']) for fs in filter['fs'])
        

def Keep_Artifact(artifact, inclusion_filters, exclusion_filters, debug=False):
    # Returns True if artifact matches any inclusion filter, and does not match any exclusion filter
    # Rejection filters will override inclusion

    state = False
    description = ''
    for i in inclusion_filters:
        if inclusion_filters[i]['f'](artifact, inclusion_filters[i]['p']):
            state = True
            description = 'Accepted: Rule ' + str(i)
            with contextlib.suppress(KeyError):
                description = description + ' - ' + inclusion_filters[i]['desc']
            break

    if not state:
        if debug:
            print('Rejected: No matches')
        return state

    # Exclusion will always override
    for j in exclusion_filters:
        if exclusion_filters[j]['f'](artifact, exclusion_filters[j]['p']):
            state = False
            description = 'Rejected: Rule ' + str(j)
            with contextlib.suppress(KeyError):
                description = description + ' - ' + exclusion_filters[j]['desc']
            break

    if debug:
        print(description)

    return state

def print_filter(fltr):
    if 'desc' in fltr:
        print(fltr['desc'])
    else:
        print('*** ', fltr['p'])

def print_filters(filters):
    for fltr in filters.values():
        print_filter(fltr)
            