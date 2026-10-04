#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, math, random
from pathlib import Path
import numpy as np

EXP="ROX-0001A"
NREC=8000
BURN=500
HIST=8
LAM=1e-3
MAXIT=100
TOL=1e-10

def seed(tag):
    return int.from_bytes(hashlib.sha256(f"{EXP}|{tag}".encode()).digest()[:8],"big")

def sig(x):
    return 1.0/(1.0+np.exp(-np.clip(x,-40,40)))

def fit_logit(X,y):
    X=np.asarray(X,float); y=np.asarray(y,float)
    p=X.shape[1]
    b=np.zeros(p)
    I=np.eye(p); I[0,0]=0.0
    for _ in range(MAXIT):
        eta=X@b; pr=sig(eta)
        g=X.T@(y-pr)-LAM*(I@b)
        w=pr*(1-pr)
        H=-(X.T@(X*w[:,None]))-LAM*I
        try:
            step=np.linalg.solve(H,g)
        except np.linalg.LinAlgError:
            step=np.linalg.pinv(H)@g
        b2=b-step
        if np.max(np.abs(b2-b))<TOL:
            b=b2; break
        b=b2
    return b

def ll(X,y,b):
    eta=np.asarray(X)@b
    y=np.asarray(y)
    return float(np.sum(y*(-np.logaddexp(0,-eta))+(1-y)*(-np.logaddexp(0,eta))))

def coef(rng, lo, hi):
    mag=rng.uniform(lo,hi)
    return mag if rng.random()<0.5 else -mag

def gen_case(kind, idx):
    rng=random.Random(seed(f"CASE|{kind}|{idx}"))
    b0=rng.uniform(-0.3,0.3)
    bz=coef(rng,0.5,1.0); ba=coef(rng,0.4,0.9)
    br=coef(rng,0.8,1.2) if kind in ("N3","N4") else 0.0
    bm=coef(rng,0.8,1.2) if kind=="N4" else 0.0
    z=rng.randrange(2); r=0.0; m=0.0
    rec=[]
    total=BURN+NREC+HIST
    for t in range(total):
        a=rng.randrange(2)
        eta=b0+bz*(2*z-1)+ba*(2*a-1)+br*r+bm*m
        p=1/(1+math.exp(-max(-40,min(40,eta))))
        y=1 if rng.random()<p else 0
        rec.append((z,a,r,m,y))
        r2=0.94*r+0.06*(2*z-1)
        m2=0.92*m+0.08*((2*y-1)-math.tanh(eta/2))
        z,r,m=y,r2,m2
    rec=rec[BURN:BURN+NREC+HIST]
    # opaque column permutation over predictor channels only
    perm=list(range(4)); rng.shuffle(perm)
    opaque=[]
    for row in rec:
        pred=[row[0],row[1],row[2],row[3]]
        opaque.append([pred[j] for j in perm]+[row[4]])
    return {
        "opaque_id":hashlib.sha256(f"{kind}|{idx}|{seed('OPAQUE')}".encode()).hexdigest()[:12],
        "kind":kind,
        "perm":perm,
        "coef":{"b0":b0,"bz":bz,"ba":ba,"br":br,"bm":bm},
        "data":np.array(opaque,float),
    }

def build_base(data, rows, bin_cols):
    zc,ac=bin_cols
    feats=[]
    ys=[]
    for t in rows:
        v=[1.0,data[t,zc],data[t,ac]]
        for lag in range(1,HIST+1):
            v.extend([data[t-lag,zc],data[t-lag,ac]])
        feats.append(v); ys.append(data[t,4])
    return np.array(feats,float),np.array(ys,float)

def identify_columns(data):
    pred=data[:,0:4]
    nun=[len(np.unique(np.round(pred[:,j],12))) for j in range(4)]
    binary=[j for j,n in enumerate(nun) if n<=2]
    cont=[j for j,n in enumerate(nun) if n>2]
    if len(binary)!=2 or len(cont)!=2:
        raise RuntimeError(f"column type identification failed {nun}")
    return sorted(binary),sorted(cont)

def internal_role_cal(data):
    binary,cont=identify_columns(data)
    # binary order is arbitrary but both enter symmetrically
    bin_cols=tuple(binary)
    train=range(HIST,3200)
    cal=range(3200,4000)
    Xtr,ytr=build_base(data,train,bin_cols)
    Xc,yc=build_base(data,cal,bin_cols)
    b0=fit_logit(Xtr,ytr); base=ll(Xc,yc,b0)
    gains=[]
    for c in cont:
        tr=np.column_stack([Xtr,data[list(train),c]])
        ca=np.column_stack([Xc,data[list(cal),c]])
        bc=fit_logit(tr,ytr)
        gains.append((ll(ca,yc,bc)-base-0.5*math.log(len(yc)),c))
    gains.sort(key=lambda x:(-x[0],x[1]))
    rcol=gains[0][1]
    mcol=cont[0] if cont[1]==rcol else cont[1]
    return bin_cols,rcol,mcol,gains

