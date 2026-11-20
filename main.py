import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

loans_raw = pd.read_csv("data/raw/loans__rates_rub.csv", header=None)
deposit_rates_raw = pd.read_csv("data/raw/deposits__rates_rub.csv", header=None)
deposit_structure_raw = pd.read_csv("data/raw/deposits__structure_rub.csv", header=None)
key_inflation_raw = pd.read_csv("data/raw/key_inflation_full__inflation_key_rate.csv", header=None)

# print("Кредитные данные:")
# print(loans_raw.head(8))
# print("*" * 70)
#
# print("Данные по ставкам вкладов:")
# print(deposit_rates_raw.head(8))
# print("*" * 70)
#
# print("Данные по структуре вкладов:")
# print(deposit_structure_raw.head(8))
# print("*" * 70)
#
# print("Данные по ключевой ставке и инфляции:")
# print(key_inflation_raw.head(8))
# print("*" * 70)


# ==========================================================================================
# ==========================================================================================

months = {
    "Январь": "01",
    "Февраль": "02",
    "Март": "03",
    "Апрель": "04",
    "Май": "05",
    "Июнь": "06",
    "Июль": "07",
    "Август": "08",
    "Сентябрь": "09",
    "Октябрь": "10",
    "Ноябрь": "11",
    "Декабрь": "12"
}


def month_to_date(value):
    parts = str(value).strip().split()
    month_number = months[parts[0]]
    year = parts[1]
    return year + "-" + month_number


def number_to_month(value):
    parts = str(value).strip().split(".")
    month_number = parts[0].zfill(2)
    year = parts[1]
    return year + "-" + month_number


# ==========================================================================================
# ==========================================================================================

credit_rates = loans_raw.iloc[5:158, [0, 9]].copy()
credit_rates.columns = ["Month_RU", "Credit_Rate"]

credit_rates["Month"] = [month_to_date(value) for value in credit_rates["Month_RU"]]
credit_rates["Credit_Rate"] = pd.to_numeric(
    credit_rates["Credit_Rate"],
    errors="coerce"
)

credit_rates = credit_rates[["Month", "Credit_Rate"]]
credit_rates = credit_rates.drop_duplicates()
credit_rates = credit_rates[credit_rates["Month"] >= "2015-01"]
credit_rates = credit_rates.sort_values("Month")
credit_rates = credit_rates.reset_index(drop=True)

print("Ставки по кредитам после обработки:")
print(credit_rates.head())
print(credit_rates.tail())
print("*" * 70)

credit_rates.to_csv(
    "data/processed/credit_rates.csv",
    index=False
)


# ==========================================================================================
# ==========================================================================================


deposit_columns = [1, 3, 4, 5, 6, 9, 10]

deposit_names = [
    "Demand",
    "Up_to_30_days",
    "31_90_days",
    "91_180_days",
    "181_days_1_year",
    "1_3_years",
    "Over_3_years"
]

deposit_rates = pd.DataFrame({
    "Month_RU": deposit_rates_raw.iloc[5:158, 0].values
})

deposit_weights = pd.DataFrame({
    "Month_RU": deposit_structure_raw.iloc[5:158, 0].values
})

for i in range(len(deposit_columns)):
    column_number = deposit_columns[i]
    column_name = deposit_names[i]

    deposit_rates[column_name] = pd.to_numeric(
        deposit_rates_raw.iloc[5:158, column_number],
        errors="coerce"
    ).values

    deposit_weights[column_name] = pd.to_numeric(
        deposit_structure_raw.iloc[5:158, column_number],
        errors="coerce"
    ).values

deposit_rates["Month"] = [month_to_date(value) for value in deposit_rates["Month_RU"]]
deposit_weights["Month"] = [month_to_date(value) for value in deposit_weights["Month_RU"]]

# Расчёт средневзвешенной ставки по вкладам.
# Вес каждого срока — его доля в общем объёме вкладов физических лиц.

weighted_deposit_rates = []

