#!/usr/bin/env python3
from __future__ import annotations

import argparse, csv, hashlib, json, math, random
from collections import defaultdict
from pathlib import Path

import numpy as np

EXP="ROX-0007A"
LAM=1e-3
LN100=math.log(100.0)

DEV={"18","14","20","15","26","25","10","22","19","24"}
VAL={"11","7","21","2"}
TEST={"1","13","17","9"}

def seed(*parts):
    return int.from_bytes(hashlib.sha256("|".join(map(str,parts)).encode()).digest()[:8],"big")

def num(x):
    try: return float(x)
    except: return float("nan")

def left(v):
    return str(v).strip().lower()=="left"

def load_csv(path, fixed=False, flip=False):
    rows=[]
    with open(path,encoding="utf-8-sig",newline="") as f:
        for r in csv.DictReader(f):
            sub=str(int(float(r["participant"])))
            vals={k:num(r.get(k)) for k in (
                "Trial","Block","RT1","Conf1","Conf2","Correct1",
                "DotNumberLeft","DotNumberRight","DotDifference",
                "LeftTime","RightTime"
            )}
            if fixed:
                vals["Left_Presentation_Time"]=num(r.get("Left_Presentation_Time"))
                vals["Right_Presentation_Time"]=num(r.get("Right_Presentation_Time"))
            if not all(math.isfinite(v) for v in vals.values()): continue
            resp=str(r.get("Response1","")).strip().lower()
            if resp not in ("left","right"): continue
            dl,dr=vals["DotNumberLeft"],vals["DotNumberRight"]
            lt,rt=vals["LeftTime"],vals["RightTime"]
            if fixed:
                lp,rp=vals["Left_Presentation_Time"],vals["Right_Presentation_Time"]
            if flip:
                dl,dr=dr,dl
                lt,rt=rt,lt
                resp="right" if resp=="left" else "left"
                if fixed: lp,rp=rp,lp
            isleft=(resp=="left")
            chosen=lt if isleft else rt
            unchosen=rt if isleft else lt
            if fixed:
                chosen_plan=lp if isleft else rp
                unchosen_plan=rp if isleft else lp
                A=chosen_plan-unchosen_plan
                total=chosen_plan+unchosen_plan
            else:
                A=chosen-unchosen
                total=chosen+unchosen
            row={
                "sub":sub,
                "trial":vals["Trial"]/200.0,
                "block":vals["Block"]/8.0,
                "logrt":math.log1p(max(vals["RT1"],0.0)),
                "M":vals["Conf1"],
                "M_next":vals["Conf2"],
                "cor":vals["Correct1"],
                "left":1.0 if isleft else 0.0,
                "diff":abs(dl-dr),
                "A":A,
                "total":total,
            }
            if all(math.isfinite(v) for k,v in row.items() if k!="sub"):
                rows.append(row)
    return rows

def which_split(sub):
    if sub in DEV:return "DEV"
    if sub in VAL:return "VAL"
    if sub in TEST:return "TEST"
    raise RuntimeError(f"unexpected participant {sub}")

def split(rows,name):
    return [r for r in rows if which_split(r["sub"])==name]

def stats(dev, keys):
    s={}
    for k in keys:
        a=np.asarray([r[k] for r in dev],float)
        sd=float(a.std(ddof=1))
        s[k]=(float(a.mean()), sd if sd>0 else 1.0)
    return s

def zz(v,st,k):
    mu,sd=st[k]
    return (float(v)-mu)/sd

def fit_ridge(X,y):
    X=np.asarray(X,float); y=np.asarray(y,float)
    I=np.eye(X.shape[1]);I[0,0]=0.0
    return np.linalg.solve(X.T@X+LAM*I,X.T@y)

def gll(y,mu,var):
    y=np.asarray(y,float);mu=np.asarray(mu,float);var=max(float(var),1e-12)
    return float(-.5*np.sum(np.log(2*math.pi*var)+(y-mu)**2/var))

