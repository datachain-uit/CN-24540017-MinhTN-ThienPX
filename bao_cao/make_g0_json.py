import pandas as pd, json, numpy as np
F='results/g0_23/'
c=pd.read_csv(F+'g0_bang_duong_cong.csv'); c['k']=c.k.astype(str)
T=pd.read_csv(F+'g0_kiem_dinh_GO.csv')
S3=pd.read_csv(F+'g0_doi_chung_xao_tron.csv'); S3['k']=S3.k.astype(str)
NAME={"LR":"LR","RF":"Random Forest","XGB":"XGBoost","CAT":"CatBoost","STACK":"Stacking LR + RF + XGB [5]","TabPFN":"TabPFN v2 [25]",
 "ZS":"Zero-shot từ nguồn (C1)","STK_LR":"Stacking điểm nguồn + LR","STK_XGB":"Stacking điểm nguồn + XGBoost","OFF_XGB":"XGBoost khởi tạo từ nguồn",
 "DAUME_LR":"Tăng cường Daumé [33] + LR","RANKAVG":"Trung bình hạng w(k)","ANCHOR_LR":"LR neo hệ số nguồn","RANKAVG_RF":"Trung bình hạng RF + nguồn (pilot GVHD)"}
f=lambda v: f"{v:.3f}".replace('.',',')
fs=lambda v: (f"{v:+.3f}").replace('.',',').replace('-','−')
KS=["10","20","50","100","200","500","full"]; TO=["LR","RF","XGB","CAT","STACK","TabPFN"]
out={}
for t in "AB":
    rows=[]; ct=c[c.target==t]
    for fam,ms in (("Chỉ dữ liệu đích",TO),("Chuyển giao",["ZS","STK_LR","STK_XGB","OFF_XGB","DAUME_LR","RANKAVG","ANCHOR_LR","RANKAVG_RF"])):
        rows.append([{"span":8,"text":f"**{fam}**","shade":"F2F2F2"}])
        for m in ms:
            cm=ct[ct.method==m].set_index('k').pr_auc
            if m=="ZS":
                rows.append([NAME[m],{"span":7,"text":f(cm['zero'])+" – không dùng nhãn đích, như nhau ở mọi k"}]); continue
            row=[NAME[m]]
            for k in KS:
                v=cm.get(k,np.nan)
                best=ct[(ct.k==k)&ct.method.isin(TO)].pr_auc.max()
                if np.isnan(v): row.append("–" + (" (vượt 10.000 dòng)" if m=="TabPFN" else ""))
                else: row.append(f"**{f(v)}**" if abs(v-best)<1e-12 and fam=="Chỉ dữ liệu đích" else f(v))
            rows.append(row)
    out['curve'+t]=rows
    g=T[T.target==t]; rows=[]
    for k in [10,20,50]:
        gk=g[g.k==k]; b=gk.iloc[0]; best=gk.loc[gk.delta.idxmax()]
        rows.append([str(k), f"{NAME[b.best_target_only]} ({f(b.base_pr)})", f"{NAME[best.method]} ({f(best.method_pr)})", fs(best.delta),
                     f"[{fs(best.ci_lo)}; {fs(best.ci_hi)}]", f(best.p_holm).replace('1,000','1,00'), "Không"])
    out['go'+t]=rows
    s=S3[S3.target==t]
    out['ctrl'+t]={m:{k:dict(d=fs(r.delta),lo=fs(r.ci_lo),hi=fs(r.ci_hi),p=f(r.p_corr)) for k,r in s[s.method==m].set_index('k').iterrows()} for m in s.method.unique()}
json.dump(out,open('bao_cao/g0.json','w'),ensure_ascii=False,indent=1)
print(out['goA']); print(out['goB'])
