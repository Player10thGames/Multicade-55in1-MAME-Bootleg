#!/usr/bin/env python3
"""
Multicade 55-in-1 MAME Bootleg ROM Archive Builder
===================================================
Builds multcade.zip from individual game ROM ZIP files for MAME4Droid 0.139u1.

ROM Parent: multcade
ROM Clone of: 39in1 (39in1.zip)
Hardware: Bootleg MAME-based arcade PCB (Intel Xscale PXA255 @ 200 MHz)

This script:
1. Reads all individual game ROM ZIP files (sorted by game number for deterministic ordering)
2. Extracts ROM files and preserves timestamps
3. Resolves duplicate filenames by preferring the LATER game's version
4. Assembles them into multcade.zip with proper Store compression
5. Verifies CRC32 checksums against the original multcade.zip (if available)
6. Generates a detailed manifest of all included ROMs

Duplicate Filename Resolution:
    Some ROM filenames appear in multiple games (e.g., "5e", "u5", "u6", "u7").
    The original multcade.zip prefers the version from the LATER game in the
    game list order. For example:
    - "5e" appears in mspacman (game #1) and scobra (game #26) -> scobra version wins
    - "u5", "u6", "u7" appear in mspacman (#1) and qix (#32) -> qix version wins
"""

import zipfile
import os
import sys
import json
import struct
import time
from datetime import datetime
from pathlib import Path

# 55 Classic Arcade Games in the Multicade bootleg
# Order matters! Later games override earlier games for duplicate ROM filenames
GAMES = [
    {"num": 1,  "title": "Ms. Pac-Man",           "romset": "mspacman", "year": 1982},
    {"num": 2,  "title": "Galaga",                 "romset": "galaga",   "year": 1981},
    {"num": 3,  "title": "Frogger",                "romset": "frogger",  "year": 1981},
    {"num": 4,  "title": "Donkey Kong",            "romset": "dkong",    "year": 1981},
    {"num": 5,  "title": "Donkey Kong Junior",      "romset": "dkongjr",  "year": 1982},
    {"num": 6,  "title": "Donkey Kong 3",           "romset": "dkong3",   "year": 1983},
    {"num": 7,  "title": "Galaxian",                "romset": "galaxian", "year": 1979},
    {"num": 8,  "title": "Dig Dug",                 "romset": "digdug",   "year": 1982},
    {"num": 9,  "title": "Crush Roller",            "romset": "crush",    "year": 1981},
    {"num": 10, "title": "Mr. Do",                  "romset": "mrdo",     "year": 1982},
    {"num": 11, "title": "Space Invaders",           "romset": "invaders", "year": 1978},
    {"num": 12, "title": "Pac-Man",                 "romset": "pacman",   "year": 1980},
    {"num": 13, "title": "Galaga 3",                "romset": "galaga3",  "year": 1984},
    {"num": 14, "title": "Gyruss",                  "romset": "gyruss",   "year": 1983},
    {"num": 15, "title": "Tank Battalion",           "romset": "tankbatt", "year": 1980},
    {"num": 16, "title": "Ladybug",                 "romset": "ladybug",  "year": 1981},
    {"num": 17, "title": "Millipede",               "romset": "milliped", "year": 1982},
    {"num": 18, "title": "Burger Time",             "romset": "btime",    "year": 1982},
    {"num": 19, "title": "Jr. Pac-Man",             "romset": "jrpacman", "year": 1983},
    {"num": 20, "title": "Mappy",                   "romset": "mappy",    "year": 1983},
    {"num": 21, "title": "Pengo",                    "romset": "pengo",    "year": 1982},
    {"num": 22, "title": "1942",                     "romset": "1942",     "year": 1984},
    {"num": 23, "title": "Centipede",               "romset": "centiped", "year": 1981},
    {"num": 24, "title": "Phoenix",                  "romset": "phoenix",  "year": 1980},
    {"num": 25, "title": "Time Pilot",              "romset": "timeplt",  "year": 1982},
    {"num": 26, "title": "Super Cobra",             "romset": "scobra",   "year": 1981},
    {"num": 27, "title": "Video Hustler",           "romset": "hustler",  "year": 1981},
    {"num": 28, "title": "Space Panic",             "romset": "panic",    "year": 1980},
    {"num": 29, "title": "Super Breakout",           "romset": "sbrkout",  "year": 1978},
    {"num": 30, "title": "New Rally-X",             "romset": "nrallyx",  "year": 1981},
    {"num": 31, "title": "Arkanoid",                "romset": "arkanoid", "year": 1986},
    {"num": 32, "title": "Qix",                      "romset": "qix",      "year": 1981},
    {"num": 33, "title": "Juno First",               "romset": "junofrst", "year": 1983},
    {"num": 34, "title": "Xevious",                  "romset": "xevious",  "year": 1982},
    {"num": 35, "title": "Mr. Do's Castle",          "romset": "docastle", "year": 1983},
    {"num": 36, "title": "Moon Cresta",             "romset": "mooncrst", "year": 1980},
    {"num": 37, "title": "Pinball Action",           "romset": "pbaction", "year": 1985},
    {"num": 38, "title": "Scramble",                "romset": "scramble", "year": 1981},
    {"num": 39, "title": "Super Pac-Man",           "romset": "superpac", "year": 1982},
    {"num": 40, "title": "Bomb Jack",               "romset": "bombjack", "year": 1983},
    {"num": 41, "title": "Shao-Lin's Road",          "romset": "shaolins", "year": 1985},
    {"num": 42, "title": "King & Balloon",           "romset": "kingball", "year": 1980},
    {"num": 43, "title": "1943: The Battle of Midway", "romset": "1943",  "year": 1987},
    {"num": 44, "title": "Van Van-Car",              "romset": "vanvan",   "year": 1983},
    {"num": 45, "title": "Pac-Man Plus",             "romset": "pacplus",  "year": 1982},
    {"num": 46, "title": "Dig Dug II",              "romset": "digdug2",  "year": 1985},
    {"num": 47, "title": "Amidar",                  "romset": "amidar",   "year": 1981},
    {"num": 48, "title": "Zaxxon",                   "romset": "zaxxon",   "year": 1982},
    {"num": 49, "title": "Pooyan",                   "romset": "pooyan",   "year": 1982},
    {"num": 50, "title": "Pleiads",                  "romset": "pleiads",  "year": 1981},
    {"num": 51, "title": "Gun Smoke",               "romset": "gunsmoke", "year": 1985},
    {"num": 52, "title": "The End",                  "romset": "theend",   "year": 1980},
    {"num": 53, "title": "1943 Kai: Midway Kaisen",  "romset": "1943kai",  "year": 1987},
    {"num": 54, "title": "Congo Bongo",              "romset": "congo",    "year": 1983},
    {"num": 55, "title": "Jumping Jack",             "romset": "jjack",    "year": 1983},
]

