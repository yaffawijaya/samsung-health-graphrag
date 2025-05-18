import pandas as pd
import zipfile
import io

# Utility to load CSV in-memory from ZIP by pattern
def load_csv_from_zip(zip_file, pattern):
    for name in zip_file.namelist():
        if pattern in name and name.endswith('.csv'):
            with zip_file.open(name) as f:
                return pd.read_csv(io.TextIOWrapper(f), skiprows=1, index_col=False).dropna(axis=1, how='all')
    return None

# Cleaning functions
def clean_food_intake(df):
    df = df.dropna(axis=1, how='all').copy()
    create_cols = [c for c in df.columns if 'create_time' in c]
    if not create_cols:
        raise ValueError(f"No create_time column. Columns: {list(df.columns)}")
    create_col = create_cols[0]
    name_cols = [c for c in df.columns if 'name' in c.lower() and 'pkg' not in c.lower()]
    if not name_cols:
        raise ValueError(f"No name column. Columns: {list(df.columns)}")
    name_col = name_cols[0]
    amt_cols = [c for c in df.columns if 'amount' in c.lower() and 'unit_amount' not in c.lower()]
    if amt_cols:
        amt_col = amt_cols[0]
    elif 'custom' in df.columns:
        amt_col = 'custom'
    else:
        raise ValueError(f"No amount column. Columns: {list(df.columns)}")
    cal_cols = [c for c in df.columns if 'calorie' in c.lower()]
    if not cal_cols:
        raise ValueError(f"No calorie column. Columns: {list(df.columns)}")
    cal_col = cal_cols[0]
    summary = (
        df[[create_col, name_col, amt_col, cal_col]]
          .rename(columns={create_col:'date', name_col:'food_name', amt_col:'amount', cal_col:'calories'})
          .assign(date=lambda d: pd.to_datetime(d['date'], errors='coerce').dt.date)
          .dropna(subset=['date'])
    )
    return summary


def clean_food_details(df):
    df = df.dropna(axis=1, how='all').copy()
    df['start_time'] = pd.to_datetime(df['start_time'], errors='coerce')
    df['create_time'] = pd.to_datetime(df['create_time'], errors='coerce')
    df['date'] = df['start_time'].dt.date
    return df


def clean_sleep_hours(df):
    df = df.dropna(axis=1, how='all')
    start_cols = [c for c in df.columns if 'start_time' in c]
    end_cols = [c for c in df.columns if 'end_time' in c]
    if not start_cols or not end_cols:
        raise ValueError(f"Sleep time columns missing. Columns: {list(df.columns)}")
    df = df[[start_cols[0], end_cols[0]]].copy()
    df.columns = ['start_time','end_time']
    df['start_time'] = pd.to_datetime(df['start_time'], errors='coerce')
    df['end_time'] = pd.to_datetime(df['end_time'], errors='coerce')
    df = df.dropna(subset=['start_time','end_time'])
    df['sleep_duration_h'] = df.apply(lambda r: (r['end_time']-r['start_time']).total_seconds()/3600, axis=1)
    df = df[(df['sleep_duration_h']>=0)&(df['sleep_duration_h']<=16)]
    df['date'] = df['start_time'].dt.date
    return df.groupby('date', as_index=False)['sleep_duration_h'].sum().rename(columns={'sleep_duration_h':'total_sleep_h'})


def clean_step_count(df):
    df = df.dropna(axis=1, how='all')[['count','day_time']].copy()
    df['day_time'] = pd.to_datetime(df['day_time'], unit='ms', errors='coerce')
    df = df.dropna(subset=['day_time'])
    df = df[df['count']>=0]
    df['date'] = df['day_time'].dt.date
    return df.groupby('date', as_index=False)['count'].sum().rename(columns={'count':'total_steps'})


def clean_water_intake(df):
    df = df.dropna(axis=1, how='all')[['start_time','amount']].copy()
    df['start_time'] = pd.to_datetime(df['start_time'], errors='coerce')
    df = df.dropna(subset=['start_time'])
    df = df[df['amount']>=0] 
    df['date'] = df['start_time'].dt.date
    return df.groupby('date', as_index=False)['amount'].sum().rename(columns={'amount':'total_water_ml'})