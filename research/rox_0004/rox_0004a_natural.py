#!/usr/bin/env python3
from __future__ import annotations

import argparse, csv, glob, hashlib, json, math, random
from collections import defaultdict
from pathlib import Path

import numpy as np

EXP="ROX-0004A"
LAM=1e-3
MAXIT=100
TOL=1e-10
LN100=math.log(100.0)

SPLITS={
"exp1":{
"DEV":set("24 9 1 23 21 2 39 25 10 4 31 12 14 50 15 48 32 34 46 28 22 27 44 37 3 20 6 35 47".split()),
"VAL":set("30 45 5 29 8 17 13 18 41 49".split()),
"TEST":set("16 33 40 11 26 38 19 7 36 42".split())},
"exp2":{
"DEV":set("46 42 48 49 10 44 24 3 14 22 7 25 11 36 6 4 34 17 45 38 26 37 23 18 12 15 35 1 13".split()),
"VAL":set("29 32 31 9 20 27 21 40 50 30".split()),
"TEST":set("8 19 28 43 5 39 47 16 33 2".split())}
}

def sha_seed(*parts):
    s="|".join(map(str,parts))
    return int.from_bytes(hashlib.sha256(s.encode()).digest()[:8],"big")

def sigmoid(x):
    return 1.0/(1.0+np.exp(-np.clip(x,-40,40)))

def fit_logit(X,y):
    X=np.asarray(X,float); y=np.asarray(y,float)
    p=X.shape[1]; b=np.zeros(p)
    I=np.eye(p); I[0,0]=0.0
    for _ in range(MAXIT):
        eta=X@b; pr=sigmoid(eta)
        g=X.T@(y-pr)-LAM*(I@b)
        w=pr*(1-pr)
        H=-(X.T@(X*w[:,None]))-LAM*I
        try: step=np.linalg.solve(H,g)
        except np.linalg.LinAlgError: step=np.linalg.pinv(H)@g
        b2=b-step
        if np.max(np.abs(b2-b))<TOL:
            b=b2; break
        b=b2
    return b

def ll_logit(X,y,b):
    eta=np.asarray(X,float)@b
    y=np.asarray(y,float)
    return float(np.sum(y*(-np.logaddexp(0,-eta))+(1-y)*(-np.logaddexp(0,eta))))

def fit_ridge(X,y):
    X=np.asarray(X,float); y=np.asarray(y,float)
    p=X.shape[1]; I=np.eye(p); I[0,0]=0.0
    return np.linalg.solve(X.T@X+LAM*I,X.T@y)

def gaussian_ll(y,mu,var):
    y=np.asarray(y,float); mu=np.asarray(mu,float)
    var=max(float(var),1e-8)
    return float(-0.5*np.sum(np.log(2*math.pi*var)+(y-mu)**2/var))

def parse_num(v):
    try: return float(v)
    except: return float("nan")

def resp_right(v):
    return 1.0 if "n" in str(v).lower() else 0.0

def load_experiment(root,exp):
    pat="InfoseekFakefeed_sub*.csv" if exp=="exp1" else "InfoseekTrainingDiff_sub*.csv"
    rows=[]
    for fn in sorted(glob.glob(str(Path(root)/exp/pat))):
        with open(fn,encoding="utf-8-sig",newline="") as f:
            for r in csv.DictReader(f):
                if r.get("running")!="main": continue
                sub=str(int(float(r["sub"])))
                if exp=="exp1" and sub=="56887": sub="5"
                info=r.get("info_choice","")
                if info not in ("see again","give response"): continue
                cj=parse_num(r.get("cj"))
                rt=parse_num(r.get("rt"))
                if not (math.isfinite(cj) and 1<=cj<=6 and math.isfinite(rt) and rt>0): continue
                task=1.0 if r.get("task")=="letter" else 0.0
                if exp=="exp1":
                    manip=1.0 if r.get("fb_condition")=="positivefb" else 0.0
                else:
                    manip=1.0 if r.get("train_name")=="easy" else 0.0
                dl=parse_num(r.get("dotsLeft")); dr=parse_num(r.get("dotsRight"))
                block=parse_num(r.get("block")); trial=parse_num(r.get("withinblocktrial"))
                cor=parse_num(r.get("cor"))
                if not all(math.isfinite(x) for x in (dl,dr,block,trial,cor)): continue
                seek=1.0 if info=="see again" else 0.0
                row={
                    "sub":sub,"task":task,"manip":manip,
                    "diff":abs(dl-dr)/80.0,"logrt":math.log1p(rt),
                    "cor":cor,"right":resp_right(r.get("resp")),
                    "block":block-5.0,"trial":trial/100.0,
                    "M":cj,"seek":seek,
                    "raw":r,
                }
                rows.append(row)
    return rows

