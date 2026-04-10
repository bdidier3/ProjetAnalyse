import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

sns.set_theme(style="whitegrid")
base = Path('.')
figdir = base / 'figures'
figdir.mkdir(exist_ok=True)

stat_df = pd.read_csv(base / 'stat.csv')
ranked = stat_df.sort_values('Var', ascending=False)['Tags'].tolist()
preferred = [
    'ST110_VARExtr_1_druck_1_IstP',
    'ST110_VARExtr_2_druck_1_IstP',
    'ST110_VARExtr_3_druck_1_IstP',
    'ST110_VAREx_1_GesamtDS',
    'ST110_VAREx_2_GesamtDS',
    'ST110_VAREx_3_GesamtDS',
    'ST110_VAREx_1_SDickeIst',
    'ST110_VAREx_2_SDickeIst',
    'ST110_VAREx_3_SDickeIst',
    'ST110_VAREx_1_Foerderrate',
    'ST110_VAREx_2_Foerderrate',
    'ST110_VAREx_3_Foerderrate',
    'ST0_VARActAuftrag'
]
selected = []
for c in preferred + ranked:
    if c not in selected:
        selected.append(c)
    if len(selected) >= 14:
        break
usecols = ['Datum'] + selected

df = pd.read_csv(base / 'extrusion.csv', usecols=usecols, parse_dates=['Datum'], dayfirst=True, low_memory=False)
num_cols = [c for c in df.columns if c != 'Datum']
for c in num_cols:
    df[c] = pd.to_numeric(df[c], errors='coerce')
for c in num_cols:
    if df[c].isna().any():
        df[c] = df[c].fillna(df[c].median())

df = df.sort_values('Datum').reset_index(drop=True)
pressure_col = next((c for c in num_cols if 'druck_1_IstP' in c), num_cols[0])
flow_col = next((c for c in num_cols if 'GesamtDS' in c), num_cols[1])
thickness_col = next((c for c in num_cols if 'SDickeIst' in c), num_cols[2])
df['pressure_roll_mean_30'] = df[pressure_col].rolling(window=30, min_periods=1).mean()

plt.figure(figsize=(10, 4.8))
plt.plot(df['Datum'], df[pressure_col], linewidth=0.6, alpha=0.6, label='Pression brute')
plt.plot(df['Datum'], df['pressure_roll_mean_30'], linewidth=1.8, label='Moyenne mobile (30)')
plt.title('Tendance temporelle de la pression')
plt.xlabel('Temps')
plt.ylabel('Pression')
plt.legend()
plt.tight_layout()
plt.savefig(figdir / 'line_pressure.png', dpi=180)
plt.close()

corr_candidates = [pressure_col, flow_col, thickness_col] + [c for c in num_cols if c not in [pressure_col, flow_col, thickness_col]][:5]
corr_matrix = df[corr_candidates].corr(numeric_only=True)
plt.figure(figsize=(7.2, 5.5))
sns.heatmap(corr_matrix, cmap='coolwarm', center=0)
plt.title('Matrice de corrélation')
plt.tight_layout()
plt.savefig(figdir / 'heatmap_corr.png', dpi=180)
plt.close()

plt.figure(figsize=(7.5, 3.8))
sns.boxplot(x=df[pressure_col], color='#E76F51')
plt.title('Boxplot de la pression')
plt.xlabel('Pression')
plt.tight_layout()
plt.savefig(figdir / 'boxplot_pressure.png', dpi=180)
plt.close()

print('Figures générées dans figures/: line_pressure.png, heatmap_corr.png, boxplot_pressure.png')
