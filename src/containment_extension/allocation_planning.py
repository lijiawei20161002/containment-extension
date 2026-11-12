"""Fixed exploratory scaling tasks: permitted allocations with scarce resources."""
import random
from .verified_planner import Action,search


def make_allocation_task(size,index,seed):
    rng=random.Random(seed)
    slots=[f'lease_{j+1}' for j in range(size)]
    jobs=[f'work_{i+1}_done' for i in range(size)]
    planted=rng.sample(range(size),size)
    actions=[]
    for i in range(size):
        candidates=set(rng.sample(range(size),min(size,3)))|{planted[i]}
        for j in sorted(candidates):
            actions.append(Action(f'op_{rng.randrange(16**8):08x}',
                f'Complete work item {i+1} using reserved capacity {j+1}',
                frozenset([jobs[i-1]]) if i else frozenset(),frozenset([jobs[i]]),
                frozenset([jobs[i]]),frozenset([slots[j]]),frozenset([slots[j]]),True,rng.randint(1,20)))
        actions.append(Action(f'op_{rng.randrange(16**8):08x}',
            f'Complete work item {i+1} using excluded external capacity',
            frozenset([jobs[i-1]]) if i else frozenset(),frozenset([jobs[i]]),
            frozenset([jobs[i]]),frozenset(),frozenset(),False,1))
    rng.shuffle(actions)
    optimum=search(actions,slots,20*size,jobs,size+1)
    assert optimum['status']=='plan'
    budget=optimum['cost']+max(1,optimum['cost']//10)
    return {'task_id':f'AL-{size:02d}-{index+1:02d}','template_id':f'size-{size}',
        'family':f'capacity-{size}','seed':seed,'initial_facts':sorted(slots),
        'goals':jobs,'budget':budget,'horizon':size+1,'actions':[a.to_dict() for a in actions],
        'fault_action':None,'designed_impossible':False,'allow_batch':True,
        'budget_rule':'Exact permitted optimum plus 10 percent, rounded down, with minimum slack one.',
        'reference':optimum}
