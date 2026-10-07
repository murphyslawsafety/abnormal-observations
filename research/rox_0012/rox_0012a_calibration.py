import json
from pathlib import Path
import numpy as np

power=np.array([0.0,36.8,73.5,110.3,147.1,183.8,220.6,257.4,294.2,330.9,367.7,459.6,551.5,643.5,717.0])
x=power/power.max()
curves={
"N5":np.array([0.9849,0.8317,0.8174,0.7899,0.7184,0.7035,0.5836,0.4886,0.4850,0.4199,0.4530,0.4133,0.3660,0.3637,0.3577]),
"N10":np.array([0.9849,0.7219,0.6223,0.5478,0.4696,0.4468,0.3930,0.3723,0.3480,0.2926,0.3134,0.2946,0.2819,0.2716,0.2816]),
"N15":np.array([0.9849,0.7462,0.6785,0.5706,0.4440,0.3610,0.2868,0.2474,0.2043,0.2063,0.1808,0.1444,0.1326,0.1152,0.0954])}

def spearman(a,b):
    ra=np.empty(len(a)); rb=np.empty(len(b))
    ra[np.argsort(a)]=np.arange(len(a))
    rb[np.argsort(b)]=np.arange(len(b))
    return float(np.corrcoef(ra,rb)[0,1])

per={}; b1=True; b4n=0
for k,y in curves.items():
    lo=(x>0)&(x<0.6); hi=x>=0.6
    ls=float(np.polyfit(x[lo],y[lo],1)[0])
    hs=float(np.polyfit(x[hi],y[hi],1)[0])
    rho=spearman(x,y)
    g1=bool(y[0]>y[-1] and rho<0 and y[hi].mean()<y[lo].mean())
    g4=bool(ls<0 and abs(hs)<abs(ls))
    b1=b1 and g1; b4n+=int(g4)
    per[k]={"rho":rho,"zero":float(y[0]),"strongest":float(y[-1]),
            "low_mean":float(y[lo].mean()),"high_mean":float(y[hi].mean()),
            "low_slope":ls,"high_slope":hs,"B1":g1,"B4":g4}
ordered=[]
for i in range(1,len(x)):
    ok=bool(curves["N15"][i]<=curves["N10"][i]<=curves["N5"][i])
    ordered.append({"I":float(x[i]),"pass":ok})
nord=sum(int(z["pass"]) for z in ordered)
b1f=bool(nord>=11 and curves["N15"][-1]<curves["N10"][-1]<curves["N5"][-1])
b4=bool(b4n>=2)
status="BACKACTION_REGIME_CALIBRATION_PASS" if b1 and b1f and b4 else "CONTROL_FAIL"
out={"experiment":"ROX-0012A","status":status,"per_frequency":per,
     "frequency":{"ordered":nord,"total":14,"pass":b1f,"details":ordered},
     "regime":{"boundary":0.6,"conditions_passing":b4n,"pass":b4},
     "gates":{"B1":b1,"B1F":b1f,"B4":b4},
     "evidence_class":"known-physics natural calibration","eureka_status":"NONE",
     "canonical_eureka_tally":6}
Path("ROX_0012A_RESULT_v1.0.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
print(json.dumps(out,indent=2,sort_keys=True))
