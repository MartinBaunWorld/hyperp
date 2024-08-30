#!/usr/bin/env python3
import os
import math


from playhouse.kv import KeyValue


def update_model(model, updates):
    for key, value in updates.items():
        if value is 'Untouched':
            continue

        setattr(model, key, value)

    return model


def migrate(database, migration_path):
    files = sorted(os.listdir(migration_path))
    kv = KeyValue(database=database)
    for f in files:
        if not f.endswith(".sql"):
            continue

        if "migration_" + f in kv:
            continue

        print(f"Migration {f}...")
        with open(f"{migration_path}/{f}") as fh:
            cursor = database.execute_sql(fh.read())
            kv["migration_" + f] = "completed"
            cursor = cursor.close()


def paginate(qs, paginate_by: int, page: int):

    objects = []

    total_objects = qs.count()
    total_pages = int(math.ceil(float(total_objects / paginate_by)))

    if page < total_pages:
        objects = qs.paginate(page, paginate_by)
        
    return objects, total_objects, total_pages 
