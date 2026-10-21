"""Copy generic research records without overwriting any existing file."""
import argparse
from pathlib import Path
import shutil


def initialize(project, templates=None):
    source=Path(templates) if templates else Path(__file__).resolve().parents[1]/'templates'/'research'
    project=Path(project).resolve()
    if not project.is_dir():raise ValueError('Project directory must already exist')
    destination=project/'research'
    if destination.is_symlink():raise ValueError('Refusing symlink research directory')
    files=sorted(source.glob('*.md'))
    conflicts=[p.name for p in files if (destination/p.name).exists() or (destination/p.name).is_symlink()]
    if conflicts:raise FileExistsError('No files copied; conflicts: '+', '.join(conflicts))
    destination.mkdir(exist_ok=True)
    for p in files:
        with (destination/p.name).open('x') as out:out.write(p.read_text())
    return len(files)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project',required=True)
    args=parser.parse_args()
    print('Created',initialize(args.project),'research files; existing AI entry files untouched.')