def split_rows(rows,exp,split):
    return [r for r in rows if r["sub"] in SPLITS[exp][split]]

def standards(dev):
    out={}
    for k in ("diff","logrt","M"):
        a=np.array([r[k] for r in dev],float)
        sd=float(a.std(ddof=1))
        out[k]=(float(a.mean()), sd if sd>0 else 1.0)
    return out

def z(v,st,k):
    mu,sd=st[k]; return (float(v)-mu)/sd

def policy_X(rows,st,include_M=True,override_M=None):
    X=[]; y=[]
    for i,r in enumerate(rows):
        diff=z(r["diff"],st,"diff")
        v=[1.0,r["task"],r["manip"],diff,z(r["logrt"],st,"logrt"),
           r["cor"],r["right"],r["block"],r["trial"],r["task"]*diff]
        if include_M:
            mv=r["M"] if override_M is None else override_M[i]
            v.append(z(mv,st,"M"))
        X.append(v); y.append(r["seek"])
    return np.asarray(X,float),np.asarray(y,float)

def valid_seek_rows(rows):
    out=[]
    for r in rows:
        if r["seek"]!=1: continue
        q=r["raw"]
        cj2=parse_num(q.get("cj2")); cor2=parse_num(q.get("cor2"))
        if not (math.isfinite(cj2) and 1<=cj2<=6 and cor2 in (0,1)): continue
        rr2=resp_right(q.get("resp2"))
        changed=1.0 if rr2!=r["right"] else 0.0
        u=dict(r); u.update({"M_next":cj2,"cor2":cor2,"changed":changed})
        out.append(u)
    return out

def update_standards(dev_seek):
    out={}
    for k in ("M","diff","logrt"):
        a=np.array([r[k] for r in dev_seek],float)
        sd=float(a.std(ddof=1))
        out[k]=(float(a.mean()),sd if sd>0 else 1.0)
    return out

def uz(v,st,k):
    mu,sd=st[k]; return (float(v)-mu)/sd

def update_X(rows,st,include_post=True,override_post=None):
    X=[]; y=[]
    for i,r in enumerate(rows):
        v=[1.0,uz(r["M"],st,"M"),r["task"],r["manip"],
           uz(r["diff"],st,"diff"),uz(r["logrt"],st,"logrt"),
           r["cor"],r["right"],r["block"],r["trial"]]
        if include_post:
            if override_post is None: c2,ch=r["cor2"],r["changed"]
            else: c2,ch=override_post[i]
            v.extend([c2,ch])
        X.append(v); y.append(r["M_next"])
    return np.asarray(X,float),np.asarray(y,float)

def permute_values(rows,values,tag):
    groups=defaultdict(list)
    for i,r in enumerate(rows):
        groups[(r["sub"],int(r["task"]),int(r["manip"]))].append(i)
    out=list(values)
    for key,idxs in sorted(groups.items()):
        rng=random.Random(sha_seed(EXP,tag,*key))
        vals=[out[i] for i in idxs]
        rng.shuffle(vals)
        for i,v in zip(idxs,vals): out[i]=v
    return out

def structural_gate(rows):
    bad=[]
    for r in rows:
        q=r["raw"]
        seek=r["seek"]==1
        cj2=parse_num(q.get("cj2"))
        resp2=str(q.get("resp2",""))
        valid2=(math.isfinite(cj2) and 1<=cj2<=6 and resp2!="-99")
        missing2=(str(q.get("cj2"))=="-99" and resp2=="-99")
        if seek and not valid2: bad.append((r["sub"],"seek_missing_second"))
        if (not seek) and not missing2: bad.append((r["sub"],"nonseek_has_second"))
    return {"pass":len(bad)==0,"violations":len(bad),"examples":bad[:10]}

