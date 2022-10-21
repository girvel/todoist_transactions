#!/usr/bin/env python3.10

import logging
import re
from datetime import datetime
from pathlib import Path

import yaml
from fire import Fire
from tiny_storage import Unit, Type
from todoist_api_python.api import TodoistAPI


config = Unit('todoist_transactions', Type.global_config)
log = logging.getLogger(__name__)


def append(path, entry):
    path.touch()
    l = yaml.safe_load(path.read_text())
    l = [entry] + (l or [])
    path.write_text(yaml.safe_dump(l))


class Cli:
    def __call__(self):
        api = TodoistAPI(
            config('api_token')
                .put(lambda: input("Todoist API token: "))
        )

        inbox = next(p for p in api.get_projects() if p.is_inbox_project)

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


    def setup(self):
        config('api_token').push(lambda: input("Todoist API token: "))
        config('journal_file').push(lambda: input("Journal file: "))


if __name__ == '__main__':
    Fire(Cli())