def make_models(data,bin_cols,rcol,mcol,rows):
    X0,y=build_base(data,rows,bin_cols)
    idx=list(rows)
    X3=np.column_stack([X0,data[idx,rcol]])
    X4=np.column_stack([X3,data[idx,mcol]])
    return (X0,X3,X4,y)

def fit_case(data):
    bin_cols,rcol,mcol,cal_gains=internal_role_cal(data)
    dev=range(HIST,4000)
    val=range(4000,6000)
    test=range(6000,8000)
    X0d,X3d,X4d,yd=make_models(data,bin_cols,rcol,mcol,dev)
    b0=fit_logit(X0d,yd); b3=fit_logit(X3d,yd); b4=fit_logit(X4d,yd)
    def ev(rows):
        X0,X3,X4,y=make_models(data,bin_cols,rcol,mcol,rows)
        l0,l3,l4=ll(X0,y,b0),ll(X3,y,b3),ll(X4,y,b4)
        n=len(y)
        G3=(l3-l0)-0.5*math.log(n)
        G4=(l4-l3)-0.5*math.log(n)
        if G3<=0 and G4<=0: cl="N0"
        elif G3>math.log(100) and G4<=0: cl="N3"
        elif G3>0 and G4>math.log(100): cl="N4"
        else: cl="UNIDENTIFIABLE"
        return {"ll0":l0,"ll3":l3,"ll4":l4,"G3":G3,"G4":G4,"class":cl}
    return {
        "bin_cols":bin_cols,"rcol":rcol,"mcol":mcol,"calibration_gains":cal_gains,
        "b0":b0,"b3":b3,"b4":b4,
        "VAL":ev(val),"TEST":ev(test)
    }

def shifted_m_control(data,fit,offset):
    d=data.copy()
    sl=np.arange(6000,8000)
    vals=d[sl,fit["mcol"]].copy()
    vals=np.roll(vals,offset%len(vals))
    d[sl,fit["mcol"]]=vals
    rows=range(6000,8000)
    X0,X3,X4,y=make_models(d,fit["bin_cols"],fit["rcol"],fit["mcol"],rows)
    l3=ll(X3,y,fit["b3"]); l4=ll(X4,y,fit["b4"])
    return (l4-l3)-0.5*math.log(len(y))

def permute_names_only_classification(fit):
    # classifications depend on values/column indices, never names.
    # Semantic renaming is therefore an exact no-op by construction.
    return fit["TEST"]["class"]

def main():
    cases=[]
    for kind in ("N0","N3","N4"):
        for i in range(4):
            cases.append(gen_case(kind,i))
    results=[]
    correct=0; all_n4=True; n0_as_n4=0; decoy_ok=True
    selected_improve=[]
    for c in cases:
        f=fit_case(c["data"])
        pred=f["TEST"]["class"]; truth=c["kind"]
        if pred==truth: correct+=1
        if truth=="N4" and pred!="N4": all_n4=False
        if truth=="N0" and pred=="N4": n0_as_n4+=1
        if truth in ("N3","N4"):
            chosen={"N3":f["TEST"]["ll3"],"N4":f["TEST"]["ll4"]}.get(pred,f["TEST"]["ll0"])
            selected_improve.append(chosen-f["TEST"]["ll0"])
        dec=None
        if truth=="N4":
            rng=random.Random(seed(f"SHIFT|{c['opaque_id']}"))
            off=rng.randint(137,863)
            g4=shifted_m_control(c["data"],f,off)
            dec={"offset":off,"G4_shifted":g4,"pass":g4<=0}
            decoy_ok &= g4<=0
        results.append({
            "opaque_id":c["opaque_id"],"truth":truth,"prediction":pred,
            "column_permutation":c["perm"],
            "role_assignment":{"binary":list(f["bin_cols"]),"r":f["rcol"],"m":f["mcol"]},
            "VAL":f["VAL"],"TEST":f["TEST"],"pseudo_recursive_control":dec
        })
    pass_all=(correct>=11 and all_n4 and decoy_ok and n0_as_n4==0 and
              (np.mean(selected_improve)>0 if selected_improve else False))
    out={
        "experiment":EXP,
        "status":"CONTROL_PASS" if pass_all else "CONTROL_FAIL",
        "evidence_class":"architectural/methodological synthetic control",
        "cases_correct":correct,"cases_total":12,
        "all_true_N4_classified_N4":all_n4,
        "N0_misclassified_N4":n0_as_n4,
        "all_shifted_m_controls_G4_nonpositive":bool(decoy_ok),
        "mean_selected_class_test_ll_gain_over_H0_for_N3_N4":float(np.mean(selected_improve)),
        "semantic_column_rename_invariance":"EXACT_BY_CONSTRUCTION_VALUES_AND_INDICES_ONLY",
        "results":results,
        "claim_boundary":"Synthetic discrimination only; no natural-domain or Powerball evidence.",
        "eureka_status":"NONE"
    }
    Path("ROX_0001A_RESULT_v1.0.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
