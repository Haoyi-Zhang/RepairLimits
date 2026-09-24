"""Exhaustive compatible-path oracle, NOT information-set dynamic programming.

The oracle and checker share the audit interpreter. Paths from different worlds
must prescribe identical actions at identical complete observation/action
histories. A finite compatible path family is exactly an executable policy.
"""
from __future__ import annotations
from .model import validate
from .check import start, run, observation, options, distance


def paths(c,w,path_cap=100000):
    reference = run(c,w,start(c,w),ideal=True).output
    answer = []
    def walk(m,history,rules):
        m = run(c,w,m); obs = observation(c,m); key = history + (obs,)
        acts = options(c,m)
        if not acts:
            answer.append((distance(c,m.output,reference),dict(rules),m.output))
            if len(answer) > path_cap: raise RuntimeError('oracle path cap')
        else:
            for a in acts:
                rules[key] = a
                walk(run(c,w,m,choice=a),key+(str(a),),rules)
                del rules[key]
    walk(start(c,w),(),{})
    return answer


def exact_oracle(c,combination_cap=2000000):
    validate(c)
    catalog = [paths(c,w) for w in c['worlds']]
    hindsight = max(min(p[0] for p in ps) for ps in catalog)
    ordered = sorted(catalog,key=len)
    best = float('inf'); tests = 0; policy = {}; winner = None
    def choose(index,worst):
        nonlocal best,tests,winner
        if worst >= best: return
        if index == len(ordered): best = worst; winner = dict(policy); return
        for cost,rules,_ in sorted(ordered[index],key=lambda x:x[0]):
            tests += 1
            if tests > combination_cap: raise RuntimeError('oracle combination cap')
            if max(worst,cost) >= best or any(k in policy and policy[k] != a for k,a in rules.items()): continue
            added = [k for k in rules if k not in policy]
            policy.update(rules)
            choose(index+1,max(worst,cost))
            for k in added: del policy[k]
    choose(0,0)
    if best == float('inf'): raise RuntimeError('no compatible policy: implementation fault')
    return {'value':int(best),'hindsight':hindsight,'path_count':sum(map(len,catalog)),'combinations':tests}
