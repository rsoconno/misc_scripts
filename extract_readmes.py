import os
import sys

def extract_readmes(start_dir='.', output_file='extracted_readmes.md'):
    """
    Finds all README and README.md files recursively in the specified directory,
    and writes their content to an output file with source directory headers.
    """
    readmes_found = []

    for root, dirs, files in os.walk(start_dir):
        # Skip .git directory to avoid clutter
        if '.git' in dirs:
            dirs.remove('.git')

        for file in files:
            if file.lower() in ['readme', 'readme.md']:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(root, start_dir)
                display_path = rel_path if rel_path != '.' else 'root directory'

                try:
                    with open(file_path, 'r', encoding='utf-8') as infile:
                        content = infile.read()
                        readmes_found.append({
                            'display_path': display_path,
                            'file_path': file_path,
                            'content': content
                        })
                except Exception as e:
                    readmes_found.append({
                        'display_path': display_path,
                        'file_path': file_path,
                        'content': f"Error reading {file_path}: {e}\n"
                    })

    if not readmes_found:
        print("No README files found.")
        return

    with open(output_file, 'w', encoding='utf-8') as outfile:
        for i, readme in enumerate(readmes_found):
            outfile.write(f"================================================================================\n")
            outfile.write(f"SOURCE: {readme['display_path']}\n")
            outfile.write(f"FILE: {readme['file_path']}\n")
            # Clear demarkation between readmes
            outfile.write(f"================================================================================\n\n")

            outfile.write(readme['content'])
            if not readme['content'].endswith('\n'):
                outfile.write('\n')
            
            outfile.write("\n\n")

if __name__ == "__main__":
    directory = sys.argv[1] if len(sys.argv) > 1 else '.'
    extract_readmes(directory)
