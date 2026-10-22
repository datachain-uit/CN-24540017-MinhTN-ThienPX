const fs = require('fs');
const path = require('path');
const ROOT = path.join(__dirname, '..');
const { Document, Packer, Paragraph, TextRun, AlignmentType, HeadingLevel, PageNumber, Footer, PageBreak } = require('docx');
const L = require('./lib');
const { P, H, B, numbered, Caption, TCap, Marker, table, image } = L;
const REFS = require('./refs');
const K = JSON.parse(fs.readFileSync(__dirname + '/kb1_trong_bao_cao.json', 'utf8'));
const G0 = JSON.parse(fs.readFileSync(__dirname + '/g0_trong_bao_cao.json', 'utf8'));
const PJ = JSON.parse(fs.readFileSync(__dirname + '/pairs_trong_bao_cao.json', 'utf8'));
const G = ROOT + '/results/kb1_AB/tong_hop_hinh.png';
const C3 = ROOT + '/kb2b_carte/hinh/hinh3_carte_duongcong.png';
const C4 = ROOT + '/kb2b_carte/hinh/hinh4_carte_tuongquan.png';
const S = 'F2F2F2', OK = 'E2EFDA', PART = 'FFF2CC', TODO = 'FCE4D6';
const st = (t) => ({ text: t, shade: t.startsWith('Đã') ? OK : t.startsWith('Một phần') || t.startsWith('Đang') ? PART : TODO });
const C = [];

// ============================================================ title
C.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 60 }, children: [new TextRun({ text: 'B. MÔ TẢ NGHIÊN CỨU', bold: true, size: 32 })] }));
C.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 60 }, children: [new TextRun({ text: 'Ứng dụng học chuyển giao để dự đoán rủi ro nghỉ việc của lực lượng lao động dựa trên các nguồn dữ liệu nhân sự khác nhau', bold: true, size: 26 })] }));
C.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 200 }, children: [new TextRun({ text: 'Bản sửa theo đánh giá của GVHD ngày 07/10/2026 · Tăng Nhật Minh (24540017), Phạm Xuân Thiên (24540028) · GVHD: ThS. Nguyễn Thị Anh Thư · cập nhật 21/10/2026', italics: true, size: 22 })] }));

// ============================================================ 0. response to review
C.push(H(1, 'Phản hồi đánh giá ngày 07/10/2026'));
C.push(P('Bản này sửa toàn bộ các vấn đề trong báo cáo đánh giá của GVHD. Thay đổi lớn nhất là kết quả sơ khởi KB1 đã được chạy lại với năm họ mô hình (kể cả TabPFN v2) theo giao thức mới (G0-1), và đoạn tính cấp thiết được viết lại theo kết quả này: khi mô hình có điều chuẩn và thang đo được căn chỉnh theo miền, chuyển giao không dùng nhãn đích từ Job Change sang IBM giảm không có ý nghĩa thống kê (0,621 so với 0,644 AUC-ROC với Logistic Regression), không còn “ngang mức ngẫu nhiên” như bản cũ. Bảng dưới đây ánh xạ từng ý kiến tới phần đã sửa; ô màu xanh là đã xong, vàng là một phần hoặc đang làm, cam là việc nhóm còn phải làm trước buổi Cổng 0 ngày 21/10.'));
C.push(TCap('Bảng 0. Phản hồi theo từng ý kiến đánh giá.'));
C.push(table([700, 2350, 4100, 1150, 1060], ['Mã', 'Ý kiến (tóm tắt)', 'Đã sửa / bổ sung', 'Vị trí', 'Trạng thái'], [
  ['R1', 'Kết quả KB1 phụ thuộc Random Forest', 'Chạy lại KB1 v2: LR (L2), RF mặc định, RF có điều chuẩn, XGBoost, TabPFN v2 và quy tắc “− kinh nghiệm”; 10 lần chia; CI 95% và corrected resampled t-test [40], hiệu chỉnh Holm; viết lại tính cấp thiết. TabPFN v2 chạy trên Colab GPU (G0-2 ngày 18/10; thiết kế 2×2 ngày 21/10).', 'B1.2, B1.3, A5.1, A5.4', st('Đã sửa (21/10): TabPFN v2 có trong thiết kế 2×2 (Bảng 4, Hình 3)')],
  ['R2', 'Tuyên bố “lần đầu” chưa chính xác; thiếu công trình gần', 'Bỏ “lần đầu”; thêm Pereira & Torezzan [31] vào Bảng 1; Bảng 2 thêm [32]–[39], [44] và cột “khác biệt so với TB-HTL”; sửa mô tả CARTE và TransTab. Nhật ký truy vấn Scopus do nhóm bổ sung.', 'B1.1, B1.2', st('Đã sửa')],
  ['R3', 'Một cặp dữ liệu không đủ để kiểm chứng giả thuyết về nhãn', 'Thêm cặp cùng ngữ nghĩa nhãn IBM ↔ HR Analytics 14.999 dòng (KB8, RQ4) và danh sách ứng viên cặp thứ ba; loại Dataset01; mô tả quần thể và định nghĩa nhãn từng bộ.', 'A2, A5.5', st('Đã sửa (21/10): thêm cặp A↔C (cùng nghĩa, mô phỏng) và A↔D (cùng nghĩa, dữ liệu thật), đủ TabPFN v2')],
  ['O1', 'Cửa sổ cho chuyển giao hẹp; thiếu tiêu chí thành công', 'Thêm Cổng 0 với tiêu chí GO/PIVOT; bảng câu hỏi – giả thuyết – tiêu chí bác bỏ; mốc của TB-HTL đặt theo baseline mạnh nhất (LR đủ đặc trưng 0,829 AUC-ROC / 0,610 PR-AUC ở IBM thay cho mốc 0,49). Cổng 0 đã chạy ngày 17/10 (G0-2 đến G0-4): kết luận PIVOT ở cả hai chiều (A5.4).', 'B2.1, B2.3', st('Đã sửa')],
  ['O2', 'TB-HTL dễ bị xem là ghép các thành phần có sẵn', 'Định vị lại đóng góp theo thứ tự (a) giao thức, (b) khi nào chuyển giao có ích, (c) TB-HTL đơn giản có ablation; mỗi thành phần có giả thuyết cơ chế; thêm đối chứng nhãn nguồn xáo trộn.', 'B1.1, B1.2, B2.1', st('Đã sửa')],
  ['O3', 'Thiết kế thống kê thiếu lực; KB2 cố định mẫu downstream', 'Viết splits.py (file chia chung, k lồng nhau, R = 30, có kiểm thử); kiểm định có hiệu chỉnh, Holm, Friedman–Nemenyi [41], CI bootstrap, ngưỡng thực tiễn 0,02. Sửa mã KB2: rút lại n mẫu theo từng seed.', 'B2.2, A3, A4', st('Đã sửa')],
  ['O4', 'Chưa có giao thức tune, chọn ngưỡng, hiệu chỉnh xác suất', 'Quy tắc tune theo k; ngưỡng chọn bằng kiểm định chéo trên k mẫu; thêm Brier, ECE, reliability diagram, hiệu chỉnh theo tỷ lệ nền và Platt.', 'B2.2, A4', st('Đã sửa')],
  ['O5', 'Phạm vi quá rộng', 'SMOTE/ADASYN/CTGAN, baseline dựa trên mô hình ngôn ngữ, XTab và module giao diện chuyển sang tùy chọn; chỉ giữ class weight; danh sách baseline theo Phụ lục D của đánh giá. Hình 2 cập nhật tương ứng.', 'B1.2, B2.2, B2.3', st('Đã sửa')],
  ['O6', 'Tái lập và minh chứng chưa đủ', 'Mã KB1 v2 kèm CSV kết quả và dự đoán thô; khóa cache và tên file kết quả theo mã băm cấu hình; requirements ghi phiên bản. KB1 v2 đã được nhóm tái lập độc lập trên Google Colab ngày 18/10: 760/760 kết quả trùng (chênh lệch tối đa 0,00004 AUC-ROC). Mã KB1 cũ không còn: thay bằng KB1 v2 và bảng truy vết A5.1c; bản thảo LNCS và sản phẩm của Thiên do nhóm tải lên.', 'A3, A5.1c, B1.3', st('Một phần: KB1 v2 đã tái lập trên Colab (18/10); mã và kết quả đã đóng gói; nhóm tải lên Drive/Git trước 21/10')],
  ['Y1', 'Ánh xạ khái niệm chung', 'Chuẩn hóa thứ hạng fit trên train từng miền; không ghép “College” với “High School”; ghi rõ “đào tạo” là hai khái niệm khác; thử thêm “thâm niên” (không cải thiện xuyên miền); kiểm tra chiều tác động.', 'B1.3', st('Đã sửa')],
  ['Y2', 'Làm sạch Job Change', 'Loại 74 dòng trùng đặc trưng (25 nhóm nhãn mâu thuẫn) trước khi chia; bỏ city, giữ city_development_index; giá trị thiếu thành hạng mục riêng; ghi tỷ lệ thiếu.', 'B1.3, A2', st('Đã sửa')],
  ['Y3', 'Bảng 1 thiếu góc nhìn phương pháp luận; chưa có phiếu đọc', 'Thêm cột ghi chú phương pháp luận cho các bài đã kiểm tra; phiếu đọc một trang cho 10 bài quan trọng nhất.', 'B1.1', st('Một phần (phiếu đọc: Thiên, 21/10)')],
  ['Y4', 'Đạo đức và công bằng', 'Báo cáo hiệu năng và mức hiệu chỉnh theo nhóm giới; phiên bản bỏ giới tính; đoạn thảo luận về sử dụng có trách nhiệm.', 'B2.2, B3', st('Đã bổ sung kế hoạch')],
  ['Y5', 'Trình bày', 'Bỏ lặp Bảng 3 và mục 5.1; bỏ in đậm không xét ý nghĩa; giải thích hai dạng Wilcoxon; Hình 1–2 là đối tượng hình vector của Word; danh mục [1]–[47] đầy đủ.', 'Toàn bài', st('Đã sửa')],
  ['Mẫu', 'Thiếu B2.3 và B3', 'Bổ sung B2.3 (kế hoạch theo thời gian, theo tuần và mức ưu tiên) và B3 (kết quả dự kiến).', 'B2.3, B3', st('Đã sửa')],
  ['Mục 7', 'Ba câu hỏi cho nhóm', 'Câu 1 (cấu hình KB1 cũ) đã trả lời ở A5.1c: mã gốc không còn, đã truy vết bằng 5 cách mã hóa. Câu 2 (hội nghị mục tiêu) và câu 3 (dữ liệu thật) nhóm trả lời trong buổi Cổng 0.', 'A5.1c, A7', st('Một phần: câu 1 đã trả lời')],
  ['Quyết định 6.1.1', 'Giữ TB-HTL làm hướng phương pháp trung tâm', 'Áp dụng quy tắc GO/PIVOT ở mục 6.3 của đánh giá: Cổng 0 cho kết quả PIVOT ở cả hai chiều, nên TB-HTL chuyển thành một phương pháp trong bảng so sánh và trọng tâm chuyển sang “khi nào chuyển giao xuyên nguồn có ích”. Nhóm đề xuất cập nhật quyết định 6.1.1 tương ứng, chờ GVHD xác nhận ngày 21/10.', 'A5.4', st('Một phần: chờ GVHD xác nhận')],
], { size: 18 }));

