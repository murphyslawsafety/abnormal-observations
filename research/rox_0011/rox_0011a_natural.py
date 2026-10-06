#!/usr/bin/env python3
from __future__ import annotations

import argparse, json, math, random, hashlib
from dataclasses import dataclass
from pathlib import Path

import h5py
import numpy as np
import pandas as pd

EXP="ROX-0011A"
FRAME_DT=0.49528
LAM=1e-3
KPC=3
LN100=math.log(100.0)

def seed(tag):
    return int.from_bytes(hashlib.sha256(f"{EXP}|{tag}".encode()).digest()[:8],"big")

def split_name(t):
    if t < 80.0: return "DEV"
    if t < 160.0: return "VAL"
    return "TEST"

def coarse_frames(stack, reflect=False):
    x=np.asarray(stack,float)
    if reflect:
        x=x[:,:,::-1]
    # exact 300x175 -> 30x35 nonoverlapping block means
    if x.shape[1:] != (300,175):
        raise RuntimeError(f"unexpected image shape {x.shape}")
    x=x.reshape(x.shape[0],30,10,35,5).mean(axis=(2,4))
    return x.reshape(x.shape[0],-1)

def fit_pca(stack, reflect=False):
    X=coarse_frames(stack,reflect)
    times=np.arange(X.shape[0])*FRAME_DT
    dev=times < 80.0
    mu=X[dev].mean(axis=0)
    sd=X[dev].std(axis=0,ddof=1)
    sd=np.where(np.isfinite(sd)&(sd>0),sd,1.0)
    Xz=(X-mu)/sd
    U,S,Vt=np.linalg.svd(Xz[dev],full_matrices=False)
    V=Vt[:KPC].T
    scores=Xz@V
    var=S*S
    evr=(var[:KPC]/var.sum()).tolist()
    tol=max(Xz[dev].shape)*np.finfo(float).eps*S[0]
    nz=S[S>tol]
    diag={
        "dev_frames":int(dev.sum()),
        "singular_values_first10":[float(v) for v in S[:10]],
        "explained_variance_ratio_first3":[float(v) for v in evr],
        "effective_rank":int(len(nz)),
        "condition_number_nonzero":float(nz[0]/nz[-1]) if len(nz) else float("inf")
    }
    return scores,diag

def interval_mean(df,t0,t1,col):
    x=df[(df["t"]>=t0)&(df["t"]<t1)][col]
    if len(x)==0: return float("nan")
    return float(pd.to_numeric(x,errors="coerce").mean())

def build_rows(scores,est,stim):
    n=len(scores)
    rows=[]
    for i in range(n-1):
        t0=i*FRAME_DT; t1=(i+1)*FRAME_DT
        if split_name(t0)!=split_name(t1):
            continue
        vig=interval_mean(est,t0,t1,"vigour")
        z=interval_mean(stim,t0,t1,"closed loop 1D_vel")
        b=interval_mean(stim,t0,t1,"closed loop 1D_base_vel")
        g=interval_mean(stim,t0,t1,"closed loop 1D_gain")
        f=interval_mean(stim,t0,t1,"closed loop 1D_fish_swimming")
        vals=(vig,z,b,g,f)
        if not all(math.isfinite(x) for x in vals): continue
        rows.append({
            "i":i,"t":t0,"split":split_name(t0),
            "A":math.log1p(max(0.0,vig)),
            "Z":z,"B":b,"G":g,"F":f,
            "M":scores[i].copy(),"Mnext":scores[i+1].copy()
        })
    # attach previous action/observation based on exact frame predecessor
    by_i={r["i"]:r for r in rows}
    out=[]
    for r in rows:
        p1=by_i.get(r["i"]-1); p2=by_i.get(r["i"]-2)
        if p1 is None or p2 is None: continue
        if p1["split"]!=r["split"] or p2["split"]!=r["split"]: continue
        rr=dict(r)
        rr["A1"]=p1["A"]; rr["A2"]=p2["A"]; rr["Z1"]=p1["Z"]
        out.append(rr)
    return out

@dataclass
class Scaler:
    mu: np.ndarray
    sd: np.ndarray
    def transform(self,X):
        return (X-self.mu)/self.sd

def fit_scaler(X):
    X=np.asarray(X,float)
    mu=X.mean(axis=0)
    sd=X.std(axis=0,ddof=1)
    sd=np.where(np.isfinite(sd)&(sd>0),sd,1.0)
    return Scaler(mu,sd)

def add_intercept(X):
    X=np.asarray(X,float)
    return np.column_stack([np.ones(len(X)),X])

def fit_ridge(X,y):
    X=np.asarray(X,float); y=np.asarray(y,float)
    I=np.eye(X.shape[1]); I[0,0]=0.0
    return np.linalg.solve(X.T@X+LAM*I,X.T@y)

