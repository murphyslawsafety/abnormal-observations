#!/usr/bin/env python3
from __future__ import annotations

import argparse, hashlib, json, math, pathlib, re
from collections import defaultdict

import numpy as np
import scipy.io as sio

EXP="ROX-0003A"
L2=1e-3
MAXIT=100
TOL=1e-10
LN100=math.log(100.0)

DEV={"004","016","020","023","018","008","005","025","013","006"}
VAL={"021","012","003","014","024"}
TEST={"007","010","015","022","011"}
ALL=DEV|VAL|TEST

PREGEN_SHA="c0b506e720ae6155f6132af36958cca2673e77ffbf482bb119fc4e72354fe967"
MAT_SHA={
"003":"8f0c8ff2817e9c0182fa804bc7677904867b7567f9abc9a3df90abd8d76424ed",
"004":"b3763003d6d2589cd81dd7fe44eb7adbc27cbcb3ab9923ed8f493e88d383d190",
"005":"a85dac8691f5ab0adda7ba771041fd171d491b88d8ebf6cb7508838ad0237227",
"006":"9b02b84a48e3a932a64135654b7af3a6e8c2c0d50f7b0497fe5131918ba52b06",
"007":"2813e7514fc65cf0e4cebb0d7af23313b49c7df95b741c846ac62509e1641db4",
"008":"7dab8bb2db48564e19bfa6cdb82edb096f11a816f0c50d86650e44e93389ee5b",
"010":"4e7062c2e7697ab3cc991478fb072fd74eeffb2d8500649a44cba08ff2c7080c",
"011":"e637c9c5ccfe8c2f549d9bf07ad7513f4ddf70ca1141941ccb5027f0e68f9d0a",
"012":"30b7b4379c706a09132616dc3d2fd93cff283daca68cdcb4ed39b369a7d0ebbc",
"013":"4a80057cb5162255f48c4d168faf52b72ad3b236741089421861c0b196fd8165",
"014":"2edb7f87dc2cb24fe35d0c359e9f470dcaeb1efcfad92b21acefa2568a9e992b",
"015":"eb732ca41667a2d7cc663768709c16977c77119f651bed9cee0f2c97770aa4cf",
"016":"0bea0cb1026e5a9e4a9dfc70595a267c4f23c1449dd9c08e5247cc3a187a3189",
"018":"5055c310fc10df1d1f337e572887f8c2786ae9edd115471918bb543cccbf6824",
"020":"a4ffe794b63d4699aff40c96f17d3ccd96b59f0ffffd2ccf078761ee9386c77b",
"021":"18acb1ee4c24a65ed64eb51e9356206bad0f10d10c87b84494a123d5c107be01",
"022":"a61dd3a21af74518f2c4177f887294373c9872556e43006c1ecc9d274fb6c643",
"023":"413b41f78e5d4f2ab0651835b2524a8067935edfda422ed661adf402afbffc4b",
"024":"65a2077e3d736d08206f8962e8a8d2b893ff2b44a56d3a49d9b5f1c4b378aed3",
"025":"0b8d48eb96b44fcfab17318734b2856acad81624812a881175b9d4bac22c6d5b",
}

