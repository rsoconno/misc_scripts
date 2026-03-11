import os
import re
import argparse
from pathlib import Path

def extract_comments(file_path):
    """Parses code files for LMOD blocks, including multi-line C-style comments."""
    lmod_blocks = []
    top_level_comments = []
    
    # Prefixes for line-based comments
    line_prefixes = ('#', '//', '--', '*')
    lmod_re = re.compile(r'LMOD', re.IGNORECASE)

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            
            # 1. Extract Top-Level Headers (First 15 lines)
            for i in range(min(15, len(lines))):
                strip_line = lines[i].strip()
                if strip_line.startswith(line_prefixes) or strip_line.startswith('/*'):
                    top_level_comments.append(strip_line)

            # 2. Extract LMOD Blocks (handling both line-based and /* */ blocks)
            processed_indices = set()
            
            for i, line in enumerate(lines):
                if i in processed_indices:
                    continue
                
                if lmod_re.search(line):
                    block = []
                    
                    # CASE A: Inside a C-style block /* ... */
                    # We look backwards for /* and forwards for */
                    is_c_block = False
                    start_c = i
                    while start_c >= 0:
                        if '/*' in lines[start_c]:
                            is_c_block = True
                            break
                        if '*/' in lines[start_c] and start_c != i: # Hit a different block's end
                            break
                        start_c -= 1
                    
                    if is_c_block:
                        end_c = i
                        while end_c < len(lines):
                            if '*/' in lines[end_c]:
                                break
                            end_c += 1
                        
                        for idx in range(start_c, min(end_c + 1, len(lines))):
                            block.append(f"Line {idx+1}: {lines[idx].rstrip()}")
                            processed_indices.add(idx)
                    
                    # CASE B: Standard Line-based comments (#, //, --)
                    else:
                        start_l = i
                        while start_l > 0 and lines[start_l-1].strip().startswith(line_prefixes):
                            start_l -= 1
                        
                        end_l = i
                        while end_l < len(lines) - 1 and lines[end_l+1].strip().startswith(line_prefixes):
                            end_l += 1
                        
                        for idx in range(start_l, end_l + 1):
                            block.append(f"Line {idx+1}: {lines[idx].rstrip()}")
                            processed_indices.add(idx)
                    
                    if block:
                        lmod_blocks.append(block)
                        
    except (PermissionError, OSError):
        return None

    return (lmod_blocks, top_level_comments) if lmod_blocks else None

def main():
    parser = argparse.ArgumentParser(description="Extract LMOD modifications from C, SQL, and Shell files.")
    parser.add_argument("repo_path", help="Path to the git repository")
    args = parser.parse_args()

    repo_root = Path(args.repo_path).resolve()
    if not repo_root.is_dir():
        print(f"Error: {repo_root} is not a valid directory.")
        return

    # Restricted file set
    ALLOWED_EXTENSIONS = {'.sql', '.sh', '.shl', '.c', '.h'}
    # Filter out documentation
    IGNORED_NAMES = {'README', 'LICENSE', '.MD'}

    output_filename = f"lmod_report_{repo_root.name}.txt"
    included_count = 0
    excluded_count = 0

    print(f"🚀 Scanning {repo_root.name} for LMOD code modifications...")

    with open(output_filename, 'w', encoding='utf-8') as out:
        out.write(f"LMOD AUDIT REPORT: {repo_root.name}\n")
        out.write(f"Targeting: {', '.join(ALLOWED_EXTENSIONS)}\n")
        out.write("=" * 60 + "\n\n")

        for root, dirs, files in os.walk(repo_root):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                file_path = Path(root) / file
                ext = file_path.suffix.lower()
                
                # Skip .py, .cpp, .md and check whitelist
                if ext not in ALLOWED_EXTENSIONS or any(ign in file.upper() for ign in IGNORED_NAMES):
                    excluded_count += 1
                    continue

                result = extract_comments(file_path)
                
                if result:
                    lmod_blocks, top_list = result
                    included_count += 1
                    rel_path = file_path.relative_to(repo_root)
                    
                    out.write(f"FILE: {rel_path}\n" + "-"*40 + "\n")
                    if top_list:
                        out.write("  [HEADER]\n  " + "\n  ".join(top_list) + "\n\n")
                    
                    out.write("  [LMOD BLOCKS]\n")
                    for block in lmod_blocks:
                        out.write("    " + "\n    ".join(block) + "\n" + "    " + "."*20 + "\n")
                    out.write("\n" + "*"*60 + "\n\n")
                else:
                    excluded_count += 1

    print("-" * 30)
    print(f"✅ Audit Complete!")
    print(f"📊 Included: {included_count} files (containing LMOD)")
    print(f"📊 Excluded: {excluded_count} files (non-code or no LMOD found)")
    print(f"📄 Report: {output_filename}")

if __name__ == "__main__":
    main()