def policy_X(rows,st,full=True,override_M=None):
    X=[];y=[]
    for i,r in enumerate(rows):
        v=[1.0,zz(r["diff"],st,"diff"),zz(r["logrt"],st,"logrt"),
           r["cor"],r["left"],r["block"],r["trial"],zz(r["total"],st,"total")]
        if full:
            mv=r["M"] if override_M is None else override_M[i]
            v.append(zz(mv,st,"M"))
        X.append(v); y.append(r["A"])
    return np.asarray(X,float),np.asarray(y,float)

def update_X(rows,st,full=True,override_A=None):
    X=[];y=[]
    for i,r in enumerate(rows):
        v=[1.0,zz(r["M"],st,"M"),zz(r["diff"],st,"diff"),
           zz(r["logrt"],st,"logrt"),r["cor"],r["left"],
           r["block"],r["trial"],zz(r["total"],st,"total")]
        if full:
            av=r["A"] if override_A is None else override_A[i]
            v.append(zz(av,st,"A"))
        X.append(v);y.append(r["M_next"])
    return np.asarray(X,float),np.asarray(y,float)

def fit_policy(rows):
    dev=split(rows,"DEV")
    st=stats(dev,("diff","logrt","total","M"))
    X0,y=policy_X(dev,st,False); X1,_=policy_X(dev,st,True)
    b0=fit_ridge(X0,y);b1=fit_ridge(X1,y)
    v0=max(float(np.mean((y-X0@b0)**2)),1e-12)
    v1=max(float(np.mean((y-X1@b1)**2)),1e-12)
    return st,b0,b1,v0,v1

def score_policy(rows,fit,name,override_M=None):
    st,b0,b1,v0,v1=fit
    rr=split(rows,name)
    X0,y=policy_X(rr,st,False)
    X1,_=policy_X(rr,st,True,override_M)
    l0=gll(y,X0@b0,v0);l1=gll(y,X1@b1,v1)
    return {"n":len(y),"ll0":l0,"ll1":l1,"G":l1-l0-.5*math.log(len(y))}

def fit_update(rows):
    dev=split(rows,"DEV")
    st=stats(dev,("M","diff","logrt","total","A"))
    X0,y=update_X(dev,st,False);X1,_=update_X(dev,st,True)
    b0=fit_ridge(X0,y);b1=fit_ridge(X1,y)
    v0=max(float(np.mean((y-X0@b0)**2)),1e-12)
    v1=max(float(np.mean((y-X1@b1)**2)),1e-12)
    return st,b0,b1,v0,v1

def score_update(rows,fit,name,override_A=None):
    st,b0,b1,v0,v1=fit
    rr=split(rows,name)
    X0,y=update_X(rr,st,False);X1,_=update_X(rr,st,True,override_A)
    l0=gll(y,X0@b0,v0);l1=gll(y,X1@b1,v1)
    return {"n":len(y),"ll0":l0,"ll1":l1,"G":l1-l0-.5*math.log(len(y))}

def permute_within_subject(rows, values, tag):
    out=list(values);groups=defaultdict(list)
    for i,r in enumerate(rows): groups[r["sub"]].append(i)
    for sub,idxs in sorted(groups.items()):
        rng=random.Random(seed(EXP,"CONTROL",tag,sub))
        vv=[out[i] for i in idxs];rng.shuffle(vv)
        for i,v in zip(idxs,vv):out[i]=v
    return out

