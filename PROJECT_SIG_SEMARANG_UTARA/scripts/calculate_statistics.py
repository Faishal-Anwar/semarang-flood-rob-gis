#!/usr/bin/env python3
"""Kompatibilitas: hitung ulang statistik dari geometri.

Script ini sebelumnya memuat angka hardcoded yang tidak konsisten dengan layer.
Semua perhitungan kini didelegasikan ke `recompute_analysis.py` agar hanya ada
satu sumber kebenaran.

Jalankan dari root proyek:
    python scripts/calculate_statistics.py
"""
from recompute_analysis import main

if __name__ == "__main__":
    main()