for i in range(len(deposit_rates)):
    total_value = 0
    total_weight = 0

    for column_name in deposit_names:
        current_rate = deposit_rates.loc[i, column_name]
        current_weight = deposit_weights.loc[i, column_name]

        if not np.isnan(current_rate) and not np.isnan(current_weight):
            total_value += current_rate * current_weight
            total_weight += current_weight

    if total_weight > 0:
        weighted_deposit_rates.append(total_value / total_weight)
    else:
        weighted_deposit_rates.append(np.nan)

deposit_rates["Deposit_Rate"] = weighted_deposit_rates

deposit_rates = deposit_rates[
    ["Month", "Deposit_Rate"] + deposit_names
]
deposit_rates = deposit_rates.drop_duplicates()
deposit_rates = deposit_rates[deposit_rates["Month"] >= "2015-01"]
deposit_rates = deposit_rates.sort_values("Month")
deposit_rates = deposit_rates.reset_index(drop=True)

deposit_weights = deposit_weights[
    ["Month"] + deposit_names
]
deposit_weights = deposit_weights[deposit_weights["Month"] >= "2015-01"]
deposit_weights = deposit_weights.sort_values("Month")
deposit_weights = deposit_weights.reset_index(drop=True)

print("Проверка суммы долей по выбранным срокам:")
print(deposit_weights[deposit_names].sum(axis=1).describe())
print("*" * 70)

print("Средневзвешенная ставка по вкладам:")
print(deposit_rates[["Month", "Deposit_Rate"]].head())
print(deposit_rates[["Month", "Deposit_Rate"]].tail())
print("*" * 70)

deposit_rates[["Month", "Deposit_Rate"]].to_csv(
    "data/processed/deposit_rates.csv",
    index=False
)

deposit_rates.to_csv(
    "data/processed/deposit_rates_by_maturity.csv",
    index=False
)

deposit_weights.to_csv(
    "data/processed/deposit_weights_by_maturity.csv",
    index=False
)


# ==========================================================================================
# ==========================================================================================


key_inflation = key_inflation_raw.iloc[1:, [0, 1, 2, 3]].copy()
key_inflation.columns = [
    "Month_RU",
    "Key_Rate",
    "Inflation",
    "Inflation_Target"
]

key_inflation["Month"] = [number_to_month(value) for value in key_inflation["Month_RU"]]

key_inflation["Key_Rate"] = pd.to_numeric(
    key_inflation["Key_Rate"],
    errors="coerce"
)

key_inflation["Inflation"] = pd.to_numeric(
    key_inflation["Inflation"],
    errors="coerce"
)

key_inflation["Inflation_Target"] = pd.to_numeric(
    key_inflation["Inflation_Target"],
    errors="coerce"
)

key_inflation = key_inflation[
    ["Month", "Key_Rate", "Inflation", "Inflation_Target"]
]
key_inflation = key_inflation.drop_duplicates()
key_inflation = key_inflation.sort_values("Month")
key_inflation = key_inflation.reset_index(drop=True)

print("Ключевая ставка и инфляция после обработки:")
print(key_inflation.head())
print(key_inflation.tail())
print("*" * 70)

key_inflation.to_csv(
    "data/processed/key_rate_inflation.csv",
    index=False
)



# ==========================================================================================
# ==========================================================================================


key_table = key_inflation.set_index("Month")
credit_table = credit_rates.set_index("Month")
deposit_table = deposit_rates[["Month", "Deposit_Rate"]].set_index("Month")

final_dataset = pd.concat(
    [
        key_table,
        credit_table,
        deposit_table
    ],
    axis=1
)

final_dataset = final_dataset.reset_index()
final_dataset = final_dataset.sort_values("Month")
final_dataset = final_dataset.drop_duplicates()


final_dataset = final_dataset.dropna(
    subset=["Key_Rate", "Inflation", "Credit_Rate", "Deposit_Rate"]
)

final_dataset = final_dataset.reset_index(drop=True)

print("Итоговая таблица:")
print(final_dataset.head())
print("*" * 70)

print("Количество наблюдений:", len(final_dataset))
print("Первый месяц:", final_dataset["Month"].min())
print("Последний месяц:", final_dataset["Month"].max())
print("Количество дубликатов:", final_dataset.duplicated().sum())
print("Количество пропусков в итоговой таблице:")
print(final_dataset.isna().sum())