# Parent ROM files (39in1.zip) - NOT included in multcade.zip
PARENT_ROM_FILES = [
    {"filename": "27c4096_plz-v001_ver.300.bin", "size": 524288,
     "description": "Main program ROM (encrypted)"},
    {"filename": "16mflash.bin", "size": 2097152,
     "description": "Flash data ROM (compressed ROM filesystem, CGC-NP203)"},
    {"filename": "93c66_eeprom.bin", "size": 512,
     "description": "EEPROM security data (93C66 16-bit)"},
]


def compute_crc32(data: bytes) -> int:
    """Compute CRC32 checksum for ROM data."""
    import zlib
    return zlib.crc32(data) & 0xFFFFFFFF


def build_multcade(source_dir: str, output_dir: str, verify_against: str = None) -> dict:
    """
    Build multcade.zip from individual game ROM ZIP files.
    
    Args:
        source_dir: Directory containing individual game ZIP files
        output_dir: Directory to write the built multcade.zip
        verify_against: Path to original multcade.zip for verification (optional)
    
    Returns:
        Build manifest dictionary with stats and file listings
    """
    source_path = Path(source_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    multcade_zip_path = output_path / "multcade.zip"
    
    # Collect all ROM files from individual game zips
    # Process games IN ORDER so later games override earlier games for duplicate filenames
    rom_files = {}  # filename -> (data, date_time, crc32, source_game, game_num)
    game_stats = []
    total_size = 0
    errors = []
    warnings = []
    overrides = []
    
    print("=" * 70)
    print("  Multicade 55-in-1 MAME Bootleg ROM Archive Builder")
    print("  MAME4Droid 0.139u1 | ROM Parent: multcade | Clone of: 39in1")
    print("=" * 70)
    print()
    
    # Process each game IN ORDER
    for game in GAMES:
        romset = game["romset"]
        game_zip = source_path / f"{romset}.zip"
        
        if not game_zip.exists():
            errors.append(f"Missing ROM ZIP: {romset}.zip (Game #{game['num']}: {game['title']})")
            print(f"  [ERROR] Missing: {romset}.zip - {game['title']} ({game['year']})")
            continue
        
        game_file_count = 0
        game_file_size = 0
        game_new_files = 0
        game_override_files = 0
        
        try:
            with zipfile.ZipFile(game_zip, 'r') as zf:
                for info in zf.infolist():
                    if info.is_dir():
                        continue
                    
                    filename = info.filename
                    data = zf.read(filename)
                    crc = compute_crc32(data)
                    
                    is_override = filename in rom_files
                    if is_override:
                        old_game = rom_files[filename][3]
                        old_crc = rom_files[filename][2]
                        overrides.append({
                            "filename": filename,
                            "from_game": old_game,
                            "to_game": romset,
                            "old_crc": f"{old_crc:08x}",
                            "new_crc": f"{crc:08x}",
                        })
                        game_override_files += 1
                    else:
                        game_new_files += 1
                    
                    # Always overwrite - later games win
                    rom_files[filename] = (data, info.date_time, crc, romset, game["num"])
                    game_file_count += 1
                    game_file_size += len(data)
                    total_size += len(data)
                    
        except zipfile.BadZipFile:
            errors.append(f"Corrupt ZIP file: {romset}.zip")
            print(f"  [ERROR] Corrupt: {romset}.zip")
            continue
        
        game_stats.append({
            "num": game["num"],
            "title": game["title"],
            "romset": romset,
            "year": game["year"],
            "file_count": game_file_count,
            "new_files": game_new_files,
            "override_files": game_override_files,
            "total_size": game_file_size,
        })
        
        override_str = f" (+{game_override_files} override)" if game_override_files > 0 else ""
        print(f"  [{game['num']:2d}] {romset:10s} - {game['title']:30s} "
              f"({game['year']}) | {game_new_files:3d} new, "
              f"{game_override_files:3d} override{override_str}, "
              f"{game_file_size:,} bytes")
    
    print()
    print(f"  Total unique ROM files: {len(rom_files)}")
    print(f"  Total overrides (duplicates resolved): {len(overrides)}")
    print(f"  Total uncompressed size: {total_size:,} bytes ({total_size/1024:.1f} KB)")
    
    if overrides:
        print()
        print("  Duplicate filename resolutions (later game wins):")
        for ov in overrides:
            print(f"    {ov['filename']:20s} : {ov['from_game']:10s} -> {ov['to_game']:10s} "
                  f"(CRC: {ov['old_crc']} -> {ov['new_crc']})")
    
    print()
    
    if errors:
        print(f"  ERRORS: {len(errors)}")
        for e in errors:
            print(f"    - {e}")
        print()
    
    # Build multcade.zip using Store compression (MAME standard)
    print("  Building multcade.zip (ZIP_STORED, no compression)...")
    
    with zipfile.ZipFile(multcade_zip_path, 'w', zipfile.ZIP_STORED) as zf_out:
        # Sort files for deterministic output
        for filename in sorted(rom_files.keys()):
            data, date_time, crc, source_game, game_num = rom_files[filename]
            
            info = zipfile.ZipInfo(filename, date_time)
            info.compress_type = zipfile.ZIP_STORED
            info.external_attr = 0
            
            zf_out.writestr(info, data)
    
    built_size = multcade_zip_path.stat().st_size
    print(f"  Built: {multcade_zip_path} ({built_size:,} bytes / {built_size/1024:.1f} KB)")
    print()
    
    # Self-verification of the built ZIP
    print("  Verifying built archive integrity...")
    verified = 0
    verify_errors = 0
    
    with zipfile.ZipFile(multcade_zip_path, 'r') as zf_verify:
        for info in zf_verify.infolist():
            filename = info.filename
            if filename in rom_files:
                data = zf_verify.read(filename)
                expected_crc = rom_files[filename][2]
                actual_crc = compute_crc32(data)
                if expected_crc != actual_crc:
                    verify_errors += 1
                    print(f"    [FAIL] CRC mismatch: {filename}")
                else:
                    verified += 1
            else:
                verify_errors += 1
                print(f"    [FAIL] Unexpected file: {filename}")
    
    print(f"  Self-verification: {verified}/{len(rom_files)} files OK, {verify_errors} errors")
    
    # Cross-verification against original multcade.zip if available
    cross_verified = 0
    cross_mismatches = 0
    cross_missing = 0
    cross_extra = 0
    
    if verify_against:
        orig_path = Path(verify_against)
        if orig_path.exists():
            print()
            print(f"  Cross-verifying against original: {orig_path}")
            
            with zipfile.ZipFile(orig_path, 'r') as zf_orig:
                orig_names = set(zf_orig.namelist())
                built_names = set(rom_files.keys())
                
                missing = orig_names - built_names
                extra = built_names - orig_names
                
                if missing:
                    cross_missing = len(missing)
                    print(f"    Missing in built: {missing}")
                if extra:
                    cross_extra = len(extra)
                    print(f"    Extra in built: {extra}")
                
                for name in orig_names:
                    if name in built_names:
                        orig_info = zf_orig.getinfo(name)
                        orig_data = zf_orig.read(name)
                        orig_crc = compute_crc32(orig_data)
                        
                        built_data = rom_files[name][0]
                        built_crc = rom_files[name][2]
                        
                        if orig_crc != built_crc:
                            cross_mismatches += 1
                            print(f"    [CRC DIFF] {name}: "
                                  f"orig={orig_crc:08x} ({len(orig_data)} bytes), "
                                  f"built={built_crc:08x} ({len(built_data)} bytes)")
                        else:
                            cross_verified += 1
                
                print(f"  Cross-verification: {cross_verified} OK, "
                      f"{cross_mismatches} CRC mismatches, "
                      f"{cross_missing} missing, {cross_extra} extra")
        else:
            print(f"  Original file not found: {orig_path} (skipping cross-verification)")
    
    print()
    
    # Build manifest
    manifest = {
        "rom_name": "multcade",
        "rom_description": "Multicade - 55-in-1 MAME Bootleg",
        "rom_parent": "39in1",
        "mame_version": "0.139u1",
        "target_platform": "MAME4Droid 0.139u1",
        "hardware": "Bootleg MAME-based arcade PCB (Intel Xscale PXA255 @ 200 MHz)",
        "status": "MACHINE_NOT_WORKING / MACHINE_IMPERFECT_SOUND",
        "build_date": datetime.utcnow().isoformat() + "Z",
        "total_games": len(GAMES),
        "games_processed": len(game_stats),
        "total_rom_files": len(rom_files),
        "total_uncompressed_size": total_size,
        "built_archive_size": built_size,
        "compression": "Store (ZIP_STORED)",
        "duplicate_resolution": "Later game in list order overrides earlier game for duplicate filenames",
        "overrides": overrides,
        "games": game_stats,
        "rom_files": [
            {
                "filename": fn,
                "size": len(rom_files[fn][0]),
                "crc32": f"{rom_files[fn][2]:08x}",
                "source_game": rom_files[fn][3],
                "game_number": rom_files[fn][4],
                "date_time": f"{rom_files[fn][1][0]:04d}-{rom_files[fn][1][1]:02d}-{rom_files[fn][1][2]:02d} "
                             f"{rom_files[fn][1][3]:02d}:{rom_files[fn][1][4]:02d}:{rom_files[fn][1][5]:02d}",
            }
            for fn in sorted(rom_files.keys())
        ],
        "parent_rom": {
            "name": "39in1",
            "description": "39-in-1 MAME bootleg (GNO-V000)",
            "files": PARENT_ROM_FILES,
        },
        "verification": {
            "self_verification": {
                "verified": verified,
                "errors": verify_errors,
            },
            "cross_verification": {
                "available": verify_against is not None and Path(verify_against).exists(),
                "verified": cross_verified,
                "crc_mismatches": cross_mismatches,
                "missing_files": cross_missing,
                "extra_files": cross_extra,
            } if verify_against else None,
        },
        "errors": errors,
    }
    
    # Write manifest
    manifest_path = output_path / "multcade_manifest.json"
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"  Manifest written: {manifest_path}")
    print()
    
    # Summary
    print("=" * 70)
    print("  BUILD SUMMARY")
    print("=" * 70)
    print(f"  ROM Name:          multcade")
    print(f"  ROM Parent:        39in1 (clone of)")
    print(f"  Target:            MAME4Droid 0.139u1")
    print(f"  Games included:    {len(game_stats)}/55")
    print(f"  ROM files:         {len(rom_files)}")
    print(f"  Duplicate overrides: {len(overrides)}")
    print(f"  Uncompressed size: {total_size:,} bytes ({total_size/1024:.1f} KB)")
    print(f"  Archive size:      {built_size:,} bytes ({built_size/1024:.1f} KB)")
    print(f"  Compression:       Store (no compression - MAME standard)")
    print(f"  Self-verification:  {verified} OK, {verify_errors} errors")
    if verify_against and Path(verify_against).exists():
        print(f"  Cross-verification: {cross_verified} OK, {cross_mismatches} CRC mismatches")
    print(f"  Build errors:      {len(errors)}")
    print()
    print(f"  Output: {multcade_zip_path}")
    print(f"  Manifest: {manifest_path}")
    print("=" * 70)
    
    return manifest


if __name__ == "__main__":
    source_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "./build"
    verify_against = sys.argv[3] if len(sys.argv) > 3 else None
    
    # Auto-detect original multcade.zip for cross-verification
    if verify_against is None:
        orig_path = Path(source_dir) / "multcade.zip"
        if orig_path.exists():
            verify_against = str(orig_path)
    
    manifest = build_multcade(source_dir, output_dir, verify_against)
    
    sys.exit(1 if manifest["errors"] else 0)
