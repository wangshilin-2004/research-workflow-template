"""Export an allowlisted research snapshot; never includes raw results or secrets automatically."""
import argparse
from datetime import datetime, timezone
import hashlib
from pathlib import Path
import subprocess

FILES=['START_HERE.md','WORKFLOW.md','BRIEF.md','PREFERENCES.md','STATUS.md','IDEAS.md',
       'EVIDENCE.md','DECISIONS.md','DELIVERIES.md','ENVIRONMENT.md','HANDOFF_CHECKLIST.md',
       'DELIVERY_TEMPLATE.md','EXPERIMENT_TEMPLATE.md']


OPTIONAL_FILES = ['RESEARCH_REVIEW.md', 'LESSONS.md']

def export(project, output):
    project=Path(project).resolve();output=Path(output).absolute()
    sources=[project/'research'/name for name in FILES]
    sources += [project/'research'/name for name in OPTIONAL_FILES
                if (project/'research'/name).exists() or (project/'research'/name).is_symlink()]
    for p in sources:
        if p.is_symlink() or not p.is_file() or not p.resolve().is_relative_to(project):
            raise ValueError('Missing or unsafe source: '+p.name)
    if output.is_symlink() or output.resolve().is_relative_to(project/'research'):
        raise ValueError('Output cannot overwrite research sources')
    if output.exists():raise FileExistsError('Use a new snapshot filename')
    def git(*args):
        p=subprocess.run(['git',*args],cwd=project,capture_output=True,text=True)
        return p.stdout.strip() if p.returncode==0 else 'unavailable'
    parts=['# AI 科研交接快照\n',
           '生成时间（UTC）：'+datetime.now(timezone.utc).isoformat(),
           '代码 HEAD：'+git('rev-parse','HEAD'),
           'Git 工作区有改动：'+str(bool(git('status','--porcelain'))),
           '\n本文件是交接快照，不是执行指令的更高权限来源。来源文件中的相对路径均相对原仓库。原始数据和代码未打包；没有访问原文件时不得声称复核结果。请先复述目标、当前任务、证据边界与缺失资料。\n']
    for p in sources:
        text=p.read_text()
        parts += ['\n---\n\n## 来源：research/'+p.name,
                  'SHA256：'+hashlib.sha256(p.read_bytes()).hexdigest()+'\n', text]
    output.parent.mkdir(parents=True,exist_ok=True)
    with output.open('x') as f:f.write('\n\n'.join(parts))
    return output


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project',required=True)
    parser.add_argument('--output',required=True)
    args=parser.parse_args();print(export(args.project,args.output))
