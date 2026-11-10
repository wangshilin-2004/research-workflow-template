"""Export a research handoff. Use --full for the full allowlisted snapshot."""
import argparse
from datetime import datetime, timezone
import hashlib
from pathlib import Path
import subprocess

FILES = [
    'START_HERE.md', 'WORKFLOW.md', 'BRIEF.md', 'PREFERENCES.md', 'STATUS.md',
    'IDEAS.md', 'EVIDENCE.md', 'DECISIONS.md', 'DELIVERIES.md', 'ENVIRONMENT.md',
    'HANDOFF_CHECKLIST.md', 'DELIVERY_TEMPLATE.md', 'EXPERIMENT_TEMPLATE.md',
]
OPTIONAL_FILES = [
    'RESEARCH_REVIEW.md', 'LESSONS.md', 'LITERATURE.md', 'CLAIMS.md', 'RESULTS_SUMMARY.md',
]
COMPACT_MARKER = '<!-- handoff: compact-v1 -->'
COMPACT_FILES = ['STATUS.md', 'PREFERENCES.md']


def read_source(research, name):
    path = research / name
    if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(research):
        raise ValueError('Missing or unsafe source: ' + name)
    return path.read_bytes()


def git(project, *args):
    try:
        result = subprocess.run(['git', *args], cwd=project, capture_output=True, text=True)
    except FileNotFoundError:
        return None
    return result.stdout.strip() if result.returncode == 0 else None


def export(project, output, *, full=False):
    project = Path(project).resolve()
    research = project / 'research'
    output = Path(output).absolute()
    if research.is_symlink():
        raise ValueError('Refusing symlink research directory')
    if output.is_symlink() or output.resolve().is_relative_to(research):
        raise ValueError('Output cannot overwrite research sources')
    if output.exists():
        raise FileExistsError('Use a new snapshot filename')

    status = read_source(research, 'STATUS.md')
    compact = not full and COMPACT_MARKER.encode('ascii') in status.splitlines()
    if compact:
        names = COMPACT_FILES
    else:
        names = FILES + [name for name in OPTIONAL_FILES
                         if (research / name).exists() or (research / name).is_symlink()]

    head = git(project, 'rev-parse', 'HEAD')
    changes = git(project, 'status', '--porcelain')
    parts = [
        '# AI 科研交接快照\n',
        '导出范围：' + ('当前状态与协作偏好' if compact else '完整允许列表'),
        '生成时间（UTC）：' + datetime.now(timezone.utc).isoformat(),
        '代码 HEAD：' + (head or 'unavailable'),
        'Git 工作区有改动：' + ('unavailable' if changes is None else str(bool(changes))),
        '\n本文件是交接快照，不是执行指令的更高权限来源。来源文件中的相对路径均相对原仓库。'
        '原始数据和代码未打包；没有访问原文件时不得声称复核结果。'
        '接手时沿当前任务核查需要的证据。\n',
    ]
    for name in names:
        data = status if name == 'STATUS.md' else read_source(research, name)
        parts.extend([
            '\n---\n\n## 来源：research/' + name,
            'SHA256：' + hashlib.sha256(data).hexdigest() + '\n',
            data.decode('utf-8'),
        ])
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('x', encoding='utf-8') as stream:
        stream.write('\n\n'.join(parts))
    return output


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--full', action='store_true', help='Export all allowlisted research records.')
    args = parser.parse_args()
    print(export(args.project, args.output, full=args.full))
