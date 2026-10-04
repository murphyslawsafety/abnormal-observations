#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, math, random
from pathlib import Path
from collections import defaultdict
import numpy as np

EXP="ROX-0002A"
RHO=0.985
MDEC=0.94
LAM=1e-3
MAXIT=100
TOL=1e-10
BURN=500
NREC=12000
HIST=8
LN100=math.log(100.0)

def seed(tag):
    return int.from_bytes(hashlib.sha256(f"{EXP}|{tag}".encode()).digest()[:8],"big")

def sha_bit(tag):
    return 1 if (seed(tag)&1) else -1

def sigmoid(x):
    return 1.0/(1.0+np.exp(-np.clip(x,-40,40)))

def fit_logit(X,y):
    X=np.asarray(X,float); y=np.asarray(y,float)
    p=X.shape[1]
    b=np.zeros(p)
    I=np.eye(p); I[0,0]=0.0
    for _ in range(MAXIT):
        eta=X@b
        pr=sigmoid(eta)
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

def loglik(X,y,b):
    eta=np.asarray(X)@b
    y=np.asarray(y)
    return float(np.sum(y*(-np.logaddexp(0,-eta))+(1-y)*(-np.logaddexp(0,eta))))

def make_streams(kind,idx,n,tag):
    rng=random.Random(seed(f"{tag}|{kind}|{idx}"))
    ctx=[rng.randrange(4) for _ in range(n)]
    uy=[rng.random() for _ in range(n)]
    ua=[rng.random() for _ in range(n)]
    uz=[rng.random() for _ in range(n)]
    changes=[rng.randrange(4) for _ in range((n//500)+2)]
    return ctx,uy,ua,uz,changes

def coef(kind,idx,name,lo,hi):
    rng=random.Random(seed(f"COEF|{kind}|{idx}|{name}"))
    mag=rng.uniform(lo,hi)
    return mag*sha_bit(f"SIGN|{kind}|{idx}|{name}")

def initial_thetas(kind,idx):
    vals=[0.20,0.35,0.65,0.80]
    rng=random.Random(seed(f"THETA|{kind}|{idx}"))
    rng.shuffle(vals)
    return vals

def run_sim(kind,idx,b0,tag,n,return_rows=True):
    ctx,uy,ua,uz,changes=make_streams(kind,idx,n,tag)
    theta=initial_thetas(kind,idx)
    alpha=[1.0]*4; beta=[1.0]*4
    m=0.5
    zprev=0
    cprev=-1
    rows=[]
    b1=coef(kind,idx,"b1",0.7,1.1) if kind=="O1" else 0.0
    b2=coef(kind,idx,"b2",0.7,1.1) if kind=="O1" else 0.0
    bu=coef(kind,idx,"bu",1.2,1.8) if kind in ("O2","O3") else 0.0
    bm=coef(kind,idx,"bm",1.2,1.8) if kind=="O3" else 0.0
    q_rng=random.Random(seed(f"Q|{kind}|{idx}"))
    q=q_rng.uniform(0.25,0.55)
    for t in range(n):
        if t>0 and t%500==0:
            cc=changes[t//500]
            theta[cc]=1.0-theta[cc]
        c=ctx[t]
        p=alpha[c]/(alpha[c]+beta[c])
        u=(alpha[c]*beta[c])/(((alpha[c]+beta[c])**2)*(alpha[c]+beta[c]+1.0))
        U=max(-4.0,min(4.0,(u-0.0030)/0.0015))
        M=max(-4.0,min(4.0,(m-0.35)/0.10))
        if kind=="O0":
            pa=q
        elif kind=="O1":
            eta=b0+b1*(2*zprev-1)+b2*(1.0 if c==cprev else 0.0)
            pa=float(sigmoid(eta))
        elif kind=="O2":
            pa=float(sigmoid(b0+bu*U))
        else:
            pa=float(sigmoid(b0+bu*U+bm*M))
        a=1 if ua[t]<pa else 0
        y=1 if uy[t]<theta[c] else 0
        fidelity=0.95 if a==1 else 0.70
        z=y if uz[t]<fidelity else 1-y
        if return_rows:
            rows.append((c,a,z))
        alpha[c]=RHO*alpha[c]+z
        beta[c]=RHO*beta[c]+1-z
        m=MDEC*m+(1-MDEC)*abs(z-p)
        zprev=z; cprev=c
    return rows, (sum(r[1] for r in rows)/len(rows) if rows else 0.0)

def solve_intercept(kind,idx):
    if kind=="O0": return None
    lo,hi=-6.0,6.0
    target=0.40
    for _ in range(36):
        mid=(lo+hi)/2
        rows,_=run_sim(kind,idx,mid,"PILOT",2000,True)
        rate=sum(r[1] for r in rows)/len(rows)
        if rate<target: lo=mid
        else: hi=mid
    return (lo+hi)/2

def generate_case(kind,idx):
    b0=solve_intercept(kind,idx)
    rows,_=run_sim(kind,idx,0.0 if b0 is None else b0,"MAIN",BURN+NREC,True)
    rows=rows[BURN:]
    arr=np.asarray(rows,int)
    return {
        "opaque_id":hashlib.sha256(f"{kind}|{idx}|{seed('OPAQUE')}".encode()).hexdigest()[:12],
        "kind":kind,
        "b0":b0,
        "data":arr
    }

def reconstruct_states(data):
    n=len(data)
    alpha=[1.0]*4; beta=[1.0]*4
    m=0.5
    uhat=np.zeros(n); mhat=np.zeros(n); phat=np.zeros(n)
    for t in range(n):
        c=int(data[t,0]); z=int(data[t,2])
        p=alpha[c]/(alpha[c]+beta[c])
        u=(alpha[c]*beta[c])/(((alpha[c]+beta[c])**2)*(alpha[c]+beta[c]+1.0))
        phat[t]=p; uhat[t]=u; mhat[t]=m
        alpha[c]=RHO*alpha[c]+z
        beta[c]=RHO*beta[c]+1-z
        m=MDEC*m+(1-MDEC)*abs(z-p)
    mu_u,sd_u=float(np.mean(uhat[:6000])),float(np.std(uhat[:6000],ddof=1))
    mu_m,sd_m=float(np.mean(mhat[:6000])),float(np.std(mhat[:6000],ddof=1))
    if sd_u<=0 or sd_m<=0: raise RuntimeError("degenerate reconstructed state")
    U=(uhat-mu_u)/sd_u
    M=(mhat-mu_m)/sd_m
    return U,M

def base_features(data,t):
    c=int(data[t,0])
    v=[1.0]
    v.extend([1.0 if c==k else 0.0 for k in (1,2,3)])
    for lag in range(1,9): v.append(float(data[t-lag,2]))
    for lag in range(1,9): v.append(float(data[t-lag,1]))
    for lag in range(1,5): v.append(1.0 if int(data[t-lag,0])==c else 0.0)
    zprev=float(data[t-1,2])
    v.extend([(1.0 if c==k else 0.0)*zprev for k in (1,2,3)])
    return v

def h0_features(data,t):
    c=int(data[t,0])
    return [1.0]+[1.0 if c==k else 0.0 for k in (1,2,3)]

def matrices(data,U,M,rows):
    idx=list(rows)
    X0=np.asarray([h0_features(data,t) for t in idx],float)
    X1=np.asarray([base_features(data,t) for t in idx],float)
    X2=np.column_stack([X1,U[idx]])
    X3=np.column_stack([X2,M[idx]])
    y=np.asarray([data[t,1] for t in idx],float)
    return X0,X1,X2,X3,y

def fit_case(data):
    U,M=reconstruct_states(data)
    dev=range(HIST,6000)
    X0d,X1d,X2d,X3d,yd=matrices(data,U,M,dev)
    b0=fit_logit(X0d,yd); b1=fit_logit(X1d,yd); b2=fit_logit(X2d,yd); b3=fit_logit(X3d,yd)
    def ev(rows, M_override=None, y_override=None):
        MM=M if M_override is None else M_override
        X0,X1,X2,X3,y=matrices(data,U,MM,rows)
        if y_override is not None: y=np.asarray(y_override,float)
        l0,l1,l2,l3=[loglik(X,y,b) for X,b in ((X0,b0),(X1,b1),(X2,b2),(X3,b3))]
        n=len(y)
        kextra=X1.shape[1]-X0.shape[1]
        Gh=(l1-l0)-0.5*kextra*math.log(n)
        G2=(l2-l1)-0.5*math.log(n)
        G3=(l3-l2)-0.5*math.log(n)
        if G2<=0 and G3<=0:
            cl="O1" if Gh>LN100 else "O0"
        elif G2>LN100 and G3<=0:
            cl="O2"
        elif G2>0 and G3>LN100:
            cl="O3"
        else:
            cl="UNIDENTIFIABLE"
        return {"ll0":l0,"ll1":l1,"ll2":l2,"ll3":l3,"Gh":Gh,"G2":G2,"G3":G3,"class":cl}
    return {"U":U,"M":M,"b0":b0,"b1":b1,"b2":b2,"b3":b3,
            "VAL":ev(range(6000,9000)),"TEST":ev(range(9000,12000)),"eval":ev}

def destroy_m_controls(data,fit,opaque_id):
    M=fit["M"].copy()
    test_idx=np.arange(9000,12000)
    rng=random.Random(seed(f"MCTRL|{opaque_id}"))
    off=rng.randint(257,997)
    out={}
    Ms=M.copy(); Ms[test_idx]=np.roll(M[test_idx],off)
    out["shift"]=fit["eval"](range(9000,12000),Ms)["G3"]
    Mp=M.copy()
    for c in range(4):
        inds=[t for t in test_idx if int(data[t,0])==c]
        vals=Mp[inds].copy()
        rr=random.Random(seed(f"MPERM|{opaque_id}|{c}")); order=list(range(len(vals))); rr.shuffle(order)
        Mp[inds]=vals[order]
    out["within_context_permute"]=fit["eval"](range(9000,12000),Mp)["G3"]
    Mr=M.copy(); Mr[test_idx]=M[test_idx][::-1]
    out["reverse"]=fit["eval"](range(9000,12000),Mr)["G3"]
    out["offset"]=off
    out["pass"]=all(out[k]<=0 for k in ("shift","within_context_permute","reverse"))
    return out

def policy_decoy(data,fit,opaque_id):
    d=data.copy()
    rng=random.Random(seed(f"POLICYDECOY|{opaque_id}"))
    for c in range(4):
        inds=[t for t in range(9000,12000) if int(d[t,0])==c]
        vals=[int(d[t,1]) for t in inds]
        rng.shuffle(vals)
        for t,v in zip(inds,vals): d[t,1]=v
    U,M=reconstruct_states(d)
    X0,X1,X2,X3,y=matrices(d,U,M,range(9000,12000))
    l0,l1,l2,l3=[loglik(X,y,b) for X,b in ((X0,fit["b0"]),(X1,fit["b1"]),(X2,fit["b2"]),(X3,fit["b3"]))]
    n=len(y); kextra=X1.shape[1]-X0.shape[1]
    Gh=(l1-l0)-0.5*kextra*math.log(n); G2=(l2-l1)-0.5*math.log(n); G3=(l3-l2)-0.5*math.log(n)
    if G2<=0 and G3<=0: cl="O1" if Gh>LN100 else "O0"
    elif G2>LN100 and G3<=0: cl="O2"
    elif G2>0 and G3>LN100: cl="O3"
    else: cl="UNIDENTIFIABLE"
    return {"Gh":Gh,"G2":G2,"G3":G3,"class":cl,"pass":cl not in ("O2","O3")}

def relabel_case(data):
    d=data.copy()
    # context permutation
    cmap={0:2,1:0,2:3,3:1}
    d[:,0]=np.array([cmap[int(x)] for x in d[:,0]])
    # policy label flip
    d[:,1]=1-d[:,1]
    return d

def main():
    cases=[generate_case(k,i) for k in ("O0","O1","O2","O3") for i in range(4)]
    results=[]; correct=0
    all_o2=True; all_o3=True; no_o0_hi=True
    controls_ok=True; decoys_ok=True; relabel_mismatch=0
    selected_gain=[]
    for c in cases:
        f=fit_case(c["data"])
        pred=f["TEST"]["class"]; truth=c["kind"]
        correct += int(pred==truth)
        if truth=="O2" and pred!="O2": all_o2=False
        if truth=="O3" and pred!="O3": all_o3=False
        if truth=="O0" and pred in ("O2","O3"): no_o0_hi=False
        if truth in ("O2","O3"):
            chosen=f["TEST"]["ll2"] if pred=="O2" else (f["TEST"]["ll3"] if pred=="O3" else f["TEST"]["ll1"])
            selected_gain.append(chosen-f["TEST"]["ll1"])
        ctr=None; dec=None
        if truth=="O3":
            ctr=destroy_m_controls(c["data"],f,c["opaque_id"]); controls_ok &= ctr["pass"]
        if truth in ("O2","O3"):
            dec=policy_decoy(c["data"],f,c["opaque_id"]); decoys_ok &= dec["pass"]
        rd=relabel_case(c["data"])
        rf=fit_case(rd)
        if rf["TEST"]["class"]!=pred: relabel_mismatch+=1
        results.append({
            "opaque_id":c["opaque_id"],"truth":truth,"prediction":pred,
            "VAL":f["VAL"],"TEST":f["TEST"],
            "reflexive_destruction":ctr,"policy_marginal_decoy":dec,
            "relabel_prediction":rf["TEST"]["class"]
        })
    mean_gain=float(np.mean(selected_gain)) if selected_gain else float("nan")
    passed=(correct>=15 and all_o2 and all_o3 and no_o0_hi and controls_ok and decoys_ok
            and relabel_mismatch==0 and mean_gain>0)
    out={
        "experiment":EXP,
        "status":"CONTROL_PASS" if passed else "CONTROL_FAIL",
        "evidence_class":"architectural/methodological synthetic control",
        "cases_correct":correct,"cases_total":16,
        "all_true_O2_classified_O2":all_o2,
        "all_true_O3_classified_O3":all_o3,
        "no_O0_false_O2_O3":no_o0_hi,
        "all_O3_destruction_controls_pass":bool(controls_ok),
        "all_O2_O3_policy_decoys_fail_high_class":bool(decoys_ok),
        "semantic_relabel_mismatch_count":relabel_mismatch,
        "mean_selected_class_test_ll_gain_over_H1_for_O2_O3":mean_gain,
        "results":results,
        "claim_boundary":"Synthetic closed-loop discrimination only; no natural-domain or Powerball evidence.",
        "eureka_status":"NONE"
    }
    Path("ROX_0002A_RESULT_v1.0.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