// ============================================================ B1
C.push(H(1, 'B1. Giới thiệu về đề tài'));
C.push(H(2, 'B1.1 Tổng quan tình hình nghiên cứu'));
C.push(P('**Bài toán nghiên cứu.** Dự đoán nghỉ việc (employee attrition prediction) là bài toán phân loại nhị phân: từ các đặc trưng nhân khẩu học, công việc và tổ chức của một nhân viên, mô hình ước lượng khả năng người đó rời khỏi vị trí hiện tại. Bài toán có giá trị thực tiễn vì mỗi ca nghỉ việc kéo theo chi phí tuyển dụng, đào tạo người thay thế và mất năng suất. Học máy đã được áp dụng cho bài toán này gần hai thập kỷ, từ mạng nơ-ron và mô hình churn [1], [2] đến ensemble, transformer và pipeline có giải thích [3]–[10]. Tuy nhiên, De Vos et al. [43] chỉ ra rằng các công trình dùng giao thức chia dữ liệu và metric khác nhau nên kết quả không so sánh trực tiếp được; bài toán chưa có một mốc “tốt nhất” thống nhất.'));
C.push(P('**So sánh các công trình về dự đoán nghỉ việc.** Bảng 1 cho thấy gần như mọi công trình huấn luyện và đánh giá trong cùng một bộ dữ liệu. Công trình gần với đề tài nhất là Pereira & Torezzan [31]: hai tác giả huấn luyện Logistic Regression và Random Forest trên một bộ dữ liệu Kaggle rồi kiểm tra trên bộ khác, và ghi nhận tính bất đối xứng giữa hai chiều. Khác với đề tài, hai bộ trong [31] có chung 6 thuộc tính và cùng ngữ nghĩa nhãn, bài chỉ báo accuracy và không xét kịch bản ít nhãn đích.'));
C.push(TCap('Bảng 1. Các công trình tiêu biểu về dự đoán nghỉ việc.'));
C.push(table([1750, 1500, 1700, 2600, 1810], ['Công trình (năm)', 'Dữ liệu', 'Thuật toán chính', 'Ghi chú phương pháp luận', 'Chuyển giao xuyên nguồn'], [
  ['Sexton et al. [1] (2005)', '1 bộ nội bộ', 'Neural network + GA', 'Đang lập phiếu đọc', 'Không'],
  ['Saradhi & Palshikar [2] (2011)', '1 bộ IT nội bộ', 'SVM, Naïve Bayes, RF', 'Đang lập phiếu đọc', 'Không'],
  ['Jain et al. [3] (2020)', 'IBM HR', 'ANN, DT, LR, SVM', 'Các mô hình đã nằm trong benchmark [43]', 'Không'],
  ['Alsheref et al. [4] (2022)', 'IBM HR', 'Ensemble tự động', 'Tạp chí ngừng được Scopus lập chỉ mục từ 2022; chỉ trích ở phần tổng quan', 'Không'],
  ['Chung et al. [5] (2023)', 'IBM HR', 'Stacking ensemble', 'Trích bản chính thức trên ESWA; dùng làm baseline lĩnh vực', 'Không'],
  ['Li [6] (2023)', 'IBM HR', 'Transformer', 'FT-Transformer trong mã của nhóm đã bao phủ hướng này', 'Không'],
  ['Mohiuddin et al. [7] (2023)', 'IBM HR', '8 mô hình ML + SHAP', 'Hệ thống hỗ trợ quyết định; trích cho phần SHAP', 'Không'],
  ['Baydili & Tasci [8] (2025)', 'IBM + HR Analytics', 'GAN-Transformer + SHAP', 'Cân bằng bằng GAN trước khi chia train/test nên AUC-ROC 0,96 có nguy cơ bị thổi phồng; không dùng làm mốc', 'Không (đánh giá từng bộ)'],
  ['Veglio et al. [9] (2025)', '1 bộ MNC nội bộ', 'Cây quyết định CHAID', 'Dữ liệu nội bộ, không tái lập được', 'Không'],
  ['AL-Ali et al. [10] (2026)', 'IBM, Job Change và 2 bộ khác', 'Nhiều ML/DL + SHAP', 'Đánh giá độc lập từng bộ', 'Không (đánh giá từng bộ)'],
  ['Pereira & Torezzan [31] (2024)', '2 bộ Kaggle, chung 6 thuộc tính', 'LR, RF', 'Chỉ báo accuracy; kỷ yếu trong nước, không có hạng', 'Có: không dùng nhãn đích, cùng ngữ nghĩa nhãn'],
  ['De Vos et al. [43] (2025)', 'Nhiều bộ, có IBM', '14 mô hình chỉ dùng dữ liệu đích', 'Giao thức benchmark chuẩn của lĩnh vực; có mã nguồn', 'Không'],
], { size: 18 }));
C.push(P('**So sánh các kỹ thuật học chuyển giao cho dữ liệu bảng.** Học chuyển giao và chuyển giao miền có nền tảng lý thuyết vững [15], [18], [19], nhưng mỗi nhóm kỹ thuật chỉ đáp ứng một phần đặc điểm của bài toán nhân sự đa nguồn (Bảng 2). Hướng gần TB-HTL nhất là tách biểu diễn chung và riêng giữa hai miền, đã có trong Domain Separation Networks [32] và ở dạng tăng cường đặc trưng của Daumé III [33]; chuyển giao giữa các không gian đặc trưng khác nhau được nghiên cứu dưới tên chuyển giao miền không đồng nhất [34], [35]. Chuyển giao cũng có thể gây hại khi miền nguồn ít liên quan (chuyển giao âm [39]).'));
C.push(TCap('Bảng 2. Kỹ thuật học chuyển giao, chuyển giao miền và mô hình xuyên bảng tiêu biểu.'));
C.push(table([1700, 1900, 1150, 800, 1050, 2760], ['Công trình (năm)', 'Kỹ thuật chính', 'Không gian đặc trưng', 'Cần nhãn đích', 'Thích ứng nhãn khác nghĩa', 'Khác biệt so với TB-HTL'], [
  ['Daumé III [33] (2007)', 'Tăng cường đặc trưng chung/riêng', 'Chung', 'Có', 'Không', 'Cùng tập đặc trưng; TB-HTL áp ý tưởng chung/riêng cho tập cột khác nhau'],
  ['Duan et al. – HFA [34] (2012)', 'Chiếu hai không gian về không gian chung học được', 'Khác nhau', 'Có (ít)', 'Không', 'Học phép chiếu; TB-HTL dùng ánh xạ khái niệm có ý nghĩa và head riêng cho nhãn khác nghĩa'],
  ['Ganin & Lempitsky – DANN [17] (2015)', 'Căn chỉnh đối kháng', 'Chung', 'Không', 'Không', 'Giả định cùng nhiệm vụ; dùng làm đối chứng cho C4'],
  ['Sun et al. – CORAL [16] (2016)', 'Căn chỉnh hiệp phương sai', 'Chung', 'Không', 'Không', 'Như trên'],
  ['Bousmalis et al. – DSN [32] (2016)', 'Bộ mã hóa chung và riêng, tái tạo', 'Chung', 'Không', 'Không', 'Gần nhất về kiến trúc; TB-HTL có nhánh riêng cho cột chỉ một miền có và tinh chỉnh có giám sát với ít nhãn'],
  ['Wang et al. [39] (2019)', 'Đặc trưng hóa và tránh chuyển giao âm', 'Chung', 'Có', 'Không', 'Động lực cho việc giảm độ mạnh chuyển giao theo k'],
  ['Wang & Sun – TransTab [23] (2022)', 'Mã hóa theo tên cột và giá trị', 'Chung một phần', 'Có', 'Một phần', 'Căn chỉnh qua tên cột; chưa căn chỉnh thang đo giá trị số giữa nguồn'],
  ['Levin et al. [11] (2023)', 'Tiền huấn luyện có giám sát + tinh chỉnh', 'Chung', 'Có', 'Có', 'Cần chung tập cột; pseudo-feature chỉ bù vài cột'],
  ['Hegselmann et al. – TabLLM [37] (2023)', 'Chuyển dòng thành văn bản, mô hình ngôn ngữ học ít mẫu', 'Bất kỳ', 'Có (ít)', 'Không áp dụng', 'Không dùng dữ liệu nguồn có nhãn; chi phí tính toán lớn'],
  ['Zhu et al. – FLAT [36] (2023, preprint)', 'Học ít mẫu trên các bảng khác tập cột', 'Khác nhau', 'Có (ít)', 'Không', 'Cần nhiều bộ dữ liệu huấn luyện; bản preprint'],
  ['Kim et al. – CARTE [24] (2024)', 'Đồ thị dòng, embedding ngôn ngữ cho tên cột và giá trị phân loại; tiền huấn luyện trên YAGO', 'Khác nhau', 'Có', 'Một phần', 'Có căn chỉnh ngữ nghĩa, nhưng chưa căn chỉnh thang đo giá trị số giữa nguồn (số lần đào tạo so với số giờ đào tạo)'],
  ['Hollmann et al. – TabPFN v2 [25] (2025)', 'Mô hình nền tảng, học trong ngữ cảnh', 'Chỉ dữ liệu đích', 'Có', 'Không áp dụng', 'Không dùng dữ liệu nguồn; baseline mạnh cho dữ liệu nhỏ'],
  ['Qu et al. – TabICL [44] (2025)', 'Mô hình nền tảng, học trong ngữ cảnh', 'Chỉ dữ liệu đích', 'Có', 'Không áp dụng', 'Như trên; giấy phép thoáng hơn'],
], { size: 18 }));
C.push(P('**Khoảng trống nghiên cứu.**'));
C.push(...numbered([
  'Các nghiên cứu nghỉ việc hầu như huấn luyện và đánh giá trong cùng một bộ dữ liệu. Công trình chuyển giao duy nhất nhóm tìm thấy [31] chỉ xét hai bộ có chung thuộc tính và cùng ngữ nghĩa nhãn, không dùng nhãn đích và chỉ báo accuracy; nhóm chưa tìm thấy công trình chuyển giao cho nghỉ việc ở hội nghị A*/A hoặc tạp chí Q1/Q2 (nhật ký truy vấn Scopus sẽ được lưu kèm).',
  'Chuyển giao miền kinh điển [16], [17], [32], [33] và chuyển giao dữ liệu bảng [11] giả định hai miền chung tập đặc trưng. Các mô hình xuyên bảng [23], [24] chấp nhận cột khác nhau và căn chỉnh theo ngữ nghĩa của tên cột, nhưng chưa căn chỉnh thang đo của giá trị số giữa các nguồn.',
  'Chưa có giao thức đánh giá có kiểm soát trả lời câu hỏi khi nào chuyển giao xuyên nguồn có ích hoặc có hại cho dự đoán nghỉ việc: theo số nhãn đích, theo mức trùng khái niệm giữa hai nguồn và theo ngữ nghĩa nhãn.',
]));
C.push(P('**Đề tài sẽ thực hiện,** theo thứ tự ưu tiên: (a) xây dựng giao thức đánh giá chuyển giao xuyên nguồn có kiểm soát cho bài toán nghỉ việc, gồm nhiều mức nhãn đích, hai chiều, nhiều cặp nguồn và kiểm định thống kê có hiệu chỉnh; (b) phân tích khi nào chuyển giao có ích hoặc có hại, tách riêng hiệu ứng mất đặc trưng, domain shift và khác ngữ nghĩa nhãn; (c) đề xuất TB-HTL như một phương pháp đơn giản, mỗi thành phần có giả thuyết cơ chế và thí nghiệm loại bỏ (ablation).'));

C.push(H(2, 'B1.2 Ý tưởng khoa học, tính cấp thiết và tính mới'));
C.push(P('**Tổng quan và tính cấp thiết.** Doanh nghiệp thu thập dữ liệu nhân sự từ nhiều hệ thống: hệ thống HRIS nội bộ ghi nhận nhân viên đang làm việc, còn các nền tảng tuyển dụng hoặc đào tạo ghi nhận ứng viên và học viên. Các nguồn khác nhau về cấu trúc cột, cách mã hóa và ý nghĩa của nhãn. Tính cấp thiết đến từ ba điểm, đã được kiểm chứng bằng thực nghiệm sơ khởi KB1 v2 (mục B1.3):'));
C.push(B('**Thiếu dữ liệu ở nơi cần dự đoán:** đơn vị mới, công ty nhỏ hoặc nhóm nhân sự ít người có rất ít ca nghỉ việc đã ghi nhận. Ở IBM, Logistic Regression dùng đủ đặc trưng đạt 0,829 AUC-ROC khi có toàn bộ 1.176 nhãn huấn luyện; kiểm tra sơ bộ của GVHD cho thấy với 10–20 nhãn, cùng mô hình chỉ đạt khoảng 0,60–0,63.'));
C.push(B('**Thông tin dùng chung giữa các nguồn rất nghèo:** chỉ dùng 4 khái niệm có ở cả hai nguồn làm mất khoảng 0,17–0,19 AUC-ROC so với dùng đủ đặc trưng (mô hình tốt nhất mỗi miền), và tín hiệu trong không gian chung đến gần như hoàn toàn từ số năm kinh nghiệm: quy tắc không cần học “điểm rủi ro = − số năm kinh nghiệm” đạt 0,648 (IBM) và 0,619 (Job Change). Ngược lại, khi đã cùng không gian khái niệm và được căn chỉnh thang đo, domain shift chỉ làm giảm thêm 0,00–0,05 AUC-ROC. Vì vậy, muốn chuyển giao có ích thì phải giữ được đặc trưng riêng của từng nguồn, không thể chỉ dùng phần giao.'));
C.push(B('**Cửa sổ hữu ích của chuyển giao hẹp và cần được kiểm chứng chặt:** kiểm tra sơ bộ của GVHD cho thấy một baseline chuyển giao đơn giản chỉ vượt mô hình chỉ dùng dữ liệu đích khi k ≤ 20 nhãn (+0,02–0,03 AUC-ROC), chưa đủ ý nghĩa thống kê sau hiệu chỉnh cho các lần chia chồng lấn, và gây chuyển giao âm từ k ≈ 50. Câu hỏi “khi nào chuyển giao có ích” vì vậy là câu hỏi nghiên cứu thực sự, không phải điều đã biết trước.'));
C.push(P('**Về ngữ nghĩa nhãn.** Theo Mobley [21], ý định rời bỏ là bước đi trước hành vi nghỉ việc, và ý định là yếu tố dự báo mạnh của hành vi [22]. Tuy nhiên, lập luận này đúng trên cùng một người; với hai quần thể khác nhau (ứng viên khóa đào tạo ở Job Change và nhân viên hư cấu ở IBM), ảnh hưởng của khác ngữ nghĩa nhãn bị trộn với khác quần thể và khác cấu trúc. Đề tài vì vậy so sánh một cặp cùng ngữ nghĩa nhãn (hành vi ↔ hành vi) với một cặp khác ngữ nghĩa (hành vi ↔ ý định) để tách hiệu ứng này (RQ4).'));
C.push(P('**Định nghĩa bài toán.**'));
C.push(table([2300, 7060], ['Thành phần', 'Mô tả'], [
  ['Lĩnh vực ứng dụng', 'Phân tích nhân sự (HR Analytics) trên nhiều nguồn dữ liệu'],
  ['Người dùng', 'Nhà quản lý nhân sự, bộ phận HR'],
  ['Quy trình hoạt động', 'Rà soát rủi ro nghỉ việc định kỳ trong quy trình giữ chân nhân tài và hoạch định nhân lực'],
  ['Vấn đề giải quyết', 'Khi nào và bằng cách nào mô hình học từ một nguồn dữ liệu nhân sự giúp dự đoán ở nguồn khác cấu trúc, có thể khác ngữ nghĩa nhãn và chỉ có ít nhãn'],
  ['Input', 'Hồ sơ nhân sự của nguồn đích; dữ liệu có nhãn của nguồn khác; k nhân viên đã biết nhãn ở nguồn đích'],
  ['Output', 'Xác suất rủi ro nghỉ việc đã hiệu chỉnh cho từng nhân viên, kèm các yếu tố đóng góp (SHAP)'],
  ['Đơn vị đánh giá', 'Nhiều cặp nguồn, hai chiều, nhiều mức k, so với baseline chỉ dùng dữ liệu đích mạnh nhất và baseline chuyển giao đơn giản'],
]));
C.push(P('Về hình thức, nguồn chuyển giao D_S = {(x_i, y_i)} và nguồn đích D_T có không gian đặc trưng khác nhau (X_S ≠ X_T), nhãn có thể khác ngữ nghĩa (P_S(y | x) ≠ P_T(y | x)), và nguồn đích chỉ có k mẫu có nhãn. Theo phân loại của Pan & Yang [18], đây là học chuyển giao quy nạp trên dữ liệu bảng không đồng nhất [35]. Hình 1 minh họa bài toán.'));
C.push(Marker('FIG1'));
C.push(Caption('Hình 1. Minh họa bài toán nghiên cứu.'));
C.push(P('**Phác thảo Work Packages và framework dự kiến.** Đề tài gồm 5 Work Package (Hình 2). WP1 (quản lý, điều phối) và WP5 (tổng hợp báo cáo) chạy xuyên suốt; ba Nội dung ứng với WP2 (khảo sát), WP3 (xây dựng framework, mở đầu bằng Cổng 0) và WP4 (thực nghiệm và phân tích). Framework gồm bốn tầng; kỹ thuật cụ thể được chốt sau Cổng 0 (21/10/2026):'));
C.push(...numbered([
  '**Căn chỉnh khái niệm liên miền (C1):** đưa các khái niệm nhân sự tương đương nhưng mã hóa khác nhau về chung ý nghĩa và thang đo, bằng ánh xạ theo tri thức chuyên ngành kết hợp chuẩn hóa theo thứ hạng fit riêng trên phần huấn luyện của từng miền; so sánh với căn chỉnh tự động theo tên cột của TransTab [23] và CARTE [24].',
  '**Học biểu diễn có khả năng chuyển giao (C2, C3):** nhánh chung cho các khái niệm có ở cả hai nguồn được tiền huấn luyện ở nguồn lớn rồi chuyển giao; nhánh riêng học lại đặc trưng chỉ nguồn đích có; tắt ngẫu nhiên nhánh riêng khi tiền huấn luyện để nhánh chung mang thông tin dự đoán. So sánh với DSN [32] và tiền huấn luyện theo [11].',
  '**Thích ứng với nhãn khác nghĩa và ít nhãn (C4):** dùng head riêng cho từng miền, coi nhãn nguồn là tác vụ phụ; độ mạnh chuyển giao (hệ số neo λ của L2-SP [26] hoặc trọng số trộn) giảm theo k và được chọn bằng kiểm định chéo trên k mẫu, nhằm tránh chuyển giao âm [39]. Đối chứng với DANN [17], CORAL [16] và TabPFN v2 [25].',
  '**Đầu ra tin cậy và có giải thích:** xác suất được hiệu chỉnh theo tỷ lệ nền của miền đích; giải thích bằng SHAP [27] và so sánh yếu tố rủi ro giữa các nguồn; báo cáo hiệu năng và mức hiệu chỉnh theo nhóm giới.',
]));
C.push(Marker('FIG2'));
C.push(Caption('Hình 2. Work Packages và framework dự kiến triển khai đề tài.'));
C.push(P('Hình 2 cho thấy ba Nội dung nối tiếp: kết quả khảo sát ở WP2 quyết định các kỹ thuật được thử ở WP3; WP3 mở đầu bằng Cổng 0 để xác định cửa sổ có ích của chuyển giao trước khi cài TB-HTL; WP4 đánh giá trên nhiều cặp nguồn và phân tích khi nào chuyển giao có ích.'));
C.push(P('**Tính mới.** Tính mới của đề tài nằm ở ba điểm kiểm chứng được:'));
C.push(B('**Về đánh giá:** giao thức chuyển giao xuyên nguồn có kiểm soát cho dự đoán nghỉ việc, chặt hơn [31]: nhiều mức nhãn đích, hai chiều, nhiều cặp nguồn, kiểm định có hiệu chỉnh, và tách riêng hiệu ứng mất đặc trưng, domain shift, khác ngữ nghĩa nhãn.'));
C.push(B('**Về phân tích:** bằng chứng thực nghiệm về điều kiện để chuyển giao có ích hoặc có hại, gồm mức k*, ảnh hưởng của mức trùng khái niệm và của ngữ nghĩa nhãn.'));
C.push(B('**Về phương pháp:** quy tắc căn chỉnh khái niệm nhân sự theo ý nghĩa và thang đo (C1), và cơ chế điều chỉnh độ mạnh chuyển giao theo k cho nhãn khác nghĩa (C4); mỗi thành phần của TB-HTL có ablation và đối chứng nhãn nguồn xáo trộn để chứng minh lợi ích đến từ tri thức nguồn chứ không chỉ từ điều chuẩn.'));

