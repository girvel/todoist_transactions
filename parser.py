import logging
import re
import time
from datetime import datetime
from pathlib import Path

import yaml
from fire import Fire
from tiny_storage import Unit
from todoist_api_python.api import TodoistAPI


config = Unit('todoist_transactions')
api = TodoistAPI(config('api_token').put(lambda: input("Your API token: ")))
log = logging.getLogger(__name__)


def append(path, entry):
    l = yaml.safe_load(path.read_text())
    l = [entry] + l
    path.write_text(yaml.safe_dump(l))


def main():
    inbox = next(p for p in api.get_projects() if p.is_inbox_project)

    while True:
        tasks = api.get_tasks(project_id=inbox.id)

        for t in tasks:
            if (
                (m := re.match(r'^T\s+(\S+)\s+(\S+)\s*$', t.content)) and
                api.close_task(t.id)
            ):
                append(
                    Path(config('journal_file')
                        .put(lambda: input("Journal file: "))
                    ),
                    {
                        "date": datetime.now(),
                        "amount": -int(m.group(2)),
                        "comment": m.group(1),
                    }
                )

                log.info(f'Appended {t.content!r}')

            time.sleep(5000)


if __name__ == '__main__':
    Fire(main)