def analyse(root,flip=False):
    free=load_csv(Path(root)/"exp2_data_free.csv",False,flip)
    fixed=load_csv(Path(root)/"exp2_data_fixed.csv",True,flip)
    if set(r["sub"] for r in free)!=DEV|VAL|TEST: raise RuntimeError("free participant set mismatch")
    if set(r["sub"] for r in fixed)!=DEV|VAL|TEST: raise RuntimeError("fixed participant set mismatch")

    pf=fit_policy(free);px=fit_policy(fixed)
    uf=fit_update(free);ux=fit_update(fixed)

    res={"counts":{
        "free":{s:len(split(free,s)) for s in ("DEV","VAL","TEST")},
        "fixed":{s:len(split(fixed,s)) for s in ("DEV","VAL","TEST")}
    }}
    res["policy_free"]={
        "DEV_M_coef":float(pf[2][-1]),
        "VAL":score_policy(free,pf,"VAL"),
        "TEST":score_policy(free,pf,"TEST")
    }
    res["policy_fixed"]={
        "DEV_M_coef":float(px[2][-1]),
        "VAL":score_policy(fixed,px,"VAL"),
        "TEST":score_policy(fixed,px,"TEST")
    }
    res["update_free"]={
        "DEV_A_coef":float(uf[2][-1]),
        "VAL":score_update(free,uf,"VAL"),
        "TEST":score_update(free,uf,"TEST")
    }
    res["update_fixed_diagnostic"]={
        "DEV_A_coef":float(ux[2][-1]),
        "VAL":score_update(fixed,ux,"VAL"),
        "TEST":score_update(fixed,ux,"TEST")
    }

    for s in ("VAL","TEST"):
        res.setdefault("agency",{})[s]=res["policy_free"][s]["G"]-res["policy_fixed"][s]["G"]
        res.setdefault("loop",{})[s]=min(res["policy_free"][s]["G"],res["agency"][s],res["update_free"][s]["G"])

    tf=split(free,"TEST")
    mp=permute_within_subject(tf,[r["M"] for r in tf],"D_MA")
    res["D_MA_TEST_G"]=score_policy(free,pf,"TEST",mp)["G"]
    ap=permute_within_subject(tf,[r["A"] for r in tf],"D_ZM")
    res["D_ZM_TEST_G"]=score_update(free,uf,"TEST",ap)["G"]
    return res

def main():
    ap=argparse.ArgumentParser();ap.add_argument("root");ap.add_argument("--output",default="ROX_0007A_RESULT_v1.0.json")
    args=ap.parse_args()
    r=analyse(args.root,False);rf=analyse(args.root,True)

    diffs={}
    for path in (
        ("policy_free","VAL"),("policy_free","TEST"),
        ("policy_fixed","VAL"),("policy_fixed","TEST"),
        ("update_free","VAL"),("update_free","TEST")
    ):
        k="/".join(path)
        diffs[k]=abs(r[path[0]][path[1]]["G"]-rf[path[0]][path[1]]["G"])
    rep_pass=max(diffs.values())<=1e-8

    gates={
        "free_policy_VAL":r["policy_free"]["VAL"]["G"]>LN100,
        "free_policy_TEST":r["policy_free"]["TEST"]["G"]>LN100,
        "free_policy_direction":r["policy_free"]["DEV_M_coef"]>0,
        "agency_VAL":r["agency"]["VAL"]>LN100,
        "agency_TEST":r["agency"]["TEST"]>LN100,
        "fixed_policy_VAL_not_strong":r["policy_fixed"]["VAL"]["G"]<=LN100,
        "fixed_policy_TEST_not_strong":r["policy_fixed"]["TEST"]["G"]<=LN100,
        "update_VAL":r["update_free"]["VAL"]["G"]>LN100,
        "update_TEST":r["update_free"]["TEST"]["G"]>LN100,
        "update_direction":r["update_free"]["DEV_A_coef"]>0,
        "loop_VAL":r["loop"]["VAL"]>LN100,
        "loop_TEST":r["loop"]["TEST"]>LN100,
        "D_MA":r["D_MA_TEST_G"]<=0,
        "D_ZM":r["D_ZM_TEST_G"]<=0,
        "representation":rep_pass
    }
    status="O2_ACTIVE_LOOP_SUPPORT" if all(gates.values()) else "FAIL"
    out={
        "experiment":EXP,"status":status,
        "evidence_class":"empirical natural human / active-observation loop",
        "threshold_ln100":LN100,
        "results":r,
        "representation_abs_gain_differences":diffs,
        "gates":gates,
        "claim_boundary":"Maximum R2/O2 natural model-guided observation candidate. Not O3, not universal ROH, not Powerball evidence.",
        "eureka_status":"NONE"
    }
    Path(args.output).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
