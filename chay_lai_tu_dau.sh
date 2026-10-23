#!/usr/bin/env bash
# Huấn luyện lại TOÀN BỘ phần CPU từ dữ liệu gốc (cần 4 file trong data/, xem data/README.md).
# Tổng thời gian khoảng 6–7 giờ CPU. Mỗi lần chạy ghi kết quả vào results/<thư mục>/ với tên chứa mã băm cấu hình,
# nên chạy lại với cấu hình khác sẽ ra file mới, không ghi đè hay dùng lại kết quả cũ.
# TabPFN v2 chạy riêng trên Colab GPU: notebooks/chay_TabPFN_v2_Cong0_Colab.ipynb và notebooks/chay_TabPFN_v2_R1_R3_Colab.ipynb.
set -euo pipefail
cd "$(dirname "$0")"
A=data/WA_Fn-UseC_-HR-Employee-Attrition.csv; B=data/aug_train.csv; C=data/HR_comma_sep.csv; D=data/turnover.csv
CPU="LR RF XGB CAT STACK ZS STK_LR STK_XGB OFF_XGB DAUME_LR RANKAVG ANCHOR_LR ZS_SHUF STK_LR_SHUF RANKAVG_SHUF ANCHOR_LR_SHUF"

python kb1_v2.py --ibm $A --jc $B --out results/kb1_v2                     # KB1 v2 cặp AB (~15 phút)
python kb1_tai_dung.py --ibm $A --jc $B                                    # A5.1c truy vết bảng KB1 cũ (~5 phút)
python g0_23.py --ibm $A --jc $B --only LR RF XGB ZS STK_LR STK_XGB OFF_XGB DAUME_LR --suffix cpu   # Cổng 0 AB, phần chính (~12 phút)
python g0_23.py --ibm $A --jc $B --only CAT STACK RANKAVG ANCHOR_LR ZS_SHUF STK_LR_SHUF RANKAVG_SHUF ANCHOR_LR_SHUF --suffix extra   # (~35 phút)
python g0_pair.py --pair AB --data A=$A B=$B --only RANKAVG_RF RANKAVG_RF_SHUF --suffix rankrf --out results/g0_23

python kb1_pair.py --pair AC --data A=$A C=$C                              # 2×2 cặp AC
python g0_pair.py  --pair AC --data A=$A C=$C --only $CPU --suffix cpu     # Cổng 0 AC (~35 phút cho đích C)
python g0_pair.py  --pair AC --data A=$A C=$C --only RANKAVG_RF RANKAVG_RF_SHUF --suffix rankrf
python g0_pair.py  --pair AC --cset consistent --data A=$A C=$C --only $CPU --suffix cpu
python g0_pair.py  --pair AC --cset consistent --data A=$A C=$C --only RANKAVG_RF RANKAVG_RF_SHUF --suffix rankrf

python kb1_pair.py --pair AD --data A=$A D=$D                              # 2×2 cặp AD
python g0_pair.py  --pair AD --data A=$A D=$D --only $CPU --suffix cpu     # Cổng 0 AD (~32 phút cho đích D)
python g0_pair.py  --pair AD --data A=$A D=$D --only RANKAVG_RF RANKAVG_RF_SHUF --suffix rankrf

python tbhtl_thamdo_nn.py --pair AB --data A=$A B=$B --targets A                # thăm dò TB-HTL MLP 23/10 (~10 phút CPU)

bash tai_lap_bang.sh && python kiem_tra_tai_lap.py