// ---------------------------------------------------------------- B1.3
C.push(H(2, 'B1.3 Kết quả nghiên cứu sơ khởi'));
C.push(P('Nội dung 1 đã hoàn thành trước khi nộp đề cương (20/09/2026). Các mục đánh dấu “bổ sung” được thực hiện sau đó, trong đó KB1 v2 được chạy theo yêu cầu của đánh giá ngày 07/10/2026.'));
C.push(P('**Kết quả khảo sát lý thuyết.** Nhóm đã khảo sát 20 công trình (10 về dự đoán nghỉ việc, 10 nền tảng về học chuyển giao, chuyển giao miền và học đa nhiệm [11]–[20]), bổ sung các mô hình xuyên bảng và mô hình nền tảng dữ liệu bảng [23]–[25] và, theo đánh giá, 17 tài liệu [31]–[47] về chuyển giao miền không đồng nhất, chuyển giao âm, thống kê so sánh mô hình và benchmark nghỉ việc. Phiếu đọc một trang cho 10 bài quan trọng nhất đang được lập.'));
C.push(P('**Công cụ và kỹ thuật triển khai.** Python 3.10, scikit-learn, XGBoost/CatBoost, PyTorch, Optuna, SHAP trên Google Colab. Nhóm đã tái hiện pipeline của Levin et al. [11] trên Yeast (3/14 nhiệm vụ, 5 seed, chưa tune; đủ cho mục đích kiểm chứng mã, không mở rộng thêm theo quyết định của GVHD) và tái hiện CARTE [24] trên 3 bộ dữ liệu giá rượu (bổ sung, tương quan 0,95 với số liệu công bố; chi tiết ở A5.3).'));
C.push(P('**Dữ liệu thực nghiệm.**'));
C.push(TCap('Bảng 3. Các nguồn dữ liệu nhân sự.'));
C.push(table([1700, 2400, 1400, 1300, 1260, 1300], ['Vai trò', 'Bộ dữ liệu', 'Số dòng', 'Số đặc trưng', 'Nhãn', 'Tỷ lệ dương'], [
  ['Miền A', 'IBM HR Analytics Employee Attrition & Performance (dữ liệu hư cấu do IBM tạo)', '1.470', '30', 'Hành vi nghỉ việc (Attrition)', '16,12% (237)'],
  ['Miền B', 'HR Analytics: Job Change of Data Scientists (ứng viên khóa đào tạo của một công ty)', '19.158; 19.084 sau khi loại 74 dòng trùng', '11 (bỏ ID và city)', 'Ý định tìm việc mới (target)', '24,93% (4.777); 24,92% sau khi loại trùng'],
  ['Miền C (bổ sung, kế hoạch)', 'HR Analytics (Kaggle, dữ liệu mô phỏng)', '14.999', '9', 'Hành vi nghỉ việc (left)', 'Sẽ kiểm tra'],
], { size: 18 }));
C.push(P('Job Change thiếu nhiều dữ liệu (giới tính 23,5%, quy mô công ty 31,0%, loại công ty 32,0%, chuyên ngành 14,7%) và có 12,8% người chưa từng đổi việc. Dataset01_HR_Analytics trong thư mục dữ liệu của nhóm là bản sao mở rộng của IBM nên bị loại khỏi danh sách nguồn.'));
C.push(P('**Ánh xạ khái niệm chung (đã sửa theo Y1).** Bốn khái niệm có ở cả hai miền: giới tính (nhị phân kèm cờ “khác/thiếu”); học vấn trên thang 0–5 (IBM: 1 Below College … 5 Doctor; Job Change: Primary School → 0, High School → 1, Graduate → 3, Masters → 4, Phd → 5; mức 2 “College” của IBM không có tương ứng, không ghép với High School như bản cũ); số năm kinh nghiệm (chặn trên 21); và đào tạo. Hai biến đào tạo là hai khái niệm khác nhau (số lần đào tạo trong năm ở IBM, số giờ học trong khóa ở Job Change), nên chỉ so sánh được theo thứ hạng trong từng miền. Chuẩn hóa thứ hạng được fit trên phần huấn luyện của từng miền. Nhóm thử thêm khái niệm thứ năm “thâm niên tại nơi làm hiện tại” (YearsAtCompany ↔ last_new_job, giá trị “never” quy về số năm kinh nghiệm, chặn 5): khái niệm này cải thiện mô hình trong-miền ở IBM (0,645 → 0,669 với Logistic Regression) nhưng không cải thiện chuyển giao (0,621 → 0,620 ở chiều B→A), nên chưa đưa vào không gian chung.'));
C.push(P('**Thực nghiệm đối chứng 2×2 (KB1 v2).** Thực nghiệm tách ảnh hưởng của việc mất đặc trưng khỏi ảnh hưởng của domain shift, với năm họ mô hình và 10 lần chia 80/20 phân tầng (seed 0–9); TabPFN v2 chạy trên Colab GPU ngày 21/10 với cùng các lần chia, tập huấn luyện Job Change (khi trong miền hoặc làm nguồn) được lấy mẫu phân tầng còn 10.000 dòng do giới hạn của TabPFN v2. Ở thiết lập xuyên miền, mô hình học trên toàn bộ miền nguồn và được kiểm tra trên cùng tập test 20% của miền đích như mô hình trong-miền, nên so sánh là bắt cặp theo lần chia. Hai cách mã hóa khái niệm chung được so sánh: giữ thang đo của nguồn, và căn chỉnh theo thứ hạng trong từng miền (C1).'));
C.push(TCap('Bảng 4. KB1 v2: AUC-ROC trung bình qua 10 lần chia, trong ngoặc là PR-AUC (tỷ lệ dương: A 0,161; B 0,249).'));
C.push(table([1640, 960, 960, 960, 960, 960, 960, 960, 1000],
  ['Mô hình', 'A: đủ đặc trưng', 'A: trong-miền, 4 KN', 'B→A, C1', 'B→A, thang nguồn', 'B: đủ đặc trưng', 'B: trong-miền, 4 KN', 'A→B, C1', 'A→B, thang nguồn'], K.main, { size: 16 }));
C.push(image(G, 6.5, 2.57));
C.push(Caption('Hình 3. KB1 v2: AUC-ROC trong-miền và xuyên-miền trên 4 khái niệm chung, CI 95% có hiệu chỉnh cho các lần chia chồng lấn [40]. Đường đứt nét là quy tắc “− kinh nghiệm”.'));
C.push(P('Kết quả cho năm nhận định, thay cho kết luận của bản cũ:'));
C.push(...numbered([
  '**Mất đặc trưng là nút thắt chính.** Từ đủ đặc trưng xuống 4 khái niệm chung, AUC-ROC của mô hình tốt nhất giảm từ 0,840 xuống 0,651 ở IBM và từ 0,799 xuống 0,639 ở Job Change (khoảng 0,16–0,19; mô hình tốt nhất ở cả hai mức là TabPFN v2). Con số 0,21–0,23 của bản cũ đúng với Random Forest mặc định (0,809 → 0,574 và 0,782 → 0,563) nhưng phóng đại so với mô hình phù hợp.',
  '**Domain shift trên không gian chung nhỏ khi mô hình có điều chuẩn.** Chiều B→A với C1: Logistic Regression 0,644 → 0,621, Random Forest có điều chuẩn 0,633 → 0,620, XGBoost 0,572 → 0,594; không chênh lệch nào có ý nghĩa sau hiệu chỉnh (p hiệu chỉnh ≥ 0,23). Kết quả “B→A chỉ đạt 0,498, ngang mức ngẫu nhiên” của bản cũ không tái lập được; Random Forest mặc định trong lần chạy này đạt 0,561–0,572. Chiều A→B giảm ít nhưng có ý nghĩa (Logistic Regression −0,014, p Holm = 0,030; Random Forest có điều chuẩn −0,027, p Holm = 0,002; XGBoost −0,049, p Holm < 0,001).',
  '**Căn chỉnh thang đo theo miền (C1) là cần thiết.** Nếu giữ thang đo của nguồn, Logistic Regression ở chiều A→B giảm xuống 0,525 và XGBoost xuống 0,546, vì “đào tạo” là số lần ở IBM nhưng là số giờ ở Job Change. Căn chỉnh theo thứ hạng trong từng miền đưa hai con số này lên 0,607 và 0,581. Đây là bằng chứng sớm cho giả thuyết H3a.',
  '**Tín hiệu chung gần như chỉ đến từ số năm kinh nghiệm,** cùng chiều ở hai miền: quy tắc “− kinh nghiệm” bằng hoặc tốt hơn mọi mô hình học trên 4 khái niệm. Hệ quả: lập luận cho C2 (giữ đặc trưng riêng) mạnh lên; C4 cần được biện minh qua thích ứng với ít nhãn và tránh chuyển giao âm, không qua “domain shift lớn”.',
  '**TabPFN v2 (bổ sung 21/10, R1) không đổi các nhận định trên.** TabPFN v2 là mô hình tốt nhất trên đủ đặc trưng (0,840 ở IBM; 0,799 ở Job Change, ngang XGBoost) và trong miền trên 4 khái niệm (0,651 và 0,639), nhưng trên 4 khái niệm vẫn chỉ ngang quy tắc “− kinh nghiệm” ở IBM (0,648). Khi xuyên miền, TabPFN v2 giảm nhiều hơn các mô hình có điều chuẩn: B→A còn 0,616 (thang nguồn) và 0,588 (C1), Δ −0,035 và −0,056 với p hiệu chỉnh 0,04–0,05 nhưng không còn ý nghĩa sau Holm (0,20 và 0,29); A→B còn 0,608–0,614 (p Holm ≤ 0,014). Điểm đáng chú ý là TabPFN v2 gần như không nhạy với cách mã hóa ở A→B (0,608 khi giữ thang nguồn so với 0,525 của Logistic Regression) và cho xuyên miền A→B cao nhất với C1 (0,614). Một mô hình nền tảng mạnh hơn vì vậy không thu hẹp được khoảng cách do mất đặc trưng (0,840 → 0,651).',
]));
C.push(P('Sanity check đạt yêu cầu: khi xáo trộn nhãn huấn luyện, Logistic Regression cho AUC-ROC 0,502 (A) và 0,483 (B). TabPFN v2 không chạy được trong môi trường này (cần GPU và tải trọng số); nhóm đã chạy TabPFN v2 trên Colab GPU (Tesla T4) ngày 18/10 cho G0-2 (A5.4) và ngày 21/10 cho thiết kế 2×2 (100 lần chạy, cùng file chia; sanity check dữ liệu trùng khớp). **Đã chạy lại ngày 16/10/2026 trên file Kaggle gốc của nhóm** (IBM: trùng từng byte với bản đã dùng; Job Change: chỉ khác nhãn hạng mục của company_size như “10/49” → “10-49”, không ảnh hưởng mã hóa): 760/760 kết quả trùng khớp, lệch tối đa 0,0000 ở cả AUC-ROC và PR-AUC. **Nhóm đã tự chạy lại KB1 v2 trên Google Colab ngày 18/10/2026** bằng notebook chay_KB1_v2_tren_Colab.ipynb: 760/760 kết quả trùng với bản báo cáo (chênh lệch tối đa 0,00004 AUC-ROC và 0,00001 PR-AUC, do khác phiên bản thư viện); sanity check và Hình 3 trùng khớp. Chi tiết kiểm định ở A5.1.'));

