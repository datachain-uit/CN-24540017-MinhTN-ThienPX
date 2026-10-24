# Phiếu đọc: [Pereira & Torezzan, 2024] – Huấn luyện một bộ, kiểm tra bộ khác   (mã trích dẫn trong báo cáo: [31])

- Người đọc: Phạm Xuân Thiên   Ngày: …/10/2026   Thời gian đọc: … giờ
- Nơi công bố và hạng: SBPO – *Simpósio Brasileiro de Pesquisa Operacional* (hội nghị Brazil). **Chưa tra được hạng CORE** — nhiều khả năng không có trong danh mục CORE
- DOI / link bản chính thức: **chưa tìm được**
- **Chưa truy cập được toàn văn.**

> 🔴 **PHIẾU NÀY CHƯA LÀM ĐƯỢC — và có một phát hiện quan trọng kèm theo.** Đọc kỹ mục dưới.

---

## 🚨 PHÁT HIỆN: có một công trình gần đề tài hơn hẳn, cùng nhóm tác giả

Khi tìm bài SBPO 2024, nhóm tra ra một **luận văn UNICAMP năm 2025** của cùng tác giả thứ nhất:

| | |
|---|---|
| **Tên** | *Aprimoramento da predição de turnover voluntário por meio da transferência de aprendizado* <br> (Nâng cao dự đoán nghỉ việc tự nguyện bằng học chuyển giao) |
| **Tác giả** | João Pedro de Lima Pereira |
| **Hướng dẫn** | Cristiano Torezzan *(ghi trong lời cảm ơn)* |
| **Đơn vị** | Universidade Estadual de Campinas (UNICAMP), Brazil |
| **Năm** | 2025 (công bố 31/10/2025) |
| **DOI** | <https://doi.org/10.47749/t/unicamp.2025.1546748> |
| **Truy cập** | Mở, nhưng kho UNICAMP chặn tải tự động |
| **Ngôn ngữ** | Tiếng Bồ Đào Nha |

**Nội dung theo mô tả của OpenAlex:** học chuyển giao bằng **TrAdaBoost** trên **hai bộ dữ liệu HR công khai**, mô hình được thích ứng sang miền đích bằng **một số ít mẫu có nhãn**.

### Vì sao điều này quan trọng với đề tài

Đây gần như **trùng khớp với câu hỏi nghiên cứu của TB-HTL**:

| | Luận văn UNICAMP 2025 | TB-HTL |
|---|---|---|
| Bài toán | Dự đoán nghỉ việc tự nguyện | Dự đoán rủi ro nghỉ việc |
| Hướng tiếp cận | Học chuyển giao | Học chuyển giao |
| Dữ liệu | Hai bộ HR công khai | Bốn miền HR công khai |
| Thiết lập | Thích ứng sang miền đích với **ít mẫu có nhãn** | Đúng thiết lập của Cổng 0: k ∈ {10, 20, 50, …} |
| Phương pháp | TrAdaBoost | Các baseline chuyển giao + TB-HTL |

**Việc cần làm gấp — nhóm phải quyết hai điều:**

1. **Luận văn này có phải là bản mở rộng của bài SBPO [31] không?** Nếu đúng, nó là **công trình gần đề tài nhất trong toàn bộ danh mục tài liệu**, gần hơn cả [11] Levin và [24] CARTE.
2. **TrAdaBoost có nên thêm vào danh sách baseline chuyển giao của Cổng 0 không?** Hiện `g0_23.py` có 8 baseline (ZS, STK_LR, STK_XGB, OFF_XGB, DAUME_LR, RANKAVG, ANCHOR_LR, RANKAVG_RF) nhưng **không có TrAdaBoost** — vốn là thuật toán chuyển giao kinh điển cho đúng tình huống *ít nhãn ở miền đích*.

> **Lưu ý về phạm vi:** đánh giá 22/10 ghi *"Tài liệu tham khảo: danh sách baseline giữ nguyên theo Phụ lục D của review 07/10, **không bổ sung baseline mới**."* Nên việc thêm TrAdaBoost **phải hỏi ý GVHD trước**, không tự ý làm. Nhưng phát hiện này cần báo cáo.

---

## 1. Bài toán

*(theo ghi chú sẵn có trong `bang1_phuong_phap_luan.csv`)*

Huấn luyện mô hình trên **một bộ dữ liệu Kaggle**, kiểm tra trên **một bộ khác**. Hai bộ chung 6 thuộc tính, **cùng ngữ nghĩa nhãn**.

Đây là lý do [31] được xếp vào nhóm ưu tiên: `docs/phieu_doc/README.md` ghi *"Gần đề tài nhất: huấn luyện một bộ, kiểm tra bộ khác"*.

## 2. Dữ liệu

Hai bộ dữ liệu Kaggle, chung 6 thuộc tính. **Tên cụ thể: ?**

