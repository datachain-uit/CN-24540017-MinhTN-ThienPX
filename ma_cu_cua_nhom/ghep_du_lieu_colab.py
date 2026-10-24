import os
import glob
import pandas as pd
import numpy as np
from google.colab import drive
drive.mount('/content/drive')
base_search_path = '/content/drive/MyDrive/'
def find_file_path(filename):
    search_pattern = os.path.join(base_search_path, '**', filename)
    files = glob.glob(search_pattern, recursive=True)
    if files:
        return files[0]
    else:
        raise FileNotFoundError(f"Không tìm thấy tệp '{filename}'")

try:
    path_hr_analytics = find_file_path('HR_Analytics.csv')
    path_ibm_attrition = find_file_path('HR-Employee-Attrition.csv')
    path_aug_train = find_file_path('aug_train.csv')
except FileNotFoundError as e:
    print(f"LỖI")
    raise
df_hr = pd.read_csv(path_hr_analytics)
df_ibm = pd.read_csv(path_ibm_attrition)
df_aug = pd.read_csv(path_aug_train)
final_columns = [
    'Attrition', 'Age', 'Gender', 'Education_Level',
    'Department', 'Job_Role', 'Monthly_Income',
    'OverTime', 'Project_Count', 'Performance_Score',
    'Years_At_Company', 'Job_Satisfaction'
]

# Xử lý tập 1: HR_Analytics
df_hr['target_clean'] = df_hr['Attrition'].map({'Yes': 1, 'No': 0})
schema_hr = df_hr[['target_clean', 'Age', 'Gender', 'Department', 'JobRole', 'MonthlyIncome', 'OverTime', 'YearsAtCompany', 'JobSatisfaction']].copy()
schema_hr.columns = ['Attrition', 'Age', 'Gender', 'Department', 'Job_Role', 'Monthly_Income', 'OverTime', 'Years_At_Company', 'Job_Satisfaction']
schema_hr['Education_Level'] = np.nan
schema_hr['Project_Count'] = np.nan
schema_hr['Performance_Score'] = np.nan
schema_hr = schema_hr[final_columns]

# Xử lý tập 2: HR-Employee-Attrition (IBM)
df_ibm['target_clean'] = df_ibm['Attrition'].map({'Yes': 1, 'No': 0})
schema_ibm = df_ibm[['target_clean', 'Age', 'Gender', 'Department', 'JobRole', 'MonthlyIncome', 'OverTime', 'YearsAtCompany', 'JobSatisfaction', 'PerformanceRating']].copy()
schema_ibm.columns = ['Attrition', 'Age', 'Gender', 'Department', 'Job_Role', 'Monthly_Income', 'OverTime', 'Years_At_Company', 'Job_Satisfaction', 'Performance_Score']
schema_ibm['Education_Level'] = np.nan
schema_ibm['Project_Count'] = np.nan
schema_ibm = schema_ibm[final_columns]

# 3.3 Xử lý tập 3: aug_train
schema_aug = df_aug[['target', 'gender', 'education_level']].copy()
schema_aug.columns = ['Attrition', 'Gender', 'Education_Level']
for col in ['Age', 'Department', 'Job_Role', 'Monthly_Income', 'OverTime', 'Project_Count', 'Performance_Score', 'Years_At_Company', 'Job_Satisfaction']:
    schema_aug[col] = np.nan
schema_aug = schema_aug[final_columns]
print("Đang hợp nhất các tập dữ liệu...")
master_dataset = pd.concat([schema_hr, schema_ibm, schema_aug], ignore_index=True)

# ==============================================================================
# STEP 5: Xử lý Ma trận Dữ liệu Rỗng (Data Imputation)
# Điền các ô trống dữ liệu bị khuyết thiếu để chuẩn bị cấu trúc cho mô hình AI
# ==============================================================================
print("Đang xử lý ma trận dữ liệu rỗng (Khuyết thiếu dữ liệu)...")

# Các cột dữ liệu dạng số -> Thay bằng giá trị trung vị (Median)
num_cols = ['Age', 'Monthly_Income', 'Project_Count', 'Performance_Score', 'Years_At_Company', 'Job_Satisfaction']
for col in num_cols:
    master_dataset[col] = master_dataset[col].fillna(master_dataset[col].median())

# Các cột dữ liệu dạng chữ/phân loại -> Thay bằng giá trị xuất hiện nhiều nhất (Mode) hoặc đặt 'Unknown'
cat_cols = ['Gender', 'Education_Level', 'Department', 'Job_Role', 'OverTime']
for col in cat_cols:
    most_frequent_value = master_dataset[col].mode()[0] if not master_dataset[col].mode().empty else 'Unknown'
    master_dataset[col] = master_dataset[col].fillna(most_frequent_value)

# Khớp định dạng nhãn Attrition (Mục tiêu) sang kiểu số nguyên
master_dataset['Attrition'] = master_dataset['Attrition'].fillna(0).astype(int)

# ==============================================================================
# STEP 6: Lưu tệp Siêu Dữ Liệu sạch trở lại Google Drive
# ==============================================================================
output_directory = os.path.dirname(path_hr_analytics)  # Lưu cùng thư mục với file dữ liệu gốc tìm thấy
output_file_path = os.path.join(output_directory, 'Master_Unified_Dataset.csv')

master_dataset.to_csv(output_file_path, index=False)
print("\n==============================================================================")
print(f"XỬ LÝ THÀNH CÔNG!")
print(f"-> Tập dữ liệu tổng hợp đã được lưu tại Drive: {output_file_path}")
print(f"-> Tổng số lượng bản ghi nhân sự thu thập được: {len(master_dataset)} ca mẫu.")
print("==============================================================================")