// ============================================================ B2
C.push(H(1, 'B2. Mục tiêu, nội dung, kế hoạch nghiên cứu'));
C.push(H(2, 'B2.1 Mục tiêu'));
C.push(...numbered([
  '**Lý thuyết (Nội dung 1):** hệ thống hóa nền tảng về học chuyển giao, chuyển giao miền đồng nhất và không đồng nhất, chuyển giao âm, học trên dữ liệu bảng ít mẫu, so sánh thống kê nhiều mô hình và AI có thể giải thích, làm cơ sở lựa chọn phương pháp và giao thức.',
  '**Giao thức và phương pháp (Nội dung 2):** xây dựng giao thức đánh giá chuyển giao xuyên nguồn có kiểm soát; xác định cửa sổ có ích của chuyển giao bằng các baseline đơn giản (Cổng 0); phát triển TB-HTL như một phương pháp đơn giản với ablation cho từng thành phần.',
  '**Thực nghiệm và phân tích (Nội dung 3):** đánh giá trên ít nhất hai cặp nguồn (một cặp cùng, một cặp khác ngữ nghĩa nhãn), hai chiều, nhiều mức k; phân tích khi nào chuyển giao có ích hoặc có hại; đánh giá hiệu chỉnh xác suất, công bằng theo giới và giải thích yếu tố rủi ro.',
]));
C.push(P('**Câu hỏi nghiên cứu, giả thuyết và tiêu chí bác bỏ.** Các ngưỡng dưới đây là đề xuất ban đầu của GVHD, sẽ được nhóm chốt và ghi vào file 00_contributions.md trước khi chạy KB4. Cột cuối ghi trạng thái hiện tại theo KB1 v2.'));
C.push(TCap('Bảng 5. Câu hỏi nghiên cứu, giả thuyết, thí nghiệm và tiêu chí bác bỏ.'));
C.push(table([560, 1700, 2650, 1200, 1850, 1400], ['Mã', 'Câu hỏi', 'Giả thuyết', 'Thí nghiệm', 'Tiêu chí bác bỏ', 'Trạng thái'], [
  ['RQ1', 'Mô hình học ở một nguồn có xếp hạng đúng rủi ro ở nguồn khác trên khái niệm chung, khi chưa dùng nhãn đích?', 'H1: với mô hình có điều chuẩn, zero-shot đạt ≥ 90% AUC-ROC của mô hình trong-miền trên cùng khái niệm', 'KB1 v2, hai chiều, mọi cặp', 'Tỷ lệ < 90% ở mọi họ mô hình có điều chuẩn', 'Ủng hộ ở cặp A–B với C1 (92–104%). Nhóm đề xuất thêm tỷ lệ phần vượt mức ngẫu nhiên (AUC − 0,5), hiện là 0,62–0,90 ở chiều A→B. G0-4: zero-shot vượt bản xáo trộn nhãn nguồn +0,12 (B→A) và +0,105 (A→B) PR-AUC, CI không chứa 0'],
  ['RQ2', 'Chuyển giao có giúp khi đích ít nhãn? Đến mức k nào?', 'H2: tồn tại k* sao cho với k ≤ k*, phương pháp chuyển giao tốt nhất vượt baseline chỉ-dữ-liệu-đích mạnh nhất (gồm TabPFN v2) ≥ 0,02 PR-AUC; với k ≥ 200 không kém quá 0,01', 'Cổng 0, KB4', 'Không mức k nào đạt ngưỡng sau hiệu chỉnh Holm, hoặc kém hơn 0,01 ở k lớn', 'Bị bác bỏ ở cặp A–B (Cổng 0, 17/10): không phương pháp nào trong 7 baseline chuyển giao vượt ngưỡng ở k ≤ 50, cả hai chiều (A5.4); đã tính cả TabPFN v2'],
  ['RQ3', 'Thành phần nào của TB-HTL tạo ra lợi ích?', 'H3a: bỏ C1 làm giảm zero-shot. H3b: bỏ nhánh riêng làm giảm mạnh khi k lớn. H3c: tắt nhánh ngẫu nhiên làm tăng AUC của nhánh chung trên nguồn. H3d: neo L2-SP tốt hơn tinh chỉnh không neo ở k ≤ 50', 'KB3, KB5, KB6, đối chứng nhãn nguồn xáo trộn', 'Ablation không khác biệt có ý nghĩa; đối chứng xáo trộn cho kết quả tương đương', 'H3a có bằng chứng sớm ở chiều A→B (KB1 v2)'],
  ['RQ4', 'Khác ngữ nghĩa nhãn làm giảm lợi ích chuyển giao bao nhiêu?', 'H4: với cùng mức trùng khái niệm, lợi ích ở cặp cùng ngữ nghĩa lớn hơn ở cặp khác ngữ nghĩa', 'So sánh ba cặp (KB8, A5.5)', 'Không khác biệt hoặc ngược chiều', 'Chưa ủng hộ (21/10): hai cặp cùng ngữ nghĩa (A↔C, A↔D) cũng không có lợi ích chuyển giao ở k ≤ 50; yếu tố nổi bật là chiều tác động của khái niệm chung và mức thông tin riêng của miền đích (A5.5)'],
  ['RQ5', 'Yếu tố rủi ro có nhất quán giữa các nguồn?', 'H5: thứ hạng SHAP của khái niệm chung tương quan dương giữa hai miền', 'KB7', 'Tương quan hạng ≤ 0 hoặc CI 95% chứa 0', 'Dấu hiệu sớm: tương quan Spearman với nhãn cùng chiều ở cả 4 khái niệm trừ giới tính'],
], { size: 17 }));

C.push(H(2, 'B2.2 Nội dung và phương pháp nghiên cứu'));
C.push(H(3, 'Nội dung 1: Nghiên cứu khảo sát nền tảng lý thuyết và công cụ triển khai (WP2, 26/06 – 20/09/2026; bổ sung đến 21/10)'));
C.push(P('**Phương pháp thực hiện:**'));
C.push(B('**Cách thức:** khảo sát có hệ thống công trình về dự đoán nghỉ việc, học chuyển giao, chuyển giao miền đồng nhất và không đồng nhất, mô hình xuyên bảng và so sánh thống kê; lập phiếu đọc một trang cho mỗi bài (bài toán, dữ liệu, giao thức, kết quả, hạn chế, liên hệ với đề tài); lưu nhật ký truy vấn Scopus; tái hiện [11] và [24] để làm chủ kỹ thuật.'));
C.push(B('**Phạm vi:** 37 công trình; tiêu chí chọn baseline: hội nghị CORE B trở lên hoặc tạp chí Scimago Q1/Q2, có mã nguồn hoặc mô tả đủ để cài lại.'));
C.push(B('**Đánh giá:** độ bao phủ tài liệu; mức khớp giữa kết quả tái hiện và bài gốc.'));
C.push(P('**Kết quả dự kiến:** báo cáo khoa học về tổng quan tài liệu, khoảng trống nghiên cứu và cơ sở lý thuyết; phiếu đọc; mã tái hiện [11] và [24].'));
C.push(H(3, 'Nội dung 2: Giao thức đánh giá và phương pháp “TB-HTL – Học chuyển giao hai nhánh cho dữ liệu nhân sự không đồng nhất” (WP3, 08/10 – 15/11/2026)'));
C.push(P('**Phương pháp thực hiện:**'));
C.push(B('**Cổng 0 (08/10 – 21/10):** KB1 v2 đa mô hình; đường cong học chỉ-dữ-liệu-đích theo k với các mô hình trong benchmark De Vos et al. [43], stacking của Chung et al. [5] và TabPFN v2 [25]; baseline chuyển giao đơn giản (zero-shot, stacking điểm nguồn, trung bình hạng có trọng số w(k) chọn bằng kiểm định chéo, LR neo hệ số nguồn); đối chứng nhãn nguồn xáo trộn. **GO** nếu ít nhất một baseline chuyển giao vượt baseline chỉ-dữ-liệu-đích mạnh nhất ở một mức k ≤ 50 với chênh lệch PR-AUC ≥ 0,02 và CI 95% không chứa 0; khi đó TB-HTL phải vượt baseline chuyển giao tốt nhất trong cửa sổ này và không gây chuyển giao âm ở k lớn. **PIVOT** nếu không đạt: TB-HTL được giữ như một phương pháp trong nghiên cứu thực nghiệm “khi nào chuyển giao xuyên nguồn có ích”. **Kết quả chạy ngày 17/10/2026: PIVOT ở cả hai chiều** (Phụ lục A5.4).'));
C.push(B('**TB-HTL:** bốn thành phần C1–C4 như mục B1.2; mỗi thành phần có một giả thuyết cơ chế (H3a–H3d) và một ablation; đo cơ chế bằng AUC-ROC của head chỉ dùng nhánh chung trên nguồn và đích, độ tương đồng biểu diễn giữa hai miền (CKA) và ảnh hưởng của kích thước nguồn (1.000 / 5.000 / 19.084 mẫu); báo cáo λ* theo k như một kết quả về cơ chế.'));
C.push(B('**Phạm vi:** cặp A–B trước giữa kỳ, cặp A–C bắt đầu từ 22/10; chiều chính B→A; k ∈ {10, 20, 50, 100, 200, 500, toàn bộ}; R = 30 lần lặp với k ≤ 200 và 10 lần với các mức còn lại; baseline nặng (CARTE, DSN, TransTab) có thể dùng 10 lần lặp.'));
C.push(B('**Baseline (theo Phụ lục D của đánh giá):** bắt buộc: De Vos et al. [43], stacking Chung et al. [5], TabPFN v2 [25], tiền huấn luyện theo Levin et al. [11] (FT-Canonical), CARTE [24], DSN [32]; nên có: DANN [17], CORAL [16], L2-SP [26], mô hình tốt nhất của AL-Ali et al. [10], TransTab [23], TabICL [44]; tùy chọn: TabLLM [37], FeatLLM [45], Tabula-8B [46], TP-BERTa [47], XTab [38]. Mọi baseline chạy lại trên cùng file chia, cùng tiền xử lý và cùng ngân sách tune; không chép số liệu từ bài gốc.'));
C.push(B('**Tune và chọn ngưỡng:** k ≤ 50 dùng siêu tham số mặc định cố định (hoặc tune trên nguồn như [11]); k ≥ 100 dùng kiểm định chéo lồng trong k mẫu; cùng số trial cho mọi phương pháp; ngưỡng chọn bằng kiểm định chéo trên k mẫu hoặc theo tỷ lệ chi phí định trước; không dùng tập test để chọn siêu tham số, epoch hay ngưỡng.'));
C.push(B('**Thống kê:** chênh lệch bắt cặp so với baseline mạnh nhất kèm CI 95% bootstrap; corrected resampled t-test [40] hoặc Wilcoxon signed-rank, hiệu chỉnh Holm; Friedman – Nemenyi và biểu đồ critical difference [41] khi tổng hợp nhiều cặp và nhiều k; ngưỡng ý nghĩa thực tiễn 0,02; PR-AUC luôn ghi kèm tỷ lệ dương. Wilcoxon rank-sum chỉ dùng trong phần tái hiện [11] để giữ đúng cách xếp hạng của bài gốc.'));
C.push(P('**Kết quả dự kiến:** báo cáo Cổng 0 (hai trang); báo cáo khoa học về giao thức và phương pháp TB-HTL kèm ablation; file chia dữ liệu chung và mã nguồn.'));
C.push(H(3, 'Nội dung 3: Thực nghiệm, phân tích và ứng dụng (WP4, 16/11 – 27/12/2026)'));
C.push(P('**Phương pháp thực hiện:**'));
C.push(B('**Cách thức:** chạy toàn bộ ma trận thực nghiệm trên các cặp nguồn và hai chiều; so sánh lợi ích chuyển giao giữa cặp cùng và khác ngữ nghĩa nhãn (RQ4); phân tích k*, ảnh hưởng của mức trùng khái niệm; giải thích bằng SHAP và so sánh yếu tố rủi ro giữa các nguồn (RQ5).'));
C.push(B('**Hiệu chỉnh xác suất:** Brier score, ECE và reliability diagram; hiệu chỉnh theo tỷ lệ nền của miền đích (prior shift) hoặc Platt scaling trên k mẫu, vì tỷ lệ dương khác nhau giữa các nguồn (16% và 25%).'));
C.push(B('**Công bằng và sử dụng có trách nhiệm:** dự đoán nghỉ việc là ứng dụng trong quản lý lao động, được xếp vào nhóm rủi ro cao trong Đạo luật AI của EU; nhóm báo cáo hiệu năng và mức hiệu chỉnh theo nhóm giới, thử phiên bản bỏ giới tính khỏi khái niệm chung, và thêm phần thảo luận rằng mô hình chỉ hỗ trợ rà soát, không dùng để ra quyết định nhân sự tự động.'));
C.push(B('**Xử lý mất cân bằng:** dùng class weight trong phần chính; SMOTE [28], ADASYN [29], CTGAN [30] chuyển sang tùy chọn vì tái lấy mẫu thường không cải thiện metric xếp hạng và làm lệch hiệu chỉnh xác suất.'));
C.push(B('**Đánh giá:** PR-AUC (chính), AUC-ROC, Brier, ECE; F1 và G-Mean tại ngưỡng chọn trên dữ liệu huấn luyện; thời gian huấn luyện và suy luận.'));
C.push(P('**Kết quả dự kiến:** báo cáo khoa học về kết quả thực nghiệm và phân tích khi nào chuyển giao có ích; bản thảo bài báo hội nghị; mã nguồn đầy đủ. Module chấm điểm rủi ro có giao diện là hạng mục tùy chọn.'));

C.push(H(2, 'B2.3 Kế hoạch nghiên cứu'));
C.push(TCap('Bảng 6. Kế hoạch theo giai đoạn.'));
C.push(table([1900, 1500, 3760, 2200], ['Thời gian', 'Giai đoạn / WP', 'Nội dung chính', 'Sản phẩm'], [
  ['26/06 – 20/09/2026', 'Nội dung 1 (WP2)', 'Khảo sát, tái hiện [11], thực nghiệm sơ khởi, đề cương', 'Đề cương đã duyệt'],
  ['21/09 – 07/10', 'WP3', 'Làm sạch dữ liệu, tái hiện CARTE, kế hoạch triển khai', 'Báo cáo tiến độ 06/10'],
  ['08/10 – 21/10', 'Cổng 0 (WP3)', 'G0-1 đến G0-4; bổ sung tài liệu và phiếu đọc; cặp thứ hai', 'Báo cáo Cổng 0, biên bản GO hoặc PIVOT'],
  ['22/10 – 08/11', 'WP3', 'TB-HTL v0 (B→A), ablation C3 và C4, đối chứng nhãn xáo trộn; cặp A–C; chiều A→B; KB3', 'Bảng ablation, bảng cặp thứ hai, slide giữa kỳ'],
  ['09/11 – 15/11', 'Giữa kỳ', 'Báo cáo GVHD; chốt phương án Giai đoạn 2', 'Góp ý GVHD'],
  ['16/11 – 13/12', 'WP4', 'CARTE và DSN trên giao thức của nhóm; DANN, CORAL, L2-SP; TransTab, TabICL; SHAP, hiệu chỉnh xác suất, phân tích theo giới; cặp thứ ba nếu có', 'Toàn bộ bảng kết quả chính'],
  ['14/12 – 27/12', 'WP4', 'Kiểm định tổng hợp (Friedman – Nemenyi), đo tài nguyên, khóa số liệu', 'Số liệu cuối cùng (27/12)'],
  ['28/12/2026 – 05/01/2027', 'WP5', 'Viết báo cáo khóa luận và bản thảo bài báo', 'Báo cáo khóa luận'],
  ['06/01 – 21/01/2027', 'Bảo vệ', 'Chuẩn bị slide, phản biện, bảo vệ', '—'],
], { size: 18 }));
C.push(TCap('Bảng 7. Kế hoạch theo tuần đến giữa kỳ (theo mục 6.6 của đánh giá).'));
C.push(table([1300, 2960, 2960, 2140], ['Tuần', 'Tăng Nhật Minh', 'Phạm Xuân Thiên', 'Sản phẩm nộp'], [
  ['T1 (08–14/10)', 'hr_data.py, loại trùng, file chia chung; G0-1 (đã chạy 4 họ mô hình; TabPFN v2 chạy trong G0-2); tải mã KB1 cũ và bản thảo LNCS lên Drive', 'Hoàn tất EDA hai miền; làm sạch bộ HR 14.999 dòng và bảng ánh xạ khái niệm với IBM; cập nhật Bảng 1–2', 'KB1 v2; notebook EDA; bảng ánh xạ; 00_contributions.md'],
  ['T2 (15–21/10)', 'G0-3, G0-4', 'G0-2 (mô hình De Vos, stacking Chung, TabPFN v2)', 'Báo cáo Cổng 0; họp 21/10'],
  ['T3 (22–28/10)', 'TB-HTL v0 chiều B→A, k ∈ {10, 20, 50, 100}', 'Pipeline cặp IBM ↔ HR 14.999: baseline và zero-shot hai chiều', 'Kết quả TB-HTL v0; bảng cặp thứ hai'],
  ['T4 (29/10–04/11)', 'Ablation C3 (ρ) và C4 (neo/không neo, λ theo k); đối chứng nhãn xáo trộn', 'Chiều A→B; KB3 trên cả hai cặp', 'Bảng ablation; KB3'],
  ['T5 (05–08/11)', { span: 2, text: 'Cả nhóm: tổng hợp bảng và hình có CI, cập nhật bản thảo, slide giữa kỳ', shade: S }, 'Slide và bản thảo cập nhật'],
], { size: 18 }));
C.push(P('*Nếu kết luận Cổng 0 là PIVOT, tuần T3–T4 của Minh chuyển sang mở rộng phân tích trên cặp thứ hai và đưa TB-HTL vào như một phương pháp trong bảng so sánh.*'));
C.push(TCap('Bảng 8. Mức ưu tiên và ước lượng tài nguyên.'));
C.push(table([4100, 2300, 2960], ['Hạng mục', 'Ưu tiên', 'Ước lượng'], [
  ['KB1 v2 đa mô hình (G0-1)', 'Bắt buộc – trước giữa kỳ', 'Đã chạy 4 họ mô hình (~15 phút CPU) và TabPFN v2 (Colab T4; ba cặp R1 + R3 khoảng 40 phút)'],
  ['Cổng 0 (G0-2 đến G0-4)', 'Bắt buộc – trước giữa kỳ', '2–4 giờ CPU; TabPFN v2 < 1 giờ GPU'],
  ['Cặp miền thứ hai', 'Bắt buộc – trước giữa kỳ', '2–3 ngày công'],
  ['TB-HTL v0, ablation C3 và C4, FT-Canonical', 'Bắt buộc – trước giữa kỳ', '6–8 giờ GPU, chia nhiều phiên Colab'],
  ['CARTE, Domain Separation Networks', 'Bắt buộc – sau giữa kỳ', 'CARTE 5–10 giờ GPU; DSN 2–4 giờ GPU'],
  ['Chiều A→B đầy đủ; DANN, CORAL, L2-SP', 'Nên có – sau giữa kỳ', '3–5 giờ GPU'],
  ['TransTab, TabICL, mô hình tốt nhất của AL-Ali et al.', 'Nên có', 'TransTab 3–5 giờ GPU; còn lại < 1 giờ'],
  ['SHAP nguồn–đích, hiệu chỉnh xác suất, phân tích theo giới', 'Nên có', '< 2 giờ CPU'],
  ['Cặp miền thứ ba (ưu tiên dữ liệu thật)', 'Nên có', '2–3 ngày công'],
  ['TabLLM, FeatLLM, Tabula-8B, TP-BERTa, XTab; SMOTE, ADASYN, CTGAN; module giao diện', 'Tùy chọn', 'Chỉ làm nếu còn thời gian'],
], { size: 18 }));

C.push(H(1, 'B3. Kết quả dự kiến'));
C.push(B('**Sản phẩm khoa học:** một bài báo hội nghị quốc tế có chỉ mục Scopus (hội nghị cụ thể và hạn nộp do nhóm và GVHD chốt); báo cáo khóa luận tốt nghiệp gồm ba Nội dung.'));
C.push(B('**Sản phẩm phương pháp:** giao thức đánh giá chuyển giao xuyên nguồn cho dự đoán nghỉ việc (file chia dữ liệu chung, quy tắc tune, chọn ngưỡng, kiểm định); bảng ánh xạ khái niệm nhân sự giữa các nguồn; phương pháp TB-HTL kèm ablation.'));
C.push(B('**Sản phẩm phân tích:** đường cong học theo k cho các cặp nguồn; mức k* mà chuyển giao còn có ích; ảnh hưởng của ngữ nghĩa nhãn và mức trùng khái niệm; so sánh yếu tố rủi ro giữa các nguồn.'));
C.push(B('**Sản phẩm phần mềm:** kho mã nguồn (Git) tái lập được toàn bộ bảng và hình, kèm file kết quả thô và dự đoán thô.'));
C.push(B('**Thảo luận sử dụng có trách nhiệm:** đánh giá theo nhóm giới và khuyến nghị sử dụng mô hình trong vai trò hỗ trợ, không thay thế quyết định nhân sự.'));

// ============================================================ Appendix A: progress
C.push(new Paragraph({ children: [new PageBreak()] }));
C.push(H(1, 'Phụ lục A. Báo cáo tiến độ (đến 21/10/2026)'));
C.push(H(2, 'A1. Tiến độ công việc'));
C.push(table([3000, 1300, 1200, 1700, 2160], ['Hạng mục', 'Hạn', 'Phụ trách', 'Trạng thái', 'Ghi chú'], [
  ['Khảo sát 20 công trình; bổ sung 17 tài liệu theo đánh giá', '20/09; 21/10', 'Cả nhóm', st('Đã xong (bổ sung đã đưa vào B1.1)'), 'Phiếu đọc 10 bài: Thiên, 21/10'],
  ['KB1 v2 (G0-1)', '14/10', 'Minh', st('Đã chạy (4 họ mô hình 11/10; TabPFN v2 21/10)'), '–'],
  ['Mã KB1 cũ và cấu hình Random Forest', '14/10', 'Minh', st('Không còn: mã gốc bị mất'), 'Thay bằng KB1 v2 và truy vết A5.1c (17/10)'],
  ['Tái hiện [11] trên Yeast (KB2)', 'Xong', 'Cả nhóm', st('Đã xong (sơ bộ)'), 'Đã sửa mã: rút mẫu theo seed, khóa cache theo cấu hình'],
  ['Tái hiện CARTE [24] (KB2b)', '10/2026', 'Cả nhóm', st('Đã xong (sơ bộ)'), 'Kết quả ở A5.3'],
  ['Bản thảo bài báo LNCS', '14/10', 'Minh', st('Chưa tải lên Drive'), 'Bảng kết quả còn trống'],
  ['Làm sạch 2 miền, file chia chung', '04/10 → 14/10', 'Minh', st('Đang làm (chậm 3 ngày)'), 'hr_data.py và splits.py đã có; đã chạy trên file Kaggle của nhóm (16/10), còn lưu JSON lên Git'],
  ['EDA từng miền', '04/10 → 14/10', 'Thiên', st('Đang làm (chậm 3 ngày)'), 'Chưa có minh chứng trên Drive'],
  ['Bộ HR 14.999 dòng và bảng ánh xạ với IBM', '14/10', 'Thiên', st('Đã xong (21/10)'), 'Kèm cặp A↔D (Babushkin); A5.5'],
  ['G0-2 đường cong học chỉ-dữ-liệu-đích', '18/10', 'Thiên', st('Đã chạy (17–18/10, 6 mô hình gồm TabPFN v2)'), 'Còn LightGBM, AdaBoost theo danh sách 6.3'],
  ['G0-3 baseline chuyển giao đơn giản; G0-4 đối chứng xáo trộn', '18/10', 'Minh', st('Đã chạy (17/10)'), 'Kết luận PIVOT, A5.4'],
  ['00_contributions.md (RQ, ngưỡng đã chốt)', '18/10', 'Cả nhóm', st('Một phần: nội dung ở Bảng 5'), 'Chép sang file và chốt ngưỡng'],
  ['Cài đặt TB-HTL', 'Sau 21/10', 'Minh', st('Chưa làm (lùi theo quyết định GVHD)'), ''],
], { size: 18 }));

C.push(H(2, 'A2. Bộ dữ liệu'));
C.push(table([2500, 1800, 1500, 3560], ['Bộ dữ liệu', 'Vai trò', 'Số dòng', 'Ghi chú'], [
  ['IBM HR Analytics Employee Attrition & Performance', 'Miền A', '1.470', 'Dữ liệu hư cấu; 237 ca nghỉ việc (16,12%); không thiếu dữ liệu'],
  ['HR Analytics: Job Change of Data Scientists', 'Miền B', '19.158 → 19.084', 'Loại 74 dòng trùng đặc trưng (25 nhóm nhãn mâu thuẫn); bỏ city vì xác định hoàn toàn city_development_index; giá trị thiếu là hạng mục riêng'],
  ['HR Analytics (HR_comma_sep.csv, nhãn left)', 'Miền C – cặp cùng ngữ nghĩa với A', '14.999 → 11.991', 'Dữ liệu mô phỏng, đã được [8] và [31] dùng. Loại 3.008 dòng trùng hoàn toàn (20%; không có nhóm nhãn mâu thuẫn); còn 1.991 ca nghỉ việc (16,6%). 10 cột: mức hài lòng, đánh giá gần nhất, số dự án, giờ làm trung bình/tháng, thâm niên, tai nạn lao động, thăng chức 5 năm, phòng ban, bậc lương'],
  ['Employee turnover (E. Babushkin)', 'Miền D – cặp thứ ba, dữ liệu thật', '1.129 → 953', 'Nhãn event (đã nghỉ việc), cùng ngữ nghĩa với IBM. Loại 13 dòng trùng và 163 bản ghi lặp của cùng một người (trùng mọi cột trừ 5 điểm tính cách, nhãn luôn giống nhau; nếu giữ lại, Random Forest trong miền trên 3 khái niệm bị thổi phồng từ 0,566 lên 0,670 AUC-ROC); còn 953 người, 486 ca nghỉ việc (51,0%); file mã hóa latin-1; quần thể chủ yếu nghề nhân sự (67%), nữ (76%); event = 0 là quan sát bị kiểm duyệt (chưa nghỉ đến lúc thu thập). Khái niệm chung với IBM: giới tính, tuổi, thâm niên (stag tính theo tháng). Kết quả đầy đủ ở A5.5'],
  ['Employee Turnover (M. Stewart, 9.540 dòng); HRDataset v14; Attrition Rate of a Company', 'Ứng viên khác', '—', 'Cần kiểm chứng nguồn gốc và giấy phép; ưu tiên dữ liệu thật (Babushkin) hoặc dữ liệu doanh nghiệp đối tác đã ẩn danh'],
  ['Dataset01_HR_Analytics', 'Loại', '1.480', 'Bản sao mở rộng của IBM; dùng sẽ thổi phồng kết quả chuyển giao'],
  ['Yeast, Emotions; wina_pl, wine_dot_com_prices, wine_vivino_price', 'Kiểm chứng mã', '—', 'Benchmark tái hiện [11] và [24]'],
], { size: 18 }));
C.push(P('**Ánh xạ khái niệm A ↔ C và A ↔ D** đã chốt và kiểm tra chiều tác động ở Bảng A5.5a–b. Bản nháp ban đầu: mức hài lòng (JobSatisfaction, thang 1–4 ↔ satisfaction_level, 0–1); đánh giá hiệu suất (PerformanceRating ↔ last_evaluation); thâm niên (YearsAtCompany ↔ time_spend_company); thăng chức (YearsSinceLastPromotion < 5 ↔ promotion_last_5years); phòng ban (Department ↔ sales, gộp nhóm); mức lương (JobLevel hoặc tertile MonthlyIncome ↔ salary low/medium/high); làm thêm giờ (OverTime ↔ average_montly_hours theo ngưỡng). So với cặp A–B chỉ có 4 khái niệm, cặp A–C có khoảng 7, nên còn cho phép phân tích ảnh hưởng của mức trùng khái niệm.'));
C.push(P('*Nguồn tải dùng trong lần chạy KB1 v2 ngày 11/10:* IBM từ kho GitHub của IBM (IBM/employee-attrition-aif360, 1.470 × 35, khớp bản Kaggle); Job Change từ gói R dlookr (jobchange, 19.158 dòng, 4.777 ca dương, khớp bản Kaggle). *Xác nhận ngày 16/10:* chạy lại trên file Kaggle gốc của nhóm (aug_train.csv và WA_Fn-UseC_-HR-Employee-Attrition.csv) cho kết quả trùng khớp hoàn toàn với lần chạy 11/10 (760/760 ô, lệch 0,0000); file IBM trùng từng byte, file Job Change chỉ khác cách ghi hạng mục company_size. Kết quả lưu ở results/kb1_v2_kaggle/ kèm bảng so sánh.'));