final_dataset.to_csv(
    "data/processed/final_dataset.csv",
    index=False
)


# ==========================================================================================
# ==========================================================================================

# Разница между ставкой по кредитам и ставкой по вкладам.
final_dataset["Spread"] = (
    final_dataset["Credit_Rate"] - final_dataset["Deposit_Rate"]
)

# Отклонение инфляции от цели Банка России.
final_dataset["Inflation_Gap"] = (
    final_dataset["Inflation"] - final_dataset["Inflation_Target"]
)

# Год группировки данных.
final_dataset["Year"] = final_dataset["Month"].str[:4]

final_dataset.to_csv(
    "data/processed/final_dataset.csv",
    index=False
)

print("Итоговые данные сохранены.")
print("*" * 70)


# ==========================================================================================
# 8. ОПИСАТЕЛЬНАЯ СТАТИСТИКА
# ==========================================================================================

statistics = final_dataset[
    [
        "Key_Rate",
        "Inflation",
        "Credit_Rate",
        "Deposit_Rate",
        "Spread"
    ]
].agg(["mean", "median", "min", "max", "std"])

print("Описательная статистика:")
print(statistics)

statistics.to_csv(
    "results/descriptive_statistics.csv"
)


# ==========================================================================================
# ==========================================================================================

annual_summary = final_dataset.groupby("Year").agg({
    "Key_Rate": "mean",
    "Inflation": "mean",
    "Credit_Rate": "mean",
    "Deposit_Rate": "mean",
    "Spread": "mean"
})

print("Средние показатели по годам:")
print(annual_summary)

annual_summary.to_csv(
    "results/annual_summary.csv"
)


# ==========================================================================================
# ==========================================================================================

corr_matrix = final_dataset[
    [
        "Key_Rate",
        "Inflation",
        "Credit_Rate",
        "Deposit_Rate"
    ]
].corr(numeric_only=True)

print("Корреляционная матрица:")
print(corr_matrix)

corr_matrix.to_csv(
    "results/correlation_matrix.csv"
)




#=======================================================================================================================
#ГРАФИКИ================================================================================================================
#=======================================================================================================================


# ==========================================================================================
# Динамика ключевой ставки ЦБ
# ==========================================================================================

# plt.figure(figsize=(12, 6))
#
# plt.plot(
#     final_dataset["Month"],
#     final_dataset["Key_Rate"],
#     color="blue",
#     label="Ключевая ставка"
# )
#
# plt.title("Динамика ключевой ставки Банка России")
# plt.xlabel("Месяц")
# plt.ylabel("% годовых")
# plt.xticks(
#     range(0, len(final_dataset), 12),
#     final_dataset["Month"].iloc[::12],
#     rotation=45
# )
# plt.grid(alpha=0.3)
# plt.legend()
# plt.tight_layout()
# plt.savefig("figures/01_key_rate.png", dpi=300, bbox_inches="tight")
# plt.show()




# ==========================================================================================
# Динамика инфляции и цели банка РФ
# ==========================================================================================

# plt.figure(figsize=(12, 6))
#
# plt.plot(
#     final_dataset["Month"],
#     final_dataset["Inflation"],
#     color="red",
#     label="Инфляция, % годовых"
# )
#
# plt.plot(
#     final_dataset["Month"],
#     final_dataset["Inflation_Target"],
#     color="green",
#     linestyle="--",
#     label="Цель по инфляции"
# )
#
# plt.title("Динамика инфляции и цели Банка России")
# plt.xlabel("Месяц")
# plt.ylabel("%")
# plt.xticks(
#     range(0, len(final_dataset), 12),
#     final_dataset["Month"].iloc[::12],
#     rotation=45
# )
# plt.grid(alpha=0.3)
# plt.legend()
# plt.tight_layout()
# plt.savefig("figures/02_inflation.png", dpi=300, bbox_inches="tight")
# plt.show()




# ==========================================================================================
# Сравнение трёх процентных ставок в РФ
# ==========================================================================================

