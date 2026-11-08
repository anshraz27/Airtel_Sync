import pandas as pd
import os

base = r'c:\Users\thean\Desktop\airtel_digital\YTL_TrackA_Udyam_Digital_Data'

# smb_leads analysis
df = pd.read_csv(os.path.join(base, 'smb_leads.csv'))
print('=== SMB LEADS ===')
print(f'Shape: {df.shape}')
print(f'\nMissing values (top 15):')
missing = df.isnull().sum()
print(missing[missing > 0].sort_values(ascending=False).head(15))
print(f'\nStage distribution:')
print(df['stage_reached'].value_counts())
print(f'\nOutcome distribution:')
print(df['outcome'].value_counts())
print(f'\nDrop reasons:')
print(df['drop_reason'].value_counts())
print(f'\nSegment distribution:')
print(df['segment'].value_counts())
print(f'\nLead source:')
print(df['lead_source'].value_counts())
print(f'\nhas_gstin:')
print(df['has_gstin'].value_counts())
print(f'\nhas_udyam:')
print(df['has_udyam'].value_counts())
print(f'\nCity tier:')
print(df['city_tier'].value_counts())
print(f'\nPreferred language:')
print(df['preferred_language'].value_counts())
print(f'\nTurnover band:')
print(df['annual_turnover_band'].value_counts())

# GSTIN registry
gst = pd.read_csv(os.path.join(base, 'mock_gstin_registry.csv'))
print(f'\n=== GSTIN REGISTRY ===')
print(f'Shape: {gst.shape}')
print(f'Columns: {list(gst.columns)}')
print(f'Status distribution:')
print(gst['status'].value_counts())
print(f'Missing values:')
print(gst.isnull().sum())
print(f'Constitution:')
print(gst['constitution'].value_counts())

# Udyam registry
udy = pd.read_csv(os.path.join(base, 'mock_udyam_registry.csv'))
print(f'\n=== UDYAM REGISTRY ===')
print(f'Shape: {udy.shape}')
print(f'Columns: {list(udy.columns)}')
print(f'Enterprise type:')
print(udy['enterprise_type'].value_counts())
print(f'Major activity:')
print(udy['major_activity'].value_counts())
print(f'Missing values:')
print(udy.isnull().sum())

# Product catalogue
prod = pd.read_csv(os.path.join(base, 'product_catalogue.csv'))
print(f'\n=== PRODUCT CATALOGUE ===')
print(f'Shape: {prod.shape}')
print(f'Categories:')
print(prod['category'].value_counts())
print(f'Requires GSTIN:')
print(prod['requires_gstin'].value_counts())

# Join key analysis
leads_gstins = set(df[df['has_gstin']=='Y']['gstin'].dropna())
registry_gstins = set(gst['gstin'])
print(f'\n=== JOIN ANALYSIS ===')
print(f'Leads with GSTIN: {len(leads_gstins)}')
print(f'Registry GSTINs: {len(registry_gstins)}')
print(f'Matching: {len(leads_gstins & registry_gstins)}')

leads_udyam = set(df[df['has_udyam']=='Y']['udyam_number'].dropna())
registry_udyam = set(udy['udyam_number'])
print(f'Leads with Udyam: {len(leads_udyam)}')
print(f'Registry Udyam: {len(registry_udyam)}')
print(f'Matching: {len(leads_udyam & registry_udyam)}')

# Activated leads stats
act = df[df['outcome']=='Activated']
print(f'\n=== ACTIVATED LEADS ===')
print(f'Count: {len(act)}')
print(f'Avg days to activation: {act["days_lead_to_activation"].mean():.1f}')
print(f'Avg follow-up calls: {act["customer_follow_up_calls"].mean():.1f}')
print(f'Avg monthly bundle value: {act["monthly_bundle_value_inr"].mean():.0f}')
print(f'Avg acquisition cost: {act["acquisition_cost_inr"].mean():.0f}')
print(f'Churn rate: {(act["churned_within_6_months"]=="Y").mean():.2%}')
print(f'Avg NPS: {act["nps_score"].mean():.1f}')
print(f'Median bundle value: {act["monthly_bundle_value_inr"].median():.0f}')

# Activation rate by GSTIN
gstin_leads = df[df['has_gstin']=='Y']
no_gstin_leads = df[df['has_gstin']=='N']
print(f'\n=== ACTIVATION BY GSTIN ===')
print(f'With GSTIN: {(gstin_leads["outcome"]=="Activated").mean():.2%} ({len(gstin_leads)} leads)')
print(f'Without GSTIN: {(no_gstin_leads["outcome"]=="Activated").mean():.2%} ({len(no_gstin_leads)} leads)')

# Segment activation rates
print(f'\n=== ACTIVATION BY SEGMENT ===')
for seg in df['segment'].unique():
    seg_df = df[df['segment']==seg]
    act_rate = (seg_df['outcome']=='Activated').mean()
    print(f'{seg}: {act_rate:.2%} ({len(seg_df)} leads)')

# Products of interest frequency
from collections import Counter
all_prods = []
for p in df['products_of_interest'].dropna():
    all_prods.extend(p.split(';'))
print(f'\n=== TOP PRODUCTS OF INTEREST ===')
for prod_id, count in Counter(all_prods).most_common():
    print(f'{prod_id}: {count}')