C.push(H(2, 'A3. Mã nguồn và tái lập'));
C.push(table([2600, 4560, 2200], ['File / gói', 'Chức năng', 'Trạng thái'], [
  ['gate0/hr_data.py', 'Đọc IBM và Job Change (file Kaggle hoặc bản sao), loại trùng, ánh xạ khái niệm chung (4 hoặc 5 khái niệm), đủ đặc trưng', st('Đã có (11/10)')],
  ['gate0/splits.py', 'File chia chung: R lần lặp, test 20% phân tầng, k mẫu lồng nhau có ít nhất 1 mẫu dương; hàm kiểm thử', st('Đã có, đã kiểm thử')],
  ['gate0/kb1_v2.py', 'G0-1: 2×2 với LR, RF, RF có điều chuẩn, XGBoost, quy tắc; hai cách mã hóa; lưu kết quả, dự đoán thô, cấu hình và sanity check, tên file gắn mã băm cấu hình', st('Đã chạy (cfg 99d14779)')],
  ['gate0/kb1_v2_summary.py', 'CI 95% có hiệu chỉnh, corrected resampled t-test, Holm, bảng và hình', st('Đã chạy')],
  ['tabular_tl_repro (KB2)', 'Sửa theo O3/O6: rút lại n mẫu theo từng seed (cờ --fixed-downstream-sample để giữ như bài gốc); cache và file kết quả gắn mã băm cấu hình', st('Đã sửa, đã chạy thử')],
  ['code_thucnghiem_carte.py (KB2b)', 'Tái hiện CARTE, đối chiếu với kết quả công bố', st('Đã có')],
  ['gate0/g0_23.py', 'Cổng 0: G0-2 (LR, RF, XGBoost, CatBoost, stacking; TabPFN v2 với --only TabPFN), G0-3 (7 baseline chuyển giao), G0-4 (đối chứng xáo trộn); lưu file chia, kết quả, dự đoán thô, cấu hình', st('Đã chạy (17/10)')],
  ['gate0/g0_decision.py', 'Áp tiêu chí GO/PIVOT: so sánh bắt cặp với baseline đích mạnh nhất, CI hiệu chỉnh, Holm; đối chứng; hình 6–7', st('Đã chạy (17/10)')],
  ['chay_TabPFN_v2_Cong0_Colab.ipynb', 'Chạy TabPFN v2 trên Colab GPU với cùng 30 lần chia, rồi tính lại kết luận', st('Đã chạy (18/10, 390 lần, Tesla T4)')],
  ['gate0/pairs.py, kb1_pair.py, g0_pair.py, kb1_pair_summary.py, pairs_synthesis.py', 'Bộ mã nhiều cặp: bộ đọc 4 miền và ánh xạ khái niệm theo cặp; 2×2 và Cổng 0 cho cặp bất kỳ (với AB trùng kết quả cũ đến 10⁻⁶); tổng hợp ba cặp, Friedman – Nemenyi', st('Đã chạy (21/10)')],
  ['chay_TabPFN_v2_R1_R3_Colab.ipynb', 'TabPFN v2 cho 2×2 của AB (R1) và cho hai cặp mới', st('Đã chạy (21/10, Tesla T4): 300 lần 2×2 và 840 lần Cổng 0')],
  ['gate0/kb1_tai_dung.py', 'Truy vết bảng KB1 cũ: RF mặc định với 5 cách mã hóa 4 khái niệm chung (A5.1c)', st('Đã chạy (17/10)')],
  ['Mã KB1 cũ', 'Không còn (mất trước khi lưu lên Git); thay bằng KB1 v2 và kb1_tai_dung.py', st('Không còn')],
  ['Bản thảo LNCS; sản phẩm của Thiên', 'Tải lên Drive hoặc Git', st('Chưa')],
  ['Kho Git riêng tư; requirements.txt ghi phiên bản', 'Mỗi bảng trong bài có một lệnh chạy lại; cập nhật hằng tuần', st('Đang thiết lập')],
], { size: 18 }));
C.push(P('Lệnh tái lập KB1 v2: `python kb1_v2.py --ibm <file IBM> --jc <file aug_train.csv> --out results/kb1_v2` rồi `python kb1_v2_summary.py results/kb1_v2/results_kb1v2_<cfg>.csv`. Phiên bản dùng trong lần chạy: Python 3.13, scikit-learn 1.8, XGBoost 3.4.1, pandas 3.0.'));

C.push(H(2, 'A4. Kịch bản thực nghiệm và giao thức'));
C.push(table([900, 2700, 3700, 1060, 1000], ['KB', 'Mục đích', 'Thiết lập chính', 'Phụ trách, hạn', 'Trạng thái'], [
  ['G0-1', 'KB1 v2: mất đặc trưng và domain shift (RQ1)', 'LR (L2), RF, RF có điều chuẩn, XGBoost, TabPFN v2; 10 lần chia; hai cách mã hóa; CI và kiểm định có hiệu chỉnh', 'Minh, 14/10', st('Đã chạy (11/10 và 21/10, gồm TabPFN v2)')],
  ['G0-2', 'Đường cong học chỉ-dữ-liệu-đích (RQ2)', 'k ∈ {10, 20, 50, 100, 200, 500, toàn bộ}; mô hình De Vos et al., stacking Chung et al., TabPFN v2; R = 30', 'Thiên, 18/10', st('Đã chạy (17–18/10); còn LightGBM, AdaBoost')],
  ['G0-3', 'Baseline chuyển giao đơn giản (RQ2)', 'Zero-shot; stacking điểm nguồn; trung bình hạng w(k) chọn bằng kiểm định chéo; LR neo hệ số nguồn', 'Minh, 18/10', st('Đã chạy (17/10)')],
  ['G0-4', 'Đối chứng', 'Lặp G0-3 với mô hình nguồn học trên nhãn nguồn bị xáo trộn', 'Minh, 18/10', st('Đã chạy (17/10)')],
  ['KB2', 'Kiểm chứng mã tái hiện [11]', 'Yeast, 3/14 nhiệm vụ, 5 seed, không tune', '—', st('Đã chạy')],
  ['KB2b', 'Kiểm chứng mã CARTE [24]', '3 bộ giá rượu, 32 và 64 mẫu, seed 1–2', '—', st('Đã chạy')],
  ['KB3', 'C1 – căn chỉnh khái niệm (H3a)', 'Thang đo của nguồn / căn chỉnh theo miền / căn chỉnh tự động theo tên cột; cả hai cặp', 'Thiên, T4', st('Chưa (có bằng chứng sớm)')],
  ['KB4', 'TB-HTL so với baseline (RQ2)', 'Baseline theo B2.2; mọi k; R = 30 (10 với baseline nặng)', 'Minh, T3 → sau giữa kỳ', st('Chưa')],
  ['KB5', 'C3 – tắt nhánh riêng (H3c)', 'ρ ∈ {0; 0,2; 0,4; 0,6}; tiền huấn luyện chỉ khái niệm chung', 'Minh, T4', st('Chưa')],
  ['KB6', 'C4 – thích ứng (H3d)', 'Neo/không neo; λ theo k bằng kiểm định chéo; head chung/riêng; DANN, CORAL, L2-SP sau giữa kỳ', 'Minh, T4', st('Chưa')],
  ['KB7', 'Đánh giá tổng thể (RQ5)', 'Hai chiều; Brier, ECE; theo nhóm giới; SHAP; thời gian', 'Cả nhóm, WP4', st('Chưa')],
  ['KB8', 'Ngữ nghĩa nhãn (RQ4)', 'Cặp cùng ngữ nghĩa A ↔ C, A ↔ D so với cặp khác ngữ nghĩa A ↔ B', 'Thiên, T3', st('Đã chạy (21/10, CPU)')],
], { size: 18 }));
C.push(P('**Giao thức chuẩn áp dụng từ KB3** (mục 6.4 của đánh giá):'));
C.push(B('**Dữ liệu:** loại dòng trùng trước khi chia; ghi số dòng và số ca dương sau mỗi bước.'));
C.push(B('**Chia dữ liệu:** một file chia chung cho mọi phương pháp (JSON, lưu trong Git); k mẫu phân tầng, lồng nhau, có ít nhất một mẫu dương, thay đổi theo lần lặp; miền nguồn giữ 10% làm validation.'));
C.push(B('**Chống rò rỉ:** imputer, encoder, scaler, chuẩn hóa thứ hạng của khái niệm chung, CORAL và tái lấy mẫu chỉ fit trên phần huấn luyện của từng lần lặp (sklearn Pipeline).'));
C.push(B('**Sanity check:** xáo trộn nhãn đích phải cho AUC ≈ 0,5; baseline lớp đa số; overfit một batch nhỏ với mô hình sâu; in kích thước và số ca dương của từng tập.'));
C.push(B('**Lưu trữ:** dự đoán thô (id, y_true, y_score) của mọi lần chạy; cấu hình và mã commit trong mỗi dòng kết quả.'));

C.push(H(2, 'A5. Kết quả chạy thực nghiệm'));
C.push(H(3, 'A5.1 KB1 v2 – kiểm định chi tiết'));
C.push(P('Bảng tổng hợp và hình ở mục B1.3 (Bảng 4, Hình 3); bảng dưới đây cho chênh lệch AUC-ROC từ trong-miền sang xuyên-miền trên 4 khái niệm chung. p thường là paired t-test không hiệu chỉnh, p hiệu chỉnh là corrected resampled t-test [40] với tỷ lệ test/train 0,25, p Holm hiệu chỉnh cho 10 phép so sánh (5 mô hình × 2 chiều) trong mỗi cách mã hóa. So với các p thường, p hiệu chỉnh lớn hơn đáng kể, đúng như nhận xét O3.'));
C.push(table([1500, 700, 1700, 760, 760, 760, 1200, 700, 700, 700, 680], ['Mã hóa', 'Chiều', 'Mô hình', 'Trong-miền', 'Xuyên-miền', 'Δ', 'CI 95% hiệu chỉnh', 'p thường', 'p hiệu chỉnh', 'p Holm', 'Tỷ lệ'], K.tests, { size: 15 }));
C.push(TCap('Bảng A5.1b. Độ nhạy theo cách mã hóa và tập khái niệm (AUC-ROC trung bình, 10 lần chia).'));
C.push(table([1700, 1500, 1000, 1290, 1290, 1290, 1290], ['Khái niệm', 'Mã hóa', 'Mô hình', 'Trong-miền A', 'B→A', 'Trong-miền B', 'A→B'], K.sens, { size: 17 }));

C.push(H(3, 'A5.1c Truy vết bảng KB1 cũ (mã gốc không còn)'));
C.push(P('Mã đã tạo bảng 2×2 cũ (Random Forest; B→A 0,498) không được lưu lại, nên không thể chạy lại đúng cấu hình. Để trả lời câu hỏi “vì sao ra 0,498”, nhóm giữ nguyên Random Forest mặc định và 10 lần chia của KB1 v2, chỉ thay cách đưa 4 khái niệm chung vào mô hình theo các lựa chọn thường gặp trong mã viết nhanh (script gate0/kb1_tai_dung.py, chạy trên file Kaggle gốc ngày 17/10/2026).'));
C.push(TCap('Bảng A5.1c. AUC-ROC trung bình (± ĐLC) của Random Forest mặc định theo cách mã hóa 4 khái niệm chung.'));
C.push(table([3300, 1150, 1150, 1150, 1150, 1100], ['Cách mã hóa', 'Trong-miền A', 'Trong-miền B', 'B→A', 'A→B', '|Lệch| TB với bảng cũ'], [
  [{ text: 'Bảng cũ (cấu hình không rõ)', shade: 'F2F2F2' }, { text: '0,581', shade: 'F2F2F2' }, { text: '0,561', shade: 'F2F2F2' }, { text: '0,498 ± 0,045', shade: 'F2F2F2' }, { text: '0,567 ± 0,008', shade: 'F2F2F2' }, { text: '–', shade: 'F2F2F2' }],
  ['V0. Ánh xạ của KB1 v2, đơn vị gốc', '0,572', '0,564', '0,569 ± 0,042', '0,536 ± 0,012', '0,028'],
  ['V1. Học vấn và kinh nghiệm của B mã hóa theo thứ tự chữ cái (LabelEncoder)', '0,575', '0,566', '0,525 ± 0,047', '0,493 ± 0,009', '0,028'],
  ['V2. Chỉ học vấn của B mã hóa theo chữ cái', '0,575', '0,567', '0,550 ± 0,063', '0,485 ± 0,006', '0,036'],
  ['V3. Chỉ kinh nghiệm của B mã hóa theo chữ cái', '0,575', '0,567', '0,488 ± 0,014', '0,442 ± 0,011', '0,037'],
  ['V4. Như V0 nhưng không chặn kinh nghiệm của A (0–40 năm)', '0,575', '0,564', '0,569 ± 0,042', '0,522 ± 0,011', '0,031'],
], { size: 17 }));
C.push(P('Ba nhận xét. (1) Số trong-miền của bảng cũ (0,581 và 0,561) khớp mọi biến thể trong khoảng ±0,01, nên phần “mất 0,21–0,23 AUC do bỏ đặc trưng” với Random Forest là tái lập được. (2) Không biến thể nào tái tạo đồng thời B→A ≈ 0,498 và A→B ≈ 0,567, nên không xác định được chính xác cấu hình cũ. (3) Chỉ riêng cách mã hóa đã làm B→A dao động từ 0,488 đến 0,569 và A→B từ 0,442 đến 0,536 với cùng một mô hình và cùng các lần chia. Mức 0,498 rơi đúng vào vùng mà mã hóa không nhất quán giữa hai miền (ví dụ kinh nghiệm của B bị mã hóa theo thứ tự chữ cái: “<1”, “>20”, “1”, “10”, “11”…) kéo xuyên miền xuống quanh ngẫu nhiên. Vì vậy con số 0,498 được xem là sản phẩm của cách mã hóa, không phải bằng chứng về domain shift, và được thay hoàn toàn bằng KB1 v2.'));