def gaussian_ll(y,mu,var):
    y=np.asarray(y,float); mu=np.asarray(mu,float)
    var=np.maximum(np.asarray(var,float),1e-10)
    return float(-0.5*np.sum(np.log(2*np.pi*var)+(y-mu)**2/var))

def ridge_model(train_X,train_y):
    sc=fit_scaler(train_X)
    X=add_intercept(sc.transform(train_X))
    beta=fit_ridge(X,train_y)
    resid=np.asarray(train_y)-X@beta
    if resid.ndim==1: var=float(np.mean(resid*resid))
    else: var=np.mean(resid*resid,axis=0)
    return {"sc":sc,"beta":beta,"var":var}

def model_ll(model,X,y):
    XX=add_intercept(model["sc"].transform(np.asarray(X,float)))
    return gaussian_ll(y,XX@model["beta"],model["var"])

def rows_of(rows,sp):
    return [r for r in rows if r["split"]==sp]

def e2_X(rows,full=True,M_override=None):
    X=[]
    for j,r in enumerate(rows):
        v=[r["A1"],r["A2"],r["Z1"],r["B"],r["G"]]
        if full:
            m=r["M"] if M_override is None else M_override[j]
            v.extend(map(float,m))
        X.append(v)
    return np.asarray(X,float)

def e3_X(rows,full=True,A_override=None):
    X=[]
    for j,r in enumerate(rows):
        a=r["A"] if A_override is None else A_override[j]
        v=[r["B"],r["G"]]
        if full: v.extend([a,a*r["G"]])
        X.append(v)
    return np.asarray(X,float)

def e4_X(rows,full=True,Z_override=None):
    X=[]
    for j,r in enumerate(rows):
        v=list(map(float,r["M"]))+[r["A"],r["B"],r["G"]]
        if full:
            z=r["Z"] if Z_override is None else Z_override[j]
            v.append(z)
        X.append(v)
    return np.asarray(X,float)

def gain_scalar(m0,m1,X0,X1,y,k):
    n=len(y)
    if n<5: return {"n":n,"G":float("nan"),"ll0":float("nan"),"ll1":float("nan")}
    l0=model_ll(m0,X0,y); l1=model_ll(m1,X1,y)
    return {"n":n,"ll0":l0,"ll1":l1,"G":l1-l0-0.5*k*math.log(n)}

def prepare_models(rows):
    dev=rows_of(rows,"DEV")
    # E2
    y2=np.array([r["A"] for r in dev])
    m20=ridge_model(e2_X(dev,False),y2)
    m21=ridge_model(e2_X(dev,True),y2)

    # E3 active only
    active=[r for r in dev if (r["G"]>=0.5 or (r["G"]<0.5 and r["B"]<=-5))]
    y3=np.array([r["Z"] for r in active])
    m30=ridge_model(e3_X(active,False),y3)
    m31=ridge_model(e3_X(active,True),y3)

    # E4
    y4=np.vstack([r["Mnext"] for r in dev])
    m40=ridge_model(e4_X(dev,False),y4)
    m41=ridge_model(e4_X(dev,True),y4)
    return (m20,m21,m30,m31,m40,m41)

def score(rows,models):
    m20,m21,m30,m31,m40,m41=models
    out={}
    for sp in ("VAL","TEST"):
        rr=rows_of(rows,sp)
        y2=np.array([r["A"] for r in rr])
        out[f"E2_{sp}"]=gain_scalar(m20,m21,e2_X(rr,False),e2_X(rr,True),y2,3)

        closed=[r for r in rr if r["G"]>=0.5]
        opn=[r for r in rr if r["G"]<0.5 and r["B"]<=-5]
        yc=np.array([r["Z"] for r in closed]); yo=np.array([r["Z"] for r in opn])
        out[f"E3_closed_{sp}"]=gain_scalar(m30,m31,e3_X(closed,False),e3_X(closed,True),yc,2)
        out[f"E3_open_{sp}"]=gain_scalar(m30,m31,e3_X(opn,False),e3_X(opn,True),yo,2)

        y4=np.vstack([r["Mnext"] for r in rr])
        out[f"E4_{sp}"]=gain_scalar(m40,m41,e4_X(rr,False),e4_X(rr,True),y4,3)

        vals=[out[f"E2_{sp}"]["G"],out[f"E3_closed_{sp}"]["G"],out[f"E4_{sp}"]["G"]]
        out[f"L_LOOP_{sp}"]=float(min(vals)) if all(math.isfinite(v) for v in vals) else float("nan")
    return out

