from .dataset import build_dataset
from .evaluator import run
from pathlib import Path
import json
if __name__=='__main__':
    report=run(build_dataset()); out=Path(__file__).parent/'results'/'latest_report.json'; out.parent.mkdir(exist_ok=True); out.write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2)); print('Release gate:', 'PASS' if report['passed'] else 'FAIL')