C.push(H(3, 'A5.2 KB2 – Tái hiện [11] trên Yeast'));
C.push(P('ROC-AUC trung bình (3/14 nhiệm vụ, 5 seed, không tune). Không in đậm vì chưa xét ý nghĩa thống kê. Lưu ý: lần chạy này dùng mã cũ, cố định một lần rút n mẫu cho mọi seed (đúng như repo gốc), nên độ lệch giữa các seed chỉ phản ánh nhiễu khởi tạo; điều này giải thích hiện tượng n = 10 thấp hơn n = 4. Mã đã được sửa để rút lại mẫu theo seed; theo quyết định của GVHD, KB2 không được mở rộng thêm.'));
C.push(table([520, 720, 720, 720, 720, 720, 720, 720, 720, 720, 720, 720, 720],
  ['n', 'FT FS', 'FT LH-E2E', 'FT MLP-E2E', 'FT LH', 'FT MLP', 'MLP FS', 'MLP LH-E2E', 'MLP MLP-E2E', 'MLP LH', 'MLP MLP', 'CatBoost FS', 'CatBoost Stacking'], [
  ['200', '0,661', '0,712', '0,718', '0,732', '0,699', '0,684', '0,720', '0,733', '0,739', '0,734', '0,715', '0,732'],
  ['100', '0,630', '0,706', '0,706', '0,738', '0,702', '0,625', '0,692', '0,717', '0,733', '0,733', '0,659', '0,711'],
  ['20', '0,595', '0,653', '0,640', '0,680', '0,634', '0,602', '0,668', '0,650', '0,673', '0,666', '0,567', '0,586'],
  ['10', '0,552', '0,578', '0,609', '0,600', '0,593', '0,536', '0,542', '0,518', '0,540', '0,524', '0,555', '0,570'],
  ['4', '0,525', '0,593', '0,603', '0,614', '0,615', '0,527', '0,568', '0,564', '0,562', '0,558', '0,547', '0,568'],
], { size: 15 }));

C.push(H(3, 'A5.3 KB2b – Tái hiện CARTE [24] trên 3 bộ dữ liệu giá rượu'));
C.push(P('Nhóm chạy 12 lượt (3 bộ × 32 và 64 mẫu × seed 1–2, bagging 5 mô hình thay vì 10) và ghép với file kết quả công bố của tác giả theo đúng bộ dữ liệu, cỡ huấn luyện và seed. Tương quan giữa 12 cặp là 0,95; chênh lệch tuyệt đối trung bình 0,043 R²; trung bình của nhóm nằm trong ±1 độ lệch chuẩn qua 10 seed của bài báo ở 5/6 cấu hình. Đây là kiểm chứng mã; theo Phụ lục D của đánh giá, CARTE sẽ được chạy lại trên giao thức và dữ liệu nhân sự của nhóm sau giữa kỳ, không dùng số liệu công bố trong bảng so sánh chính.'));
C.push(table([2000, 900, 1600, 1500, 1800, 1560], ['Bộ dữ liệu', 'Số mẫu', 'R² nhóm (TB, 2 seed)', 'R² công bố, cùng seed', 'R² công bố, 10 seed (TB ± ĐLC)', 'CatBoost công bố, cùng seed'], [
  ['wina_pl', '32', '0,128', '0,131', '0,117 ± 0,080', '0,059'], ['wina_pl', '64', '0,222', '0,213', '0,279 ± 0,056', '0,155'],
  ['wine_dot_com_prices', '32', '0,317', '0,350', '0,333 ± 0,086', '0,389'], ['wine_dot_com_prices', '64', '0,480', '0,511', '0,495 ± 0,045', '0,444'],
  ['wine_vivino_price', '32', '0,516', '0,564', '0,515 ± 0,098', '0,409'], ['wine_vivino_price', '64', '0,613', '0,628', '0,614 ± 0,035', '0,544'],
], { size: 18 }));
C.push(image(C3, 6.3, 2.34));
C.push(Caption('Hình 4. R² theo số mẫu huấn luyện: CARTE do nhóm chạy lại, CARTE công bố và CatBoost không tiền huấn luyện (cùng seed 1–2).'));
C.push(image(C4, 3.2, 3.05));
C.push(Caption('Hình 5. Đối chiếu từng lượt chạy CARTE của nhóm với kết quả công bố.'));
C.push(P('Giới hạn: KB2b là bài toán hồi quy, tri thức được chuyển từ đồ thị tri thức bên ngoài chứ không từ một bảng nguồn có nhãn; nhóm mới chạy 2/10 seed và 2/7 cỡ huấn luyện.'));

C.push(H(3, 'A5.4 Cổng 0 – G0-2, G0-3 và G0-4 (chạy ngày 17–18/10/2026)'));
C.push(P('**Thiết lập.** 30 lần chia dùng chung (splits.py: train/test 80/20 phân tầng; k mẫu lồng nhau, phân tầng, có ít nhất một mẫu dương), chạy trên file Kaggle gốc. **G0-2** – mô hình chỉ dùng dữ liệu đích, trên đủ đặc trưng của miền đích: LR, Random Forest, XGBoost, CatBoost (theo benchmark De Vos et al. [43]), stacking LR + RF + XGBoost (Chung et al. [5]) và TabPFN v2 [25] (chạy trên Colab GPU T4 ngày 18/10, cùng file chia; k = toàn bộ ở Job Change không chạy vì vượt giới hạn 10.000 dòng huấn luyện của TabPFN v2). **G0-3** – tám baseline chuyển giao đơn giản, cùng dùng mô hình nguồn LR học trên toàn bộ miền nguồn với 4 khái niệm chung đã căn chỉnh theo miền (C1): zero-shot; trung bình hạng giữa Random Forest chỉ dùng đích và điểm nguồn như pilot ở Phụ lục A của đánh giá (bổ sung ngày 21/10, w chọn bằng kiểm định chéo); stacking điểm nguồn với LR hoặc XGBoost; XGBoost khởi tạo từ logit nguồn (base_margin); tăng cường đặc trưng Daumé [33]; trung bình hạng w(k), với w ∈ {0; 0,25; 0,5; 0,75; 1} chọn bằng kiểm định chéo trên k mẫu; LR neo hệ số nguồn (logit nguồn làm offset, phạt L2 phần lệch, cùng tinh thần L2-SP [26]). **G0-4** – lặp zero-shot, stacking + LR, trung bình hạng và LR neo với mô hình nguồn học trên nhãn nguồn bị xáo trộn. Mọi phương pháp dùng siêu tham số mặc định cố định ở mọi k (Cổng 0 không tune); tiền xử lý chỉ fit trên k mẫu; bộ căn chỉnh C1 của miền đích fit trên đặc trưng không nhãn của phần train đích. Tiêu chí GO/PIVOT giữ đúng như đã chốt ở B2.2; so sánh bắt cặp theo lần chia, CI 95% có hiệu chỉnh [40], Holm trên 24 phép so sánh của mỗi chiều. Baseline đích mạnh nhất được chọn sau khi xem kết quả tại từng k, nên phép so sánh nghiêng về phía baseline, tức thận trọng với GO.'));
C.push(TCap('Bảng A5.4a. Chiều B→A (đích IBM, tỷ lệ dương 0,160): PR-AUC trung bình qua 30 lần chia theo số mẫu có nhãn k của miền đích. In đậm: baseline chỉ dùng đích tốt nhất tại mỗi k.'));
C.push(table([2560, 970, 970, 970, 970, 970, 970, 980], ['Phương pháp', 'k = 10', '20', '50', '100', '200', '500', 'Toàn bộ'], G0.curveA, { size: 16 }));
C.push(TCap('Bảng A5.4b. Chiều A→B (đích Job Change, tỷ lệ dương 0,249): PR-AUC trung bình qua 30 lần chia.'));
C.push(table([2560, 970, 970, 970, 970, 970, 970, 980], ['Phương pháp', 'k = 10', '20', '50', '100', '200', '500', 'Toàn bộ'], G0.curveB, { size: 16 }));
C.push(image(ROOT + '/results/g0_23/g0_hinh_duong_cong.png', 6.4, 2.81));
C.push(Caption('Hình 6. Đường cong PR-AUC theo k: các mô hình chỉ dùng dữ liệu đích, chuyển giao tốt nhất tại mỗi k (nét đứt đen), zero-shot (chấm hồng) và mức đoán ngẫu nhiên.'));
C.push(TCap('Bảng A5.4c. Kiểm định tiêu chí GO tại k ≤ 50: baseline chuyển giao tốt nhất so với baseline chỉ dùng đích mạnh nhất tại cùng k (Δ PR-AUC).'));
C.push(table([640, 420, 2150, 2550, 760, 1500, 620, 720], ['Chiều', 'k', 'Baseline đích mạnh nhất (PR-AUC)', 'Chuyển giao tốt nhất (PR-AUC)', 'Δ', 'CI 95% hiệu chỉnh', 'p Holm', 'Đạt GO'],
  [...G0.goA.map(r => ['B→A', ...r]), ...G0.goB.map(r => ['A→B', ...r])], { size: 16 }));
C.push(image(ROOT + '/results/g0_23/g0_hinh_delta.png', 6.4, 2.62));
C.push(Caption('Hình 7. Chênh lệch PR-AUC của từng baseline chuyển giao so với baseline chỉ dùng đích mạnh nhất tại k ≤ 50, CI 95% có hiệu chỉnh. Nét đứt: ngưỡng GO +0,02.'));
C.push(P('**Nhận xét.**', { extra: { keepNext: true } }));
C.push(...numbered([
  '**Không phương pháp chuyển giao nào đạt tiêu chí GO, ở cả hai chiều.** Trong 48 phép so sánh (8 phương pháp × 3 mức k × 2 chiều) chỉ có hai chênh lệch dương, đều rất nhỏ và CI chứa 0: trung bình hạng (LR) ở A→B với k = 10 (+0,012; CI [−0,047; +0,070]) và trung bình hạng RF + nguồn ở B→A với k = 10 (+0,004; CI [−0,043; +0,051]). Ở B→A, Random Forest chỉ học trên 10 nhân viên IBM có đủ đặc trưng đã đạt 0,321 PR-AUC; chỉ biến thể trộn với chính Random Forest nhỉnh hơn được 0,004.',
  '**Nguồn có mang thông tin, nhưng không thêm được gì khi đã có vài mẫu đích (G0-4).** Zero-shot vượt bản dùng nhãn nguồn xáo trộn ' + G0.ctrlA.ZS.zero.d + ' PR-AUC ở B→A (CI [' + G0.ctrlA.ZS.zero.lo + '; ' + G0.ctrlA.ZS.zero.hi + ']) và ' + G0.ctrlB.ZS.zero.d + ' ở A→B (CI [' + G0.ctrlB.ZS.zero.lo + '; ' + G0.ctrlB.ZS.zero.hi + ']); AUC-ROC 0,628 so với 0,493 và 0,607 so với 0,457. Khi đã có k mẫu đích, stacking và LR neo chỉ hơn bản xáo trộn không quá 0,012 ở mọi k; trung bình hạng hơn 0,03–0,05 ở k ≤ 20 nhưng CI chứa 0. So với chính mô hình cùng họ chỉ dùng đích, chuyển giao thêm tối đa 0,011 PR-AUC (bỏ qua trường hợp XGBoost suy biến ở mục 3).',
  '**Hiện tượng kỹ thuật cần ghi.** XGBoost mặc định với k = 10 không tách được nút nào (tổng hessian nhỏ hơn min_child_weight = 1), nên dự đoán hằng và PR-AUC đúng bằng tỷ lệ dương; vì vậy XGBoost khởi tạo từ nguồn ở k = 10 trùng với zero-shot. Điều này không ảnh hưởng kết luận vì baseline mạnh nhất ở k ≤ 50 là Random Forest (B→A) và LR hoặc TabPFN v2 (A→B). Stacking [5] chỉ dẫn đầu khi k ≥ 100 ở B→A (0,637 khi dùng toàn bộ dữ liệu).',
  '**Lý giải.** Bốn khái niệm chung (giới tính, học vấn, kinh nghiệm, đào tạo) chỉ mang tín hiệu yếu (zero-shot AUC-ROC khoảng 0,61–0,63), trong khi đặc trưng riêng của miền đích (làm thêm giờ, thu nhập, mức độ hài lòng ở IBM; city_development_index ở Job Change) mạnh hơn nhiều. Vài chục mẫu đích đã đủ để vượt toàn bộ thông tin mà nguồn chuyển sang được qua bốn khái niệm này. Nút thắt của cặp A–B vì vậy là mức trùng khái niệm thấp, không phải lệch miền – khớp với KB1 v2.',
  '**TabPFN v2 (chạy ngày 18/10, 390 lần).** Ở A→B, TabPFN v2 là baseline chỉ dùng đích mạnh nhất từ k = 50 (0,409 ở k = 50; 0,455 ở k = 100; 0,517 ở k = 500). Ở B→A, TabPFN v2 không dẫn đầu ở k ≤ 50 (0,290 so với Random Forest 0,321 ở k = 10) và chỉ ngang stacking khi dùng toàn bộ dữ liệu (0,634 so với 0,637). Kết luận PIVOT không đổi khi thêm TabPFN v2, đúng như dự kiến vì TabPFN chỉ làm baseline chỉ dùng đích mạnh hơn.',
]));
C.push(P('**Các điểm chưa đầy đủ so với đánh giá (nhóm hoàn thiện trước hoặc ngay sau 21/10).** (1) G0-2 chưa có LightGBM và AdaBoost trong danh sách mô hình của mục 6.3 (TabPFN v2 đã bổ sung ngày 18/10); (2) biến thể trung bình hạng Random Forest + zero-shot như pilot của GVHD đã bổ sung ngày 21/10 cho cả ba cặp (Bảng A5.4a–c, A5.5; đối chiếu với pilot ở nhận xét 6 của A5.5); (3) Cổng 0 mới báo PR-AUC và AUC-ROC, chưa báo Brier, ECE, F1/G-Mean tại ngưỡng, thời gian chạy và kiểm tra xáo trộn nhãn đích theo giao thức 6.4. Các bổ sung này chỉ có thể làm baseline chỉ dùng đích mạnh hơn hoặc bổ sung chỉ số phụ, nên không làm thay đổi kết luận PIVOT.'));
C.push(P('**Kết luận Cổng 0: PIVOT ở cả hai chiều.** Theo quy tắc đã chốt ở B2.2, TB-HTL không còn là đóng góp trung tâm mà là một phương pháp trong bảng so sánh; trọng tâm chuyển sang (a) giao thức đánh giá và (b) phân tích “khi nào chuyển giao xuyên nguồn có ích”. Kết quả Cổng 0 là kết quả đầu tiên của (b). Ba hướng đề xuất để thảo luận với GVHD ngày 21/10: (i) cặp IBM ↔ HR 14.999 dòng có nhiều khái niệm chung hơn (mức hài lòng, đánh giá hiệu suất, thâm niên, mức lương, phòng ban) và cùng ngữ nghĩa nhãn – kiểm tra lợi ích có xuất hiện khi mức trùng khái niệm tăng hay không (RQ4) – đã thực hiện ngày 21/10 cùng cặp IBM ↔ Babushkin, xem A5.5; (ii) mô phỏng tổ chức có hồ sơ nghèo bằng cách giới hạn đặc trưng của miền đích – kiểm tra chuyển giao có ích khi đích thiếu đặc trưng riêng hay không; (iii) thay đổi kích thước nguồn và mức trùng khái niệm để vẽ vùng mà chuyển giao có ích.'));