# plt.figure(figsize=(14, 7))
#
# plt.plot(
#     final_dataset["Month"],
#     final_dataset["Key_Rate"],
#     label="Ключевая ставка",
#     color="blue"
# )
#
# plt.plot(
#     final_dataset["Month"],
#     final_dataset["Credit_Rate"],
#     label="Ставка по кредитам",
#     color="red"
# )
#
# plt.plot(
#     final_dataset["Month"],
#     final_dataset["Deposit_Rate"],
#     label="Средневзвешенная ставка по вкладам",
#     color="green"
# )
#
# plt.title("Сравнение процентных ставок в России")
# plt.xlabel("Месяц")
# plt.ylabel("% годовых")
# plt.xticks(
#     range(0, len(final_dataset), 12),
#     final_dataset["Month"].iloc[::12],
#     rotation=45
# )
# plt.grid(alpha=0.3)
# plt.legend()
# plt.tight_layout()
# plt.savefig("figures/03_three_rates.png", dpi=300, bbox_inches="tight")
# plt.show()




# ==========================================================================================
# Разница между кредитными и депозитными ставками
# ==========================================================================================

# plt.figure(figsize=(12, 6))
#
# plt.plot(
#     final_dataset["Month"],
#     final_dataset["Spread"],
#     color="purple",
#     label="Разница ставок"
# )
#
# plt.plot(
#     final_dataset["Month"],
#     [0] * len(final_dataset),
#     color="black",
#     linestyle="--",
#     label="Нулевая линия"
# )
#
# plt.title("Разница между ставками по кредитам и вкладам")
# plt.xlabel("Месяц")
# plt.ylabel("Процентные пункты")
# plt.xticks(
#     range(0, len(final_dataset), 12),
#     final_dataset["Month"].iloc[::12],
#     rotation=45
# )
# plt.grid(alpha=0.3)
# plt.legend()
# plt.tight_layout()
# plt.savefig("figures/04_spread.png", dpi=300, bbox_inches="tight")
# plt.show()





# ==========================================================================================
# Диаграмма рассеивания
# ==========================================================================================

# plt.figure(figsize=(9, 6))
#
# plt.scatter(
#     final_dataset["Key_Rate"],
#     final_dataset["Credit_Rate"],
#     color="red",
#     alpha=0.6
# )
#
# plt.title("Связь ключевой ставки и ставки по кредитам")
# plt.xlabel("Ключевая ставка, %")
# plt.ylabel("Ставка по кредитам, %")
# plt.grid(alpha=0.3)
# plt.tight_layout()
# plt.savefig("figures/05_credit_scatter.png", dpi=300, bbox_inches="tight")
# plt.show()




# ==========================================================================================
# Корреляционная тепловая карта
# ==========================================================================================

# plt.figure(figsize=(9, 7))
#
# sns.heatmap(
#     corr_matrix,
#     annot=True,
#     cmap="coolwarm",
#     fmt=".2f"
# )
#
# plt.title("Корреляционная матрица процентных и инфляционных показателей")
# plt.tight_layout()
# plt.savefig("figures/06_correlation_heatmap.png", dpi=300, bbox_inches="tight")
# plt.show()




# ==========================================================================================
# Средние процентные ставки по годам
# ==========================================================================================

plt.figure(figsize=(13, 6))

years = annual_summary.index
x = np.arange(len(years))
width = 0.2

plt.bar(
    x - width * 1.5,
    annual_summary["Key_Rate"],
    width,
    label="Ключевая ставка"
)

plt.bar(
    x - width * 0.5,
    annual_summary["Credit_Rate"],
    width,
    label="Кредиты"
)

plt.bar(
    x + width * 0.5,
    annual_summary["Deposit_Rate"],
    width,
    label="Вклады"
)

plt.bar(
    x + width * 1.5,
    annual_summary["Inflation"],
    width,
    label="Инфляция"
)

plt.title("Средние показатели по годам")
plt.xlabel("Год")
plt.ylabel("%")
plt.xticks(x, years, rotation=45)
plt.grid(axis="y", alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig("figures/07_annual_comparison.png", dpi=300, bbox_inches="tight")
plt.show()