def destruction(rows,models):
    m20,m21,m30,m31,m40,m41=models
    test=rows_of(rows,"TEST")
    # E2 neural shift
    mseq=[r["M"] for r in test]
    mshift=np.roll(np.asarray(mseq),37,axis=0)
    y2=np.array([r["A"] for r in test])
    d2=gain_scalar(m20,m21,e2_X(test,False),e2_X(test,True,mshift),y2,3)["G"]

    # E3 action shift within closed test
    closed=[r for r in test if r["G"]>=0.5]
    ashift=np.roll(np.array([r["A"] for r in closed]),31)
    yc=np.array([r["Z"] for r in closed])
    d3=gain_scalar(m30,m31,e3_X(closed,False),e3_X(closed,True,ashift),yc,2)["G"]

    # E4 permute Z within rounded schedule strata
    zperm=np.array([r["Z"] for r in test],float)
    groups={}
    for i,r in enumerate(test):
        key=(round(r["B"],3),round(r["G"],3))
        groups.setdefault(key,[]).append(i)
    for key,idxs in sorted(groups.items()):
        vals=list(zperm[idxs])
        rng=random.Random(seed(f"D_E4|{key}"))
        rng.shuffle(vals)
        for i,v in zip(idxs,vals): zperm[i]=v
    y4=np.vstack([r["Mnext"] for r in test])
    d4=gain_scalar(m40,m41,e4_X(test,False),e4_X(test,True,zperm),y4,3)["G"]
    return {"D_E2_TEST_G":float(d2),"D_E3_TEST_G":float(d3),"D_E4_TEST_G":float(d4)}

def analyze(root,reflect=False):
    root=Path(root)
    sess=root/"example_imaging"/"181113_f1"
    with h5py.File(sess/"stack.hdf5","r") as h:
        stack=np.asarray(h["data"],float)
    scores,diag=fit_pca(stack,reflect=reflect)
    est=pd.read_hdf(sess/"160136_estimator_log.hdf5")
    stim=pd.read_hdf(sess/"160136_stimulus_log.hdf5")
    rows=build_rows(scores,est,stim)
    models=prepare_models(rows)
    sc=score(rows,models)
    dest=destruction(rows,models)
    counts={
        "rows_total":len(rows),
        "DEV":sum(r["split"]=="DEV" for r in rows),
        "VAL":sum(r["split"]=="VAL" for r in rows),
        "TEST":sum(r["split"]=="TEST" for r in rows),
        "VAL_closed":sum(r["split"]=="VAL" and r["G"]>=0.5 for r in rows),
        "TEST_closed":sum(r["split"]=="TEST" and r["G"]>=0.5 for r in rows),
        "VAL_open":sum(r["split"]=="VAL" and r["G"]<0.5 and r["B"]<=-5 for r in rows),
        "TEST_open":sum(r["split"]=="TEST" and r["G"]<0.5 and r["B"]<=-5 for r in rows),
    }
    return {"pca":diag,"counts":counts,"scores":sc,"destruction":dest}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("root")
    ap.add_argument("--output",default="ROX_0011A_RESULT_v1.0.json")
    args=ap.parse_args()

    orig=analyze(args.root,False)
    refl=analyze(args.root,True)

    keys=[
        "E2_VAL","E2_TEST","E3_closed_VAL","E3_closed_TEST",
        "E3_open_VAL","E3_open_TEST","E4_VAL","E4_TEST"
    ]
    diffs={k:abs(orig["scores"][k]["G"]-refl["scores"][k]["G"]) for k in keys}
    rep_pass=max(diffs.values())<=1e-6

    s=orig["scores"]; d=orig["destruction"]; p=orig["pca"]
    gates={
        "E2_VAL":s["E2_VAL"]["G"]>LN100,
        "E2_TEST":s["E2_TEST"]["G"]>LN100,
        "E3_closed_VAL":s["E3_closed_VAL"]["G"]>LN100,
        "E3_closed_TEST":s["E3_closed_TEST"]["G"]>LN100,
        "E3_open_VAL":s["E3_open_VAL"]["G"]<=0,
        "E3_open_TEST":s["E3_open_TEST"]["G"]<=0,
        "E4_VAL":s["E4_VAL"]["G"]>LN100,
        "E4_TEST":s["E4_TEST"]["G"]>LN100,
        "D_E2":d["D_E2_TEST_G"]<=0,
        "D_E3":d["D_E3_TEST_G"]<=0,
        "D_E4":d["D_E4_TEST_G"]<=0,
        "representation":bool(rep_pass),
        "finite_rank":bool(p["effective_rank"]>=KPC and math.isfinite(p["condition_number_nonzero"]))
    }
    status="NATURAL_CLOSED_LOOP" if all(gates.values()) else "FAIL"
    out={
        "experiment":EXP,
        "status":status,
        "evidence_class":"empirical natural vertebrate closed sensorimotor-observation loop",
        "threshold_ln100":LN100,
        "source_md5":"eb6dc08c900aff6112f0d3bb4d06be82",
        "original":orig,
        "reflected":refl,
        "representation_abs_gain_differences":diffs,
        "gates":gates,
        "claim_boundary":"Natural N3/closed active-observation architecture only; not O3 self-model recursion, not universal ROH, not Powerball evidence.",
        "eureka_status":"NONE"
    }
    Path(args.output).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
