"""Bounded command-line interface. Outputs never derive paths from case identifiers."""
from __future__ import annotations
import argparse, json, resource, sys
from pathlib import Path
from .check import strict_json, check_certificate, policy_replay
from .model import validate
from .solve import synthesize, extract_core
from .oracle import exact_oracle
from .symbolic import classify_contract


def load(path: str):
    p=Path(path)
    if p.stat().st_size > 32*1024*1024:
        raise ValueError('input file exceeds 32 MiB limit')
    return strict_json(p.read_text(encoding='utf-8'))


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='command',required=True)
    for name in ('solve','oracle','core'):
        p=sub.add_parser(name);p.add_argument('case')
    p=sub.add_parser('check');p.add_argument('case');p.add_argument('certificate')
    p=sub.add_parser('symbolic');p.add_argument('input');p.add_argument('--order',choices=('interleaved','actions-first'),default='interleaved')
    args=parser.parse_args()
    resource.setrlimit(resource.RLIMIT_AS,(3*1024**3,3*1024**3))
    resource.setrlimit(resource.RLIMIT_CPU,(40,40))
    try:
        if args.command=='symbolic':
            data=load(args.input)
            if type(data) is not dict or set(data)!={'specification','premise'}:
                raise ValueError('symbolic input fields')
            result=classify_contract(data['specification'],data['premise'],order=args.order)
        else:
            c=load(args.case);validate(c)
            if args.command=='solve': result=synthesize(c)
            elif args.command=='oracle': result=exact_oracle(c)
            elif args.command=='core':
                result={'kind':'inclusion-minimal-not-minimum','worlds':extract_core(c,c['budget'])}
            else:
                cert=load(args.certificate)
                result={'check':check_certificate(c,cert),'replay':policy_replay(c,cert)}
        print(json.dumps(result,sort_keys=True,separators=(',',':')))
        return 0
    except (ValueError,TypeError,KeyError,IndexError,RecursionError,UnicodeError,OSError) as error:
        print(json.dumps({'status':'rejected','reason':str(error)}),file=sys.stderr)
        return 2
    except (RuntimeError,MemoryError) as error:
        print(json.dumps({'status':'unknown-resource','reason':str(error)}),file=sys.stderr)
        return 3

if __name__=='__main__':
    raise SystemExit(main())
