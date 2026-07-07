
import pandas as pd

# 读取 person.csv
df = pd.read_csv("csv/person.csv")

# 假设身高单位为英寸（该脚本已转换），体重单位为磅
# BMI = kg / m^2
# kg = lbs * 0.45359237
# m = inches * 0.0254

height_col = "height"
weight_col = "weight"

df = df.copy()

df[height_col] = pd.to_numeric(df[height_col], errors="coerce")
df[weight_col] = pd.to_numeric(df[weight_col], errors="coerce")

height_m = df[height_col] * 0.0254
weight_kg = df[weight_col] * 0.45359237

df["bmi"] = weight_kg / (height_m ** 2)

bmi_df = df[["id", "bmi"]]
bmi_df.to_csv("csv/bmi.csv", index=False)

print("BMI文件已生成: csv/bmi.csv")