C.push(H(3, 'A5.5 Cặp miền thứ hai và thứ ba (R3, RQ4; chạy ngày 21/10/2026)'));
C.push(P('**Thiết lập.** Cùng giao thức với A5.1 (2×2, 10 lần chia) và A5.4 (Cổng 0, 30 lần chia, cùng tiêu chí GO/PIVOT), áp dụng cho hai cặp mới có **cùng ngữ nghĩa nhãn** với IBM (đã nghỉ việc): A ↔ C (HR 14.999, dữ liệu mô phỏng, nhiều khái niệm chung) và A ↔ D (Babushkin, dữ liệu thật, ít khái niệm chung). Tập khái niệm chính được chốt trước khi chạy (Bảng A5.5a–b); chiều tác động của từng khái niệm được kiểm tra bằng AUC-ROC đơn biến trên mỗi miền theo yêu cầu Y1. Các mô hình CPU chạy đủ; TabPFN v2 chạy bằng notebook Colab ngày 21/10 với cùng file chia (kết quả TabPFN v2 cho đích A trùng tuyệt đối giữa các cặp và với lần chạy 18/10, xác nhận tái lập).'));
C.push(TCap('Bảng A5.5a. Ánh xạ khái niệm IBM (A) ↔ HR 14.999 (C) và chiều tác động (AUC-ROC đơn biến; < 0,5 nghĩa là giá trị cao đi kèm rủi ro thấp).'));
C.push(table([1900, 2050, 2250, 900, 900, 1360], ['Khái niệm', 'Cột ở A', 'Cột ở C', 'AUC ở A', 'AUC ở C', 'Chiều'], PJ.map_AC, { size: 16 }));
C.push(TCap('Bảng A5.5b. Ánh xạ khái niệm IBM (A) ↔ Babushkin (D) và chiều tác động.'));
C.push(table([1900, 2050, 2250, 900, 900, 1360], ['Khái niệm', 'Cột ở A', 'Cột ở D', 'AUC ở A', 'AUC ở D', 'Chiều'], PJ.map_AD, { size: 16 }));
C.push(P('Ở cặp A ↔ C, **thâm niên tác động ngược chiều**: ở IBM làm lâu thì ít nghỉ, ở HR 14.999 làm lâu lại nghỉ nhiều hơn. Theo yêu cầu Y1, nhóm giữ tập chính đã chốt trước (5 khái niệm) cho kết luận Cổng 0 và chạy thêm phân tích phụ với tập “cùng chiều” bỏ thâm niên; tập phụ được chọn sau khi xem nhãn nên chỉ dùng để giải thích, không dùng để kết luận GO.'));
C.push(TCap('Bảng A5.5c. Thí nghiệm 2×2 cặp A ↔ C: AUC-ROC trung bình (PR-AUC) qua 10 lần chia, tập khái niệm chính.'));
C.push(table([1240, 1015, 1015, 1015, 1015, 1015, 1015, 1015, 1015], ['Mô hình', 'Đủ đặc trưng A', 'Trong-miền A', 'C→A (std)', 'C→A (C1)', 'Đủ đặc trưng C', 'Trong-miền C', 'A→C (std)', 'A→C (C1)'], PJ.kb1_AC, { size: 14 }));
C.push(TCap('Bảng A5.5d. Thí nghiệm 2×2 cặp A ↔ D: AUC-ROC trung bình (PR-AUC) qua 10 lần chia, tập khái niệm chính.'));
C.push(table([1240, 1015, 1015, 1015, 1015, 1015, 1015, 1015, 1015], ['Mô hình', 'Đủ đặc trưng A', 'Trong-miền A', 'D→A (std)', 'D→A (C1)', 'Đủ đặc trưng D', 'Trong-miền D', 'A→D (std)', 'A→D (C1)'], PJ.kb1_AD, { size: 14 }));
C.push(TCap('Bảng A5.5e. Độ nhạy theo tập khái niệm và cách mã hóa, LR (AUC-ROC). Cặp A ↔ C: core = 5 khái niệm chốt trước, consistent = bỏ thâm niên, ext = thêm làm thêm giờ và phòng ban; cặp A ↔ D: core = 3 khái niệm, ext = thêm nhóm nghề.'));
C.push(table([1700, 900, 1350, 1350, 1350, 1350], ['Cặp / tập', 'Mã hóa', 'Trong-miền A', 'Nguồn → A', 'Trong-miền đích kia', 'A → đích kia'],
  [...PJ.sens_AC.map(r => ['A ↔ C / ' + r[0], ...r.slice(1)]), ...PJ.sens_AD.map(r => ['A ↔ D / ' + r[0], ...r.slice(1)])], { size: 16 }));
C.push(TCap('Bảng A5.5f. Cổng 0 cho hai cặp mới: baseline chuyển giao tốt nhất so với baseline chỉ dùng đích mạnh nhất tại cùng k ≤ 50 (Δ PR-AUC, CI 95% hiệu chỉnh). Tập khái niệm chính.'));
C.push(table([900, 500, 2300, 2500, 800, 1700, 660], ['Chiều', 'k', 'Baseline đích mạnh nhất (PR-AUC)', 'Chuyển giao tốt nhất (PR-AUC)', 'Δ', 'CI 95% hiệu chỉnh', 'Đạt GO'],
  [...PJ.go_AC, ...PJ.go_AD], { size: 16 }));
C.push(image(ROOT + '/results/g0_AC/g0_hinh_duong_cong.png', 6.4, 2.81));
C.push(Caption('Hình 8. Cặp A ↔ C: đường cong PR-AUC theo k (tập khái niệm chính).'));
C.push(image(ROOT + '/results/g0_AD/g0_hinh_duong_cong.png', 6.4, 2.81));
C.push(Caption('Hình 9. Cặp A ↔ D: đường cong PR-AUC theo k.'));
C.push(TCap('Bảng A5.5g. Phân tích phụ cặp A ↔ C với tập “cùng chiều” (bỏ thâm niên; chọn sau khi xem nhãn).'));
C.push(table([900, 500, 2300, 2500, 800, 1700, 660], ['Chiều', 'k', 'Baseline đích mạnh nhất (PR-AUC)', 'Chuyển giao tốt nhất (PR-AUC)', 'Δ', 'CI 95% hiệu chỉnh', 'Đạt GO'], PJ.go_ACc, { size: 16 }));
C.push(TCap('Bảng A5.5h. Tổng hợp ba cặp: LR trên đủ đặc trưng và trên khái niệm chung (AUC-ROC), zero-shot (PR-AUC / tỷ lệ dương) và kết luận Cổng 0.'));
C.push(table([520, 700, 1500, 850, 850, 850, 1200, 2190, 700], ['Cặp', 'Chiều', 'Ngữ nghĩa nhãn', 'Đủ đặc trưng', 'KN chung, trong miền', 'KN chung, xuyên miền (tốt nhất)', 'Zero-shot PR-AUC / tỷ lệ dương', 'Chuyển giao tốt nhất ở k ≤ 50 (Δ, CI)', 'Kết luận'], PJ.synth, { size: 14 }));
C.push(P('**Friedman – Nemenyi (O3).** ' + PJ.friedman + ' Hạng trung bình của từng phương pháp ở Bảng A5.5i và Hình 10.'));
C.push(TCap('Bảng A5.5i. Hạng trung bình theo PR-AUC trên 41 khối (cặp × chiều × k); 1 = tốt nhất.'));
C.push(table([3600, 2400, 1600], ['Phương pháp', 'Nhóm', 'Hạng trung bình'], PJ.ranks, { size: 16 }));
C.push(image(ROOT + '/results/tong_hop_cap/cd_diagram.png', 5.6, 4.26));
C.push(Caption('Hình 10. Hạng trung bình ± CD/2 (Nemenyi, α = 0,05): hai phương pháp khác nhau có ý nghĩa khi hai đoạn không chồng nhau.'));
C.push(P('**Nhận xét.**', { extra: { keepNext: true } }));
C.push(...numbered(PJ.notes));

C.push(H(2, 'A6. Sản phẩm cho buổi đánh giá ngày 21/10/2026'));
C.push(table([5400, 2000, 1960], ['Sản phẩm', 'Phụ trách', 'Trạng thái'], [
  ['Mã KB1 cũ và KB1 v2, kèm file CSV kết quả thô', 'Minh', st('KB1 v2 và truy vết A5.1c đã có; mã cũ không còn')],
  ['Bản thảo LNCS hiện tại', 'Minh', st('Chưa tải lên')],
  ['File chia dữ liệu chung và notebook EDA của hai miền', 'Minh, Thiên', st('Đang làm')],
  ['00_contributions.md với RQ, giả thuyết, tiêu chí đã chốt', 'Cả nhóm', st('Một phần: Bảng 5')],
  ['Bảng 1–2 cập nhật và phiếu đọc ít nhất 10 bài', 'Thiên', st('Một phần: Bảng 1–2 đã cập nhật')],
  ['Báo cáo Cổng 0 (hai trang) với đường cong học và bảng baseline chuyển giao', 'Cả nhóm', st('Một phần: kết quả đầy đủ (gồm TabPFN v2) và kết luận PIVOT ở A5.4; chưa tách thành báo cáo hai trang')],
  ['Bảng ánh xạ khái niệm cho cặp miền thứ hai', 'Thiên', st('Một phần: bản nháp ở A2')],
  ['Bảng trạng thái cài đặt các baseline, kèm phiên bản mã', 'Minh', st('Chưa')],
], { size: 18 }));

C.push(H(2, 'A7. Câu hỏi của GVHD cần nhóm trả lời'));
C.push(...numbered([
  'Cấu hình Random Forest trong KB1 cũ (số cây, độ sâu, min_samples_leaf), cách mã hóa giới tính và giá trị thiếu, cách chuẩn hóa đặc trưng đào tạo (toàn miền hay chỉ phần train)? — *Mã cũ đã bị mất trước khi lưu lên Git nên không còn ghi nhận được cấu hình. Nhóm đã truy vết bằng 5 cách mã hóa (A5.1c): số trong-miền cũ tái lập được, còn 0,498 chỉ xuất hiện khi mã hóa không nhất quán giữa hai miền, nên bảng cũ được thay hoàn toàn bằng KB1 v2 (cấu hình đầy đủ trong config_kb1v2_99d14779.json). Từ nay mọi số liệu đều có mã và kết quả thô trên Git.*',
  'Hội nghị mục tiêu cụ thể và hạn nộp bài? — *Nhóm đề xuất trong buổi Cổng 0.*',
  'Nhóm có khả năng tiếp cận dữ liệu nhân sự thật (doanh nghiệp đối tác, đã ẩn danh) không? — *Nhóm trả lời; nếu có, dùng làm cặp miền thứ ba.*',
]));

// ============================================================ references
C.push(H(1, 'Tài liệu tham khảo'));
C.push(P('Số [1]–[22] giữ như đề cương; [23]–[30] bổ sung trong bản triển khai; [31]–[47] bổ sung theo đánh giá ngày 07/10/2026.'));
for (const [title, items] of REFS) {
  C.push(H(3, title));
  for (const it of items) C.push(new Paragraph({ children: L.runs(it, { size: 20 }), spacing: { after: 60 }, indent: { left: 500, hanging: 500 }, alignment: AlignmentType.LEFT }));
}

// ============================================================ document
const FONT = L.FONT;
const doc = new Document({
  creator: 'Tăng Nhật Minh, Phạm Xuân Thiên', title: 'B. Mô tả nghiên cứu (bản sửa 21/10/2026)',
  styles: {
    default: { document: { run: { font: FONT, size: 24 } } },
    paragraphStyles: [
      { id: 'Heading1', name: 'Heading 1', basedOn: 'Normal', next: 'Normal', quickFormat: true, run: { font: FONT, size: 30, bold: true, color: '000000' }, paragraph: { spacing: { before: 320, after: 140 }, keepNext: true, outlineLevel: 0 } },
      { id: 'Heading2', name: 'Heading 2', basedOn: 'Normal', next: 'Normal', quickFormat: true, run: { font: FONT, size: 27, bold: true, color: '000000' }, paragraph: { spacing: { before: 240, after: 110 }, keepNext: true, outlineLevel: 1 } },
      { id: 'Heading3', name: 'Heading 3', basedOn: 'Normal', next: 'Normal', quickFormat: true, run: { font: FONT, size: 24, bold: true, italics: true, color: '000000' }, paragraph: { spacing: { before: 180, after: 90 }, keepNext: true, outlineLevel: 2 } },
    ],
  },
  numbering: { config: L.numConfigs },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1134, right: 1134, bottom: 1134, left: 1134 } } },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ children: [PageNumber.CURRENT], size: 20 })] })] }) },
    children: C,
  }],
});
Packer.toBuffer(doc).then(b => { fs.writeFileSync(__dirname + '/base.docx', b); console.log('ok'); });