def analyze(root,exp,flip=False):
    rows=load_experiment(root,exp)
    if flip:
        for r in rows:
            r["right"]=1.0-r["right"]
            # correctness and absolute difficulty are invariant; final response-change is
            # reconstructed after flipping both response labels below via changed identity,
            # so it is also invariant.
    dev=split_rows(rows,exp,"DEV"); val=split_rows(rows,exp,"VAL"); test=split_rows(rows,exp,"TEST")
    st=standards(dev)
    X0d,yd=policy_X(dev,st,False); X1d,_=policy_X(dev,st,True)
    b0=fit_logit(X0d,yd); b1=fit_logit(X1d,yd)
    def score_pol(rr):
        X0,y=policy_X(rr,st,False); X1,_=policy_X(rr,st,True)
        l0=ll_logit(X0,y,b0); l1=ll_logit(X1,y,b1)
        return {"n":len(y),"ll0":l0,"ll1":l1,"G":l1-l0-0.5*math.log(len(y))}
    pval=score_pol(val); ptest=score_pol(test)

    # D_MA
    mperm=permute_values(test,[r["M"] for r in test],f"{exp}|D_MA")
    X0t,yt=policy_X(test,st,False); X1p,_=policy_X(test,st,True,mperm)
    dma=ll_logit(X1p,yt,b1)-ll_logit(X0t,yt,b0)-0.5*math.log(len(yt))

    devs=valid_seek_rows(dev); vals=valid_seek_rows(val); tests=valid_seek_rows(test)
    ust=update_standards(devs)
    U0d,yud=update_X(devs,ust,False); U1d,_=update_X(devs,ust,True)
    c0=fit_ridge(U0d,yud); c1=fit_ridge(U1d,yud)
    var0=max(float(np.mean((yud-U0d@c0)**2)),1e-8)
    var1=max(float(np.mean((yud-U1d@c1)**2)),1e-8)
    def score_up(rr):
        U0,y=update_X(rr,ust,False); U1,_=update_X(rr,ust,True)
        l0=gaussian_ll(y,U0@c0,var0); l1=gaussian_ll(y,U1@c1,var1)
        return {"n":len(y),"ll0":l0,"ll1":l1,"G":l1-l0-0.5*2*math.log(len(y))}
    uval=score_up(vals); utest=score_up(tests)

    pairs=[(r["cor2"],r["changed"]) for r in tests]
    pp=permute_values(tests,pairs,f"{exp}|D_ZM")
    U0u,yu=update_X(tests,ust,False); U1p,_=update_X(tests,ust,True,pp)
    dzm=gaussian_ll(yu,U1p@c1,var1)-gaussian_ll(yu,U0u@c0,var0)-0.5*2*math.log(len(yu))

    structure=structural_gate(rows)
    return {
        "counts":{"all":len(rows),"DEV":len(dev),"VAL":len(val),"TEST":len(test),
                  "seek_DEV":len(devs),"seek_VAL":len(vals),"seek_TEST":len(tests)},
        "policy":{"DEV_M_coef":float(b1[-1]),"VAL":pval,"TEST":ptest,"D_MA_TEST_G":dma},
        "update":{"DEV_post_coefs":[float(c1[-2]),float(c1[-1])],"DEV_var0":var0,"DEV_var1":var1,
                  "VAL":uval,"TEST":utest,"D_ZM_TEST_G":dzm},
        "structure":structure,
        "loop_TEST":min(ptest["G"],utest["G"])
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("root")
    ap.add_argument("--output",default="ROX_0004A_RESULT_v1.0.json")
    args=ap.parse_args()
    res={}
    flips={}
    for exp in ("exp1","exp2"):
        res[exp]=analyze(args.root,exp,False)
        flips[exp]=analyze(args.root,exp,True)
    repdiff={}
    rep_pass=True
    for exp in ("exp1","exp2"):
        diffs={
            "policy_VAL":abs(res[exp]["policy"]["VAL"]["G"]-flips[exp]["policy"]["VAL"]["G"]),
            "policy_TEST":abs(res[exp]["policy"]["TEST"]["G"]-flips[exp]["policy"]["TEST"]["G"]),
            "update_VAL":abs(res[exp]["update"]["VAL"]["G"]-flips[exp]["update"]["VAL"]["G"]),
            "update_TEST":abs(res[exp]["update"]["TEST"]["G"]-flips[exp]["update"]["TEST"]["G"]),
        }
        repdiff[exp]=diffs
        rep_pass &= max(diffs.values())<=1e-8

    gates={}
    for exp in ("exp1","exp2"):
        r=res[exp]
        gates[f"{exp}_policy"]=(
            r["policy"]["VAL"]["G"]>LN100 and r["policy"]["TEST"]["G"]>LN100 and r["policy"]["DEV_M_coef"]<0)
        gates[f"{exp}_update"]=(r["update"]["VAL"]["G"]>LN100 and r["update"]["TEST"]["G"]>LN100)
        gates[f"{exp}_structure"]=r["structure"]["pass"]
        gates[f"{exp}_D_MA"]=r["policy"]["D_MA_TEST_G"]<=0
        gates[f"{exp}_D_ZM"]=r["update"]["D_ZM_TEST_G"]<=0
    gates["representation"]=bool(rep_pass)
    status="O2_LOOP_REPLICATED" if all(gates.values()) else "FAIL"
    out={
        "experiment":EXP,"status":status,
        "evidence_class":"empirical natural human / architectural loop test",
        "source_artifact_digest":"sha256:256e8f7c8c8cfaee22276bafd0108d25227a861c9b9aae2bceca390c6b6ce066",
        "threshold_ln100":LN100,
        "results":res,"representation_abs_gain_differences":repdiff,
        "gates":gates,
        "claim_boundary":"Maximum R2/O2 model-guided observation candidate. Not O3, not universal ROH, not Powerball evidence.",
        "eureka_status":"NONE"
    }
    Path(args.output).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
