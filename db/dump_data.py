import json
from datetime import datetime
from pathlib import Path

from models import Reminder
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

table_names_to_dump = ["reminder"]
model_classes = {
    "reminder": Reminder,
}
out_file_name = "fixtures.json"

path = str(Path(__file__).parent.parent / "db.sqlite")
engine = create_engine("sqlite:///" + path, echo=True)

Session = sessionmaker(bind=engine)
session = Session()


def serialize_value(value):
    if isinstance(value, datetime):
        return datetime.strftime(value, "%Y-%m-%d %H:%M:%S")
    return value


def serialize_table(model):
    data = [
        {
            column.name: serialize_value(getattr(row, column.name))
            for column in model.__table__.columns
        }
        for row in session.query(model).all()
    ]
    return data


tables_data = {}

for table_name in table_names_to_dump:
    model_class = model_classes.get(table_name)
    if model_class is not None:
        tables_data[table_name] = serialize_table(model_class)
    else:
        print(f"Model class for table {table_name} not found.")

with open(out_file_name, "w") as f:
    json.dump(tables_data, f, indent=4)

print(f"Data has been dumped to {out_file_name}")
