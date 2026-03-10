import os

def extract_readmes(output_file='extracted_readmes.md'):
    """
    Finds all README.md files recursively in the current directory,
    and writes their content to an output file with source directory headers.
    """
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for root, dirs, files in os.walk('.'):
            # Skip .git directory to avoid clutter
            if '.git' in dirs:
                dirs.remove('.git')
            
            for file in files:
                if file.lower() == 'readme.md':
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(root, '.')
                    
                    display_path = rel_path if rel_path != '.' else 'root directory'
                    
                    outfile.write(f"# Source: {display_path}\n")
                    outfile.write(f"File: {file_path}\n\n")
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as infile:
                            content = infile.read()
                            outfile.write(content)
                            if not content.endswith('\n'):
                                outfile.write('\n')
                    except Exception as e:
                        outfile.write(f"Error reading {file_path}: {e}\n")
                    
                    outfile.write("\n---\n\n")

if __name__ == "__main__":
    extract_readmes()
