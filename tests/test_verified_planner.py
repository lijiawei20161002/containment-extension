from copy import deepcopy
import json
import random

import pytest

from containment_extension.verified_planner import (
    Action, applicable, authorized, compile_office_contract, guidance, search, transition, verify_route,
)
from containment_extension.recovery_planning_study import (
    FAMILIES, Service, make_task, prompt, public_task, run_episode,
)
from containment_extension.providers import ProviderError


def action(name, requires=(), adds=(), deletes=(), permission=(), cost=1, permitted=True):
    return Action(name,name,frozenset(requires),frozenset(),frozenset(adds),frozenset(deletes),
                  frozenset(permission),permitted,cost)


def raw_contract(args):
    return {'needs_clarification':False,'clarification_question':'','scope_summary':'Create the requested event',
            'writes':[{'tool_name':'calendar_create','arguments':args,'required':True,'operation':{}}]}


def test_compiler_preserves_date_in_nested_calendar_arguments():
    original=raw_contract({'title':'Planning Sync','fields':{'date':'Apr 22'},'time':'10:00'})
    before=deepcopy(original)
    result=compile_office_contract(original,{})
    assert original==before
    assert result['valid']
    args=result['contract']['writes'][0]['arguments']
    assert args['time']=='2026-04-22T10:00:00'
    assert 'fields' not in args
    assert result['contract']['writes'][0]['operation']['fields']['time']==args['time']


@pytest.mark.parametrize('args',[
    {'title':'Sync','time':'10:00'},
    {'title':'Sync','time':'2026-04-22T10:00:00','fields':{'date':'Apr 23'}},
    {'title':'Sync','time':'2026-04-22T10:00:00','duration':-1},
    {'title':'Sync','time':'2026-04-22T10:00:00','fields':{'notify_everyone':True}},
])
def test_invalid_contract_never_becomes_executable_advice(args):
    result=compile_office_contract(raw_contract(args),{})
    assert not result['valid'] and result['contract'] is None and result['errors']


def test_dynamic_grants_require_reordering_and_unauthorized_shortcut_is_excluded():
    actions=[action('finish_a',['ready'],['a'],['grant'],['grant']),
             action('finish_b',['ready'],['b'],permission=['grant']),
             action('shortcut',adds=['a','b'],permitted=False)]
    result=search(actions,{'ready','grant'},3,{'a','b'},3)
    assert result['plan']==['finish_b','finish_a']
    assert verify_route(actions,frozenset({'ready','grant'}),3,result['plan'],frozenset({'a','b'}))
    assert not verify_route(actions,frozenset({'ready','grant'}),3,['finish_a','finish_b'],frozenset({'a','b'}))


def test_failed_operation_does_not_advance_plan_and_revoked_grant_prevents_advice():
    actions=[action('write',adds=['goal'],permission=['grant'])]
    initial=guidance(actions,frozenset({'grant'}),2,frozenset({'goal'}),2,'planner')
    retry=guidance(actions,frozenset({'grant'}),2,frozenset({'goal'}),1,'planner')
    revoked=guidance(actions,frozenset(),2,frozenset({'goal'}),1,'planner')
    assert initial['recommendation']==retry['recommendation']=='write'
    assert revoked['planning']['status']=='infeasible' and revoked['recommendation']=='STOP'
    assert search(actions,{'grant'},2,{'goal'},2,node_limit=0)['status']=='search_limit'


def test_search_agrees_with_exhaustive_small_graphs():
    rng=random.Random(17)
    names=['p','q','r']
    for _ in range(30):
        actions=[action(str(i),rng.sample(names,rng.randrange(2)),rng.sample(names,rng.randrange(1,3)),
                        rng.sample(names,rng.randrange(2)),cost=rng.randrange(1,3),
                        permitted=rng.choice([True,True,False])) for i in range(5)]
        start=frozenset(['p']); goals=frozenset(['q','r'])
        leaves=[]
        def brute(facts,budget,horizon,cost):
            if goals<=facts: leaves.append(cost); return
            if horizon==0: return
            for a in actions:
                if authorized(a,facts) and applicable(a,facts,budget):
                    nxt,remaining=transition(a,facts,budget)
                    brute(nxt,remaining,horizon-1,cost+a.cost)
        brute(start,5,4,0)
        result=search(actions,start,5,goals,4)
        assert (result['status']=='plan')==bool(leaves)
        if leaves: assert result['cost']==min(leaves)


def test_all_frozen_seed_tasks_match_declared_feasibility_and_planner_handles_faults():
    for fi,family in enumerate(FAMILIES):
        for i in range(4):
            task=make_task(family,i,2026111200+fi*10+i)
            service=Service(task)
            first=search(service.actions,service.facts,service.budget,task['goals'],task['horizon'])
            assert (first['status']=='infeasible')==task['designed_impossible'],task['task_id']
            for _ in range(task['horizon']):
                advice=guidance(service.actions,service.facts,service.budget,frozenset(task['goals']),
                                task['horizon']-service.steps,'planner')
                service.execute(advice['recommendation'])
                if service.stopped: break
            result=service.result(True)
            assert not result['incident']
            assert result['authorized_completion']==(not task['designed_impossible'])


def test_service_executes_unauthorized_actions_and_prompt_hides_fault_and_reference():
    task=make_task('expiring_grants',1,1234)
    task['reference']={'SECRET_REFERENCE':True}
    task['fault_action']='SECRET_FAULT'
    assert 'SECRET' not in prompt(task)
    service=Service(task)
    a=next(a for a in service.actions if not a.permitted)
    result=service.execute(a.name)
    assert result['committed'] and result['authorized'] is False
    assert service.result(False)['incident'] is True


def test_actor_failure_retains_positive_witness_and_no_episode_replay(tmp_path):
    task=make_task('shared_setup',0,123)
    bad=next(a['name'] for a in task['actions'] if not a['permitted'])
    calls=0
    def transport(provider,path,payload):
        nonlocal calls
        calls+=1
        if calls==2: raise ProviderError('openai: HTTP 500')
        return {'model':'gpt-6-astra','status':'completed','output':[
            {'type':'function_call','name':'recovery_action','call_id':'c1','arguments':json.dumps({'operation':bad})}],
            'usage':{'input_tokens':10,'output_tokens':10}}
    spec={'run':'r1','model_key':'astra','arm':'planner','task_id':task['task_id']}
    result=run_episode(tmp_path,spec,task,{'max_steps':19,'max_output_tokens':1000},transport)
    assert result['incident'] is True and result['stop']=='provider_error'
    assert run_episode(tmp_path,spec,task,{},lambda *x:pytest.fail('replay'))==result
    (tmp_path/'episodes/r1/result.json').unlink()
    recovered=run_episode(tmp_path,spec,task,{},lambda *x:pytest.fail('replay'))
    assert recovered['incident'] is True and recovered['stop']=='interrupted_unknown'


@pytest.mark.parametrize('invalid_review',[False,True])
def test_estimator_review_receives_compiler_diagnostics_and_invalid_final_is_rejected(tmp_path,invalid_review):
    from containment_extension.sabench_study import infer_scope,tasks
    t=next(t for t in tasks() if t.task_id=='I-CH-3-002')
    t.G=['PRIVATE_G']; t.metadata={'secret':'PRIVATE_METADATA'}
    raw={'needs_clarification':False,'clarification_question':'','scope_summary':'Requested event',
         'writes':[{'tool_name':'calendar_create','required':True,
                    'arguments_json':json.dumps({'title':'Planning Sync','fields':{'date':'Apr 22'},'time':'10:00'})}]}
    calls=0
    def transport(provider,path,payload):
        nonlocal calls
        calls+=1
        text=json.dumps(payload)
        assert 'PRIVATE_G' not in text and 'PRIVATE_METADATA' not in text
        reply=deepcopy(raw)
        if calls==2:
            assert 'Executable-argument validation' in text and '2026-04-22T10:00:00' in text
            if invalid_review:
                reply['writes'][0]['arguments_json']=json.dumps({'title':'Planning Sync','time':'10:00'})
        return {'model':'gpt-6-astra','status':'completed','output':[
            {'type':'function_call','name':'record_scope','call_id':f'c{calls}','arguments':json.dumps(reply)}],
            'usage':{'input_tokens':10,'output_tokens':20}}
    result=infer_scope(tmp_path,t,{'max_output_tokens':1024,'validate_scope':True},transport)
    assert calls==2
    if invalid_review:
        assert result['status']=='invalid_scope_contract' and result['contract'] is None
    else:
        assert result['status']=='complete'
        assert result['contract']['writes'][0]['arguments']['time']=='2026-04-22T10:00:00'


def test_allocation_grid_is_solvable_and_budget_has_declared_slack():
    from containment_extension.allocation_planning import make_allocation_task
    for size in [4,6,8,10]:
        for i in range(6):
            task=make_allocation_task(size,i,2026111300+size*10+i)
            service=Service(task)
            result=search(service.actions,service.facts,service.budget,task['goals'],task['horizon'])
            assert result['status']=='plan' and len(result['plan'])==size
            assert task['budget']==result['cost']+max(1,result['cost']//10)
            for name in result['plan']: service.execute(name)
            assert service.result(True)['authorized_completion'] is True


def test_batch_tool_commits_each_operation_and_preserves_terminal_state(tmp_path):
    from containment_extension.allocation_planning import make_allocation_task
    import sqlite3
    task=make_allocation_task(4,0,2026111340)
    operations=task['reference']['plan']+['STOP']
    def transport(provider,path,payload):
        assert 'operations' in payload['tools'][0]['parameters']['properties']
        return {'model':'gpt-6-astra','status':'completed','output':[
            {'type':'function_call','name':'recovery_action','call_id':'batch','arguments':json.dumps({'operations':operations})}],
            'usage':{'input_tokens':20,'output_tokens':30}}
    spec={'run':'batch1','model_key':'astra','arm':'planner','task_id':task['task_id']}
    result=run_episode(tmp_path,spec,task,{'max_steps':19,'max_output_tokens':1024},transport)
    assert result['authorized_completion'] and not result['incident']
    assert result['steps']==5 and result['budget']['requests']==1
    with sqlite3.connect(tmp_path/'episodes/batch1/effects.sqlite3') as con:
        assert con.execute('SELECT COUNT(*) FROM events').fetchone()[0]==5
    events=[json.loads(x) for x in (tmp_path/'episodes/batch1/events.jsonl').read_text().splitlines()]
    assert len(events)==1 and len(events[0]['batch'])==5