Báo cáo tiến độ 22/10 (mục A2) ghi miền C — HR 14.999 dòng — *"đã được [8] và [31] dùng"*. Nên nhiều khả năng một trong hai bộ của [31] chính là **miền C** của nhóm.

Số dòng, số cột, tỷ lệ dương: **?**

## 3. Giao thức đánh giá

| Mục | Bài làm gì | Trang/mục trong bài |
|---|---|---|
| Metric báo cáo | **Chỉ accuracy** *(đã ghi sẵn trong Bảng 1)* | ? |
| Chia dữ liệu | Huấn luyện trên một bộ Kaggle; kiểm tra trên bộ khác *(đã ghi sẵn)* | ? |
| Mất cân bằng | **?** — trước hay sau khi chia | ? |
| Chọn siêu tham số | **?** | ? |
| Kiểm định thống kê, khoảng tin cậy | **?** | ? |
| Công bố mã, dữ liệu | **?** | ? |
| Rủi ro rò rỉ thông tin | **?** | ? |

## 4. Kết quả chính

**?** — chưa đọc được.

**Có dùng làm mốc so sánh được không?** Đáng chú ý là bài **chỉ báo cáo accuracy**. Với dữ liệu nghỉ việc mất cân bằng, accuracy không cho biết mô hình bắt được bao nhiêu ca nghỉ việc. Nếu bài chỉ có accuracy thì **không so trực tiếp với PR-AUC của nhóm được**.

## 5. Hạn chế

**Do tác giả nêu:** **?**

**Do nhóm nhận xét:**
- Chỉ dùng accuracy — thiếu thước đo phù hợp với mất cân bằng.
- Chỉ 6 thuộc tính chung giữa hai bộ, tương đương mức của cặp AB (4 khái niệm) và thấp hơn cặp AC (5–8 khái niệm) của nhóm.
- *(bổ sung sau khi đọc)*

## 6. Liên hệ với đề tài TB-HTL

**Dùng ở đâu:** Bảng 1, và là **công trình đối chứng gần nhất** — bài duy nhất trong danh mục [1]–[10], [31], [43] có thiết lập *huấn luyện một bộ, kiểm tra bộ khác*.

**Có chuyển giao xuyên nguồn không: CÓ** — đây là điểm khác biệt so với mọi bài còn lại trong Bảng 1.

**Khác gì với TB-HTL:**

| | Pereira & Torezzan [31] | TB-HTL |
|---|---|---|
| Chuyển giao xuyên bộ | Có | Có |
| Ngữ nghĩa nhãn | Cùng ngữ nghĩa | Khảo sát **cả hai**: cùng (AC, AD) và khác (AB) |
| Số khái niệm chung | 6 | 3 (AD), 4 (AB), 5–8 (AC) |
| Thước đo | Chỉ accuracy | PR-AUC, AUC-ROC, kiểm định có hiệu chỉnh |
| Có baseline chỉ dùng đích không | **?** | Có — và là tiêu chí GO/PIVOT |

**Điểm mấu chốt cần kiểm khi đọc được bài:** [31] có so sánh với **baseline chỉ dùng dữ liệu đích** không? Nếu không, thì bài chưa trả lời được câu hỏi *chuyển giao có thực sự giúp ích hay không* — và đó chính là chỗ TB-HTL khác biệt, vì Cổng 0 của nhóm lấy đúng tiêu chí này làm căn cứ GO/PIVOT.

---

## Ô cần điền vào `bang1_phuong_phap_luan.csv` (dòng `[31]`)

Đã có sẵn: `metric_bao_cao` = *Chỉ accuracy*; `giao_thuc_chia` = *Huấn luyện trên một bộ Kaggle; kiểm tra trên bộ khác*; `rui_ro_ro_ri_ghi_chu` = *Hai bộ chung 6 thuộc tính; cùng ngữ nghĩa nhãn*.

Còn thiếu: `mat_can_bang_truoc_hay_sau_chia`, `cong_bo_ma`, `trang_nguon` — **đều cần toàn văn**.

---

## Việc còn lại của phiếu này

**Không làm được gì thêm nếu không có bài.** Ba hướng, theo thứ tự ưu tiên:

1. **Hỏi Minh** — bài này nằm trong danh mục [31] của nhóm, nên nhiều khả năng Minh đã có PDF khi lập Bảng 1.
2. **Tra kỷ yếu Galoá** — SBPO 2024 (LVI, Fortaleza, 04–07/11/2024): <https://proceedings.science/sbpo/sbpo-2024> → tìm theo tác giả *Torezzan*. Trang này chặn truy cập tự động nhưng mở bằng trình duyệt được.
3. **Tải luận văn UNICAMP 2025** ở link trên — dù không phải bài [31], nó gần đề tài hơn và **cần báo cáo với GVHD**.
