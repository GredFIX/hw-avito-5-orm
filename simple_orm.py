import sqlite3


class SqliteDatabase:
    def __init__(self, db_name: str):
        self.db_name = db_name

    def connect(self):
        self.conn = sqlite3.connect(self.db_name)

    def close(self):
        self.conn.close()

    def create_tables(self, models: list):
        for model in models:
            table_columns = ", ".join(
                [field["_meta"].to_sql() for _, field in model._data.items()]
            )
            self.conn.execute(
                "create table if not exists "
                f"{model._name} ({table_columns});"
            )


class Field:
    def __get__(self, obj, type=None):
        if self._name in obj._data and "_value" in obj._data[self._name]:
            return obj._data[self._name]["_value"]
        return self._default_value

    def __set__(self, obj, value):
        obj._data[self._name]["_value"] = value

    def to_sql(self) -> str:
        return f"{self._name} {self._type}"


class CharField(Field):
    _name = ""
    _type = "TEXT"
    _default_value = ""

    def __init__(self, min_length=0, max_length=255):
        self.min_length = min_length
        self.max_length = max_length

    def __set__(self, obj, value):
        if not isinstance(value, str):
            raise TypeError(obj, self._name, str, value)
        if len(value) > self.max_length or len(value) < self.min_length:
            raise ValueError(
                "value must be between {min} and {max}".format(
                    min=self.min_length, max=self.max_length
                )
            )
        super().__set__(obj, value)


class IntegerField(Field):
    _name = ""
    _type = "INTEGER"
    _default_value = 0

    def __init__(self, min_value=-(2 ** 63)):
        self.min_value = min_value

    def __set__(self, obj, value):
        if not isinstance(value, int):
            raise TypeError(obj, self._name, int, value)
        if value < self.min_value:
            raise ValueError(
                "value must be more than {min}".format(min=self.min_value)
            )
        super().__set__(obj, value)


class ModelMeta(type):
    def __new__(
        mcs, future_class_name, future_class_parents, future_class_attr
    ):
        meta = future_class_attr.pop("Meta", None)
        if meta:
            for k, v in meta.__dict__.items():
                if not k.startswith("_"):
                    future_class_attr[k] = v

        future_class_attr["_name"] = future_class_name
        future_class_attr["_data"] = {}
        for name, value in future_class_attr.items():
            if isinstance(value, Field):
                value._name = name
                future_class_attr["_data"][name] = {"_meta": value}

        return super(ModelMeta, mcs).__new__(
            mcs, future_class_name, future_class_parents, future_class_attr
        )


class Model(metaclass=ModelMeta):
    def __init__(self, *args, **kwargs):
        for k in kwargs:
            setattr(self, k, kwargs[k])

    @classmethod
    def create(cls, **query):
        ins = cls(**query)
        print(ins._data)
        values = ", ".join(
            [
                f"'{field['_value']}'"
                if isinstance(field["_value"], str)
                else str(field["_value"])
                for _, field in ins._data.items()
            ]
        )
        ins.database.conn.execute(f"insert into {cls._name} values ({values})")

    @classmethod
    def select(cls):
        res = cls.database.conn.execute(f"select * from {cls._name};")
        result = [
            " | ".join([str(el) for el in row]) for row in res.fetchall()
        ]

        return result
