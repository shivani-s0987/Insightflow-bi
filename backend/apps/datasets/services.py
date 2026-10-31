import csv, io, math
from pathlib import Path
import numpy as np
import pandas as pd
from django.conf import settings
from rest_framework.exceptions import ValidationError
ALLOWED_EXT={'.csv','.xlsx'}
def read_dataset(dataset, sheet_name=None):
    path=dataset.source_file.path
    try:
        if dataset.file_format=='csv':
            with open(path,'rb') as f: sample=f.read(65536)
            try: sample.decode('utf-8-sig'); encoding='utf-8-sig'
            except UnicodeDecodeError: encoding='cp1252'
            try: dialect=csv.Sniffer().sniff(sample.decode(encoding,errors='replace'), delimiters=',;\t|'); sep=dialect.delimiter
            except csv.Error: sep=','
            df=pd.read_csv(path,encoding=encoding,sep=sep,nrows=500000,low_memory=False)
        else:
            df=pd.read_excel(path,sheet_name=sheet_name or 0,nrows=500000,engine='openpyxl' if dataset.file_format=='xlsx' else None)
    except Exception as exc:
        raise ValidationError({'code':'dataset_read_error','detail':'The dataset could not be parsed. Check its encoding, delimiter, worksheet, and file integrity.'}) from exc
    if not isinstance(df,pd.DataFrame): raise ValidationError({'detail':'Select one worksheet to analyze.'})
    if len(df.columns)>250: raise ValidationError({'detail':'This dataset exceeds the 250-column limit.'})
    df.columns=[str(c).strip() or f'column_{i+1}' for i,c in enumerate(df.columns)]
    if len(set(df.columns))!=len(df.columns):
        seen={}; cols=[]
        for c in df.columns: seen[c]=seen.get(c,0)+1; cols.append(c if seen[c]==1 else f'{c}_{seen[c]}')
        df.columns=cols
    return df

def json_safe(value):
    if value is None or pd.isna(value): return None
    if isinstance(value,(np.integer,)): return int(value)
    if isinstance(value,(np.floating,float)): return float(value) if math.isfinite(float(value)) else None
    if isinstance(value,(np.bool_,)): return bool(value)
    if hasattr(value,'isoformat'): return value.isoformat()
    return str(value)

def apply_pipeline(df, pipeline):
    out=df.copy()
    if not isinstance(pipeline,list) or len(pipeline)>100: raise ValidationError({'detail':'Invalid transformation pipeline.'})
    for step in pipeline:
        if not isinstance(step,dict): raise ValidationError({'detail':'Each transformation step must be an object.'})
        op=step.get('op'); col=step.get('column')
        if op=='drop_duplicates': out=out.drop_duplicates()
        elif op=='drop_missing_rows':
            cols=step.get('columns') or ([col] if col else list(out.columns)); cols=[cols] if isinstance(cols,str) else cols; validate_columns(out,cols); out=out.dropna(subset=cols)
        elif op=='fill_missing':
            validate_columns(out,[col]); method=step.get('method','constant'); value=step.get('value','')
            if method in ('mean','median') and not pd.api.types.is_numeric_dtype(out[col]): raise ValidationError({'detail':f'{method.title()} filling requires a numeric column.'})
            elif method=='mean': value=out[col].mean()
            elif method=='median': value=out[col].median()
            elif method=='mode':
                modes=out[col].mode(dropna=True); value=modes.iloc[0] if not modes.empty else value
            elif method not in ('constant','mean','median','mode'): raise ValidationError({'detail':'Unsupported missing-value method.'})
            out[col]=out[col].fillna(value)
        elif op=='rename':
            validate_columns(out,[col]); new=str(step.get('new_name','')).strip()
            if not new or len(new)>128 or new in out.columns: raise ValidationError({'detail':'New column name must be unique and between 1 and 128 characters.'})
            out=out.rename(columns={col:new})
        elif op=='drop_column': validate_columns(out,[col]); out=out.drop(columns=[col])
        elif op=='trim_strings':
            validate_columns(out,[col]); out[col]=out[col].map(lambda x:x.strip() if isinstance(x,str) else x)
        elif op=='convert_type':
            validate_columns(out,[col]); typ=step.get('type')
            try:
                if typ=='number': out[col]=pd.to_numeric(out[col],errors='raise')
                elif typ=='string': out[col]=out[col].astype('string')
                elif typ=='date': out[col]=pd.to_datetime(out[col],errors='raise')
                elif typ=='boolean':
                    mapping={'true':True,'false':False,'1':True,'0':False,'yes':True,'no':False}
                    converted=out[col].map(lambda x: mapping.get(str(x).strip().lower()) if pd.notna(x) else None)
                    if (out[col].notna() & converted.isna()).any(): raise ValueError()
                    out[col]=converted.astype('boolean')
                else: raise ValidationError({'detail':'Unsupported target type.'})
            except (ValueError,TypeError) as exc: raise ValidationError({'detail':f'Column {col} contains values that cannot be converted to {typ}.'}) from exc
        elif op=='filter_numeric':
            validate_columns(out,[col]);
            if not pd.api.types.is_numeric_dtype(out[col]): raise ValidationError({'detail':'Numeric filters require a numeric column.'})
            try: value=float(step.get('value'))
            except (ValueError,TypeError) as exc: raise ValidationError({'detail':'Filter value must be numeric.'}) from exc
            cmp=step.get('comparison'); funcs={'gt':lambda s:s>value,'gte':lambda s:s>=value,'lt':lambda s:s<value,'lte':lambda s:s<=value,'eq':lambda s:s==value,'ne':lambda s:s!=value}
            if cmp not in funcs: raise ValidationError({'detail':'Unsupported comparison.'})
            out=out[funcs[cmp](out[col])]
        else: raise ValidationError({'detail':f'Unsupported transformation operation: {op}'})
    return out

def validate_columns(df, cols):
    if not isinstance(cols,list): cols=[cols]
    if any(not isinstance(c,str) for c in cols): raise ValidationError({'detail':'Column names must be strings.'})
    missing=[c for c in cols if c not in df.columns]
    if missing: raise ValidationError({'detail':f'Unknown column(s): {", ".join(map(str,missing))}.'})
