import os
import pathlib
import sys

def generate_tree(root='.', exclude='node_modules'):
    tree_lines = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d != exclude]
        rel_path = os.path.relpath(dirpath, root)
        depth = 0 if rel_path == '.' else rel_path.count(os.sep) + 1
        indent = ('│   ' * (depth - 1)) + ('├── ' if depth > 0 else '')
        if rel_path != '.':
            tree_lines.append(f"{indent}{os.path.basename(dirpath)}/")
        file_indent = '│   ' * depth + '├── '
        for f in sorted(filenames):
            tree_lines.append(f"{file_indent}{f}")
    return '\n'.join(tree_lines)

if __name__ == '__main__':
    try:
        root_path = pathlib.Path(__file__).parent
        output = generate_tree(str(root_path), exclude='node_modules')
        out_file = root_path / 'project_structure.txt'
        out_file.write_text(output, encoding='utf-8')
        print(f'Generated {out_file}')
    except Exception as e:
        print('Error generating structure:', e, file=sys.stderr)
        sys.exit(1)
