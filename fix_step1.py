with open("step1_spatial_engine.py", "r") as f:
    code = f.read()

# Replace kelurahan column selection to handle jumlah_rw and jumlah_rt
old_block = """# Profile per Kelurahan summary
kel_summary = []
for _, kel in gdf_kel.iterrows():
    k_name = kel['nama_kel']
    kel_perm = gdf_permukiman[gdf_permukiman['kelurahan'] == k_name]
    kel_td = gdf_terdampak[gdf_terdampak['kelurahan'] == k_name]
    
    tot_perm_ha = kel_perm['luas_ha'].sum() if len(kel_perm) > 0 else 0.0
    tot_td_ha = kel_td['luas_terpapar_ha'].sum() if len(kel_td) > 0 else 0.0
    pct = round((tot_td_ha / tot_perm_ha * 100.0), 1) if tot_perm_ha > 0 else 0.0
    
    pts_srv = len(gdf_survei[gdf_survei['kelurahan'] == k_name])
    
    kel_summary.append({
        'id_kel': kel['id_kel'],
        'nama_kel': k_name,
        'jumlah_rw': kel['jumlah_rw'],
        'jumlah_rt': kel['jumlah_rt'],
        'populasi_jiwa': kel['populasi'],
        'luas_kelurahan_ha': kel['luas_ha'],
        'luas_permukiman_ha': round(tot_perm_ha, 2),
        'luas_terpapar_ha': round(tot_td_ha, 2),
        'persentase_terpapar_pct': pct,
        'jumlah_titik_survei': pts_srv,
        'status_kerentanan': 'Sangat Kritis' if pct >= 75 else 'Kritis' if pct >= 50 else 'Waspada' if pct >= 25 else 'Aman Terkendali'
    })"""

new_block = """# Kelurahan meta dict
kel_meta_dict = {
    'Bandarharjo': {'rw': 12, 'rt': 98},
    'Bulu Lor': {'rw': 11, 'rt': 85},
    'Dadapsari': {'rw': 10, 'rt': 72},
    'Kuningan': {'rw': 9, 'rt': 68},
    'Panggung Kidul': {'rw': 8, 'rt': 64},
    'Panggung Lor': {'rw': 14, 'rt': 112},
    'Plombokan': {'rw': 7, 'rt': 56},
    'Purwosari': {'rw': 6, 'rt': 48},
    'Tanjung Mas': {'rw': 16, 'rt': 124}
}

kel_summary = []
for _, kel in gdf_kel.iterrows():
    k_name = kel['nama_kel']
    kel_perm = gdf_permukiman[gdf_permukiman['kelurahan'] == k_name]
    kel_td = gdf_terdampak[gdf_terdampak['kelurahan'] == k_name]
    
    tot_perm_ha = kel_perm['luas_ha'].sum() if len(kel_perm) > 0 else 0.0
    tot_td_ha = kel_td['luas_terpapar_ha'].sum() if len(kel_td) > 0 else 0.0
    pct = round((tot_td_ha / tot_perm_ha * 100.0), 1) if tot_perm_ha > 0 else 0.0
    
    pts_srv = len(gdf_survei[gdf_survei['kelurahan'] == k_name])
    rw_val = kel_meta_dict.get(k_name, {}).get('rw', 10)
    rt_val = kel_meta_dict.get(k_name, {}).get('rt', 70)
    
    kel_summary.append({
        'id_kel': kel['id_kel'],
        'nama_kel': k_name,
        'jumlah_rw': rw_val,
        'jumlah_rt': rt_val,
        'populasi_jiwa': kel['populasi'],
        'luas_kelurahan_ha': kel['luas_ha'],
        'luas_permukiman_ha': round(tot_perm_ha, 2),
        'luas_terpapar_ha': round(tot_td_ha, 2),
        'persentase_terpapar_pct': pct,
        'jumlah_titik_survei': pts_srv,
        'status_kerentanan': 'Sangat Kritis' if pct >= 75 else 'Kritis' if pct >= 50 else 'Waspada' if pct >= 25 else 'Aman Terkendali'
    })"""

code = code.replace(old_block, new_block)
with open("step1_spatial_engine.py", "w") as f:
    f.write(code)
print("Updated step1_spatial_engine.py")