def sha256(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()

def sigmoid(x):
    return 1/(1+np.exp(-np.clip(x,-40,40)))

def fit_logit(X,y):
    X=np.asarray(X,float); y=np.asarray(y,float)
    b=np.zeros(X.shape[1])
    I=np.eye(X.shape[1]); I[0,0]=0
    for _ in range(MAXIT):
        eta=X@b; p=sigmoid(eta)
        g=X.T@(y-p)-L2*(I@b)
        w=p*(1-p)
        H=-(X.T@(X*w[:,None]))-L2*I
        try: step=np.linalg.solve(H,g)
        except np.linalg.LinAlgError: step=np.linalg.pinv(H)@g
        b2=b-step
        if np.max(np.abs(b2-b))<TOL:
            b=b2; break
        b=b2
    return b

def bern_ll(X,y,b):
    eta=np.asarray(X)@b; y=np.asarray(y)
    return float(np.sum(y*(-np.logaddexp(0,-eta))+(1-y)*(-np.logaddexp(0,eta))))

def gaussian_fit(X,y):
    b=np.linalg.lstsq(np.asarray(X,float),np.asarray(y,float),rcond=None)[0]
    resid=np.asarray(y,float)-np.asarray(X,float)@b
    var=max(float(np.mean(resid**2)),1e-12)
    return b,var

def gaussian_ll(X,y,b,var):
    resid=np.asarray(y,float)-np.asarray(X,float)@b
    n=len(resid)
    return float(-0.5*n*math.log(2*math.pi*var)-0.5*np.sum(resid**2)/var)

def zfit(X, cont_idx):
    X=np.asarray(X,float).copy()
    mu={}; sd={}
    for j in cont_idx:
        m=float(np.mean(X[:,j])); s=float(np.std(X[:,j],ddof=1))
        if not np.isfinite(s) or s<=0: s=1.0
        mu[j]=m; sd[j]=s; X[:,j]=(X[:,j]-m)/s
    return X,mu,sd

def zapply(X,mu,sd):
    X=np.asarray(X,float).copy()
    for j,m in mu.items(): X[:,j]=(X[:,j]-m)/sd[j]
    return X

def load_evidence(path, sign=1.0):
    e=sio.loadmat(path,struct_as_record=True,squeeze_me=False)
    s=e["stimEv"]
    if s.shape!=(180,2): raise RuntimeError(f"unexpected stimEv shape {s.shape}")
    flat=[]
    for col in (0,1):
        for row in range(180):
            x=np.asarray(s[row,col],float).ravel()
            if x.size!=240: raise RuntimeError("unexpected evidence length")
            flat.append(sign*x)
    return np.asarray(flat,float)

def subject_id(path):
    m=re.search(r"SUB-(\d{3})",pathlib.Path(path).name)
    if not m: raise RuntimeError(f"cannot parse subject {path}")
    return m.group(1)

def load_subject(path,evidence):
    sid=subject_id(path)
    if sid not in ALL: return None
    if sha256(path)!=MAT_SHA[sid]: raise RuntimeError(f"hash mismatch {sid}")
    j=sio.loadmat(path,struct_as_record=True,squeeze_me=False)
    dat=np.asarray(j["data"]["data"][0,0],float)
    conf=np.asarray(j["confDat"]["conf"][0,0],float).ravel()
    inds=np.asarray(j["p"]["trialInds"][0,0],int).ravel()
    if dat.shape!=(900,10) or conf.size!=900 or inds.size!=900:
        raise RuntimeError(f"schema mismatch {sid}: {dat.shape} {conf.shape} {inds.shape}")
    rows=[]
    for i in range(900):
        base=int(inds[i])-1
        idx=base+(180 if (i%2==0) else 0)  # MATLAB odd trials 1,3,... receive +180
        if not (0<=idx<360): raise RuntimeError(f"bad evidence index {sid} {i} {idx}")
        ev=evidence[idx]
        cond=int(round(dat[i,1]))
        resp=float(dat[i,7]); correct=float(dat[i,8]); rt=float(dat[i,9]); cf=float(conf[i])
        rows.append({"sid":sid,"trial":i+1,"cond":cond,"resp":resp,"correct":correct,"rt":rt,"conf":cf,"ev":ev})
    return rows

def policy_rows(trials):
    out=[]
    for tr in trials:
        rt=tr["rt"]
        if not np.isfinite(rt) or rt<=0: continue
        event=(rt<2.0)
        stopbin=min(20,max(1,int(math.ceil(rt/0.1))))
        ev=np.asarray(tr["ev"],float)
        blocks=np.array([np.sum(ev[b*12:(b+1)*12]) for b in range(20)],float)
        cum=np.cumsum(blocks)
        for bi in range(stopbin):
            # time bin is 1..20
            recent=[blocks[bi-k] if bi-k>=0 else 0.0 for k in range(4)]
            E=float(cum[bi]); M=abs(E)
            y=1.0 if (event and bi==stopbin-1) else 0.0
            base=[1.0]
            base += [1.0 if (bi+1)==b else 0.0 for b in range(2,21)]
            base += [1.0 if tr["cond"]==c else 0.0 for c in range(2,10)]
            base += recent
            base += [E]
            h1=base+[M]
            out.append({"sid":tr["sid"],"trial":tr["trial"],"cond":tr["cond"],"bin":bi+1,"y":y,
                        "x0":base,"x1":h1,"M":M})
    return out

def conf_rows(trials):
    out=[]
    for tr in trials:
        rt=tr["rt"]; cf=tr["conf"]
        if not np.isfinite(rt) or rt<=0 or not np.isfinite(cf): continue
        frame=min(240,max(1,int(math.ceil(rt*120))))
        E=float(np.sum(tr["ev"][:frame])); M=abs(E)
        x0=[1.0]+[1.0 if tr["cond"]==c else 0.0 for c in range(2,10)]+[rt,tr["correct"],tr["resp"]]
        x1=x0+[M]
        out.append({"sid":tr["sid"],"trial":tr["trial"],"cond":tr["cond"],"y":cf,"x0":x0,"x1":x1,"M":M})
    return out

def split_rows(rows,sids):
    return [r for r in rows if r["sid"] in sids]

def matrices(rows,key):
    return np.asarray([r[key] for r in rows],float),np.asarray([r["y"] for r in rows],float)

def fit_policy(dev):
    X0,y=matrices(dev,"x0"); X1,_=matrices(dev,"x1")
    # Continuous controls: last 5 H0 columns (4 recent blocks + signed cumulative);
    # H1 adds M.
    c0=list(range(X0.shape[1]-5,X0.shape[1]))
    c1=list(range(X1.shape[1]-6,X1.shape[1]))
    X0z,mu0,sd0=zfit(X0,c0)
    X1z,mu1,sd1=zfit(X1,c1)
    return {"b0":fit_logit(X0z,y),"b1":fit_logit(X1z,y),"mu0":mu0,"sd0":sd0,"mu1":mu1,"sd1":sd1,
            "M_coef":float(fit_logit(X1z,y)[-1])}

def score_policy(rows,fit,override_M=None):
    X0,y=matrices(rows,"x0"); X1,_=matrices(rows,"x1")
    if override_M is not None: X1[:,-1]=override_M
    X0z=zapply(X0,fit["mu0"],fit["sd0"]); X1z=zapply(X1,fit["mu1"],fit["sd1"])
    l0=bern_ll(X0z,y,fit["b0"]); l1=bern_ll(X1z,y,fit["b1"])
    return {"n":len(y),"ll0":l0,"ll1":l1,"G":(l1-l0)-0.5*math.log(len(y))}

def fit_conf(dev):
    X0,y=matrices(dev,"x0"); X1,_=matrices(dev,"x1")
    # Standardize RT in C0; RT and M in C1. Correct/response are not standardized.
    rt_idx=X0.shape[1]-3
    X0z,mu0,sd0=zfit(X0,[rt_idx])
    X1z,mu1,sd1=zfit(X1,[rt_idx,X1.shape[1]-1])
    b0,v0=gaussian_fit(X0z,y); b1,v1=gaussian_fit(X1z,y)
    return {"b0":b0,"v0":v0,"b1":b1,"v1":v1,"mu0":mu0,"sd0":sd0,"mu1":mu1,"sd1":sd1,
            "M_coef":float(b1[-1])}

def score_conf(rows,fit,override_M=None):
    X0,y=matrices(rows,"x0"); X1,_=matrices(rows,"x1")
    if override_M is not None: X1[:,-1]=override_M
    X0z=zapply(X0,fit["mu0"],fit["sd0"]); X1z=zapply(X1,fit["mu1"],fit["sd1"])
    l0=gaussian_ll(X0z,y,fit["b0"],fit["v0"]); l1=gaussian_ll(X1z,y,fit["b1"],fit["v1"])
    return {"n":len(y),"ll0":l0,"ll1":l1,"G":(l1-l0)-0.5*math.log(len(y))}

def seed_for(*parts):
    return int.from_bytes(hashlib.sha256("|".join([EXP,*map(str,parts)]).encode()).digest()[:8],"big")

def destroy_policy_M(rows):
    arr=np.asarray([r["M"] for r in rows],float)
    out=arr.copy()
    groups=defaultdict(list)
    for i,r in enumerate(rows): groups[(r["sid"],r["cond"],r["bin"])].append(i)
    for key,idx in groups.items():
        rng=np.random.default_rng(seed_for("D1",*key))
        vals=out[idx].copy(); rng.shuffle(vals); out[idx]=vals
    return out

def destroy_conf_M(rows):
    arr=np.asarray([r["M"] for r in rows],float)
    out=arr.copy()
    groups=defaultdict(list)
    for i,r in enumerate(rows): groups[(r["sid"],r["cond"])].append(i)
    for key,idx in groups.items():
        rng=np.random.default_rng(seed_for("D2",*key))
        vals=out[idx].copy(); rng.shuffle(vals); out[idx]=vals
    return out

def analyze(subject_paths,pregen,sign=1.0,controls=True):
    if sha256(pregen)!=PREGEN_SHA: raise RuntimeError("preGen hash mismatch")
    ev=load_evidence(pregen,sign=sign)
    trials=[]
    for p in subject_paths:
        x=load_subject(p,ev)
        if x is not None: trials.extend(x)
    got={r["sid"] for r in trials}
    if got!=ALL: raise RuntimeError(f"subject set mismatch {sorted(got)}")
    prows=policy_rows(trials); crows=conf_rows(trials)
    pd,pv,pt=[split_rows(prows,s) for s in (DEV,VAL,TEST)]
    cd,cv,ct=[split_rows(crows,s) for s in (DEV,VAL,TEST)]
    pf=fit_policy(pd); cf=fit_conf(cd)
    pval=score_policy(pv,pf); ptest=score_policy(pt,pf)
    cval=score_conf(cv,cf); ctest=score_conf(ct,cf)
    out={"policy":{"DEV_rows":len(pd),"VAL":pval,"TEST":ptest,"M_coef_DEV":pf["M_coef"]},
         "confidence":{"DEV_trials":len(cd),"VAL":cval,"TEST":ctest,"M_coef_DEV":cf["M_coef"]},
         "trial_counts":{"DEV":len(cd),"VAL":len(cv),"TEST":len(ct)}}
    if controls:
        d1=score_policy(pt,pf,destroy_policy_M(pt))
        d2=score_conf(ct,cf,destroy_conf_M(ct))
        out["controls"]={"D1_policy_alignment":d1,"D2_confidence_alignment":d2}
    return out

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--subjects-dir",required=True)
    ap.add_argument("--pregen",required=True)
    ap.add_argument("--output",default="ROX_0003A_RESULT_v1.0.json")
    args=ap.parse_args()
    paths=sorted(pathlib.Path(args.subjects_dir).glob("*.mat"))
    actual=analyze(paths,args.pregen,sign=1.0,controls=True)
    flipped=analyze(paths,args.pregen,sign=-1.0,controls=False)
    diffs={
        "policy_VAL_G":abs(actual["policy"]["VAL"]["G"]-flipped["policy"]["VAL"]["G"]),
        "policy_TEST_G":abs(actual["policy"]["TEST"]["G"]-flipped["policy"]["TEST"]["G"]),
        "conf_VAL_G":abs(actual["confidence"]["VAL"]["G"]-flipped["confidence"]["VAL"]["G"]),
        "conf_TEST_G":abs(actual["confidence"]["TEST"]["G"]-flipped["confidence"]["TEST"]["G"]),
    }
    rep_pass=max(diffs.values())<=1e-8
    gates={
        "policy_VAL":actual["policy"]["VAL"]["G"]>LN100,
        "policy_TEST":actual["policy"]["TEST"]["G"]>LN100,
        "confidence_VAL":actual["confidence"]["VAL"]["G"]>LN100,
        "confidence_TEST":actual["confidence"]["TEST"]["G"]>LN100,
        "policy_M_positive":actual["policy"]["M_coef_DEV"]>0,
        "confidence_M_positive":actual["confidence"]["M_coef_DEV"]>0,
        "D1_destroyed":actual["controls"]["D1_policy_alignment"]["G"]<=0,
        "D2_destroyed":actual["controls"]["D2_confidence_alignment"]["G"]<=0,
        "representation":rep_pass,
    }
    status="O2_CANDIDATE_SUPPORT" if all(gates.values()) else "FAIL"
    result={"experiment":EXP,"status":status,"evidence_class":"empirical natural-domain R2/O2 candidate",
            "actual":actual,"sign_flipped":{"policy":flipped["policy"],"confidence":flipped["confidence"]},
            "representation_abs_gain_differences":diffs,"representation_pass":rep_pass,
            "gates":gates,
            "claim_boundary":"At most model-guided observation candidate evidence in one human task; not O3, not universal ROH, not Powerball evidence.",
            "eureka_status":"NONE"}
    pathlib.Path(args.output).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
