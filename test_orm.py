import pytest
from unittest.mock import patch, MagicMock

from .simple_orm import Model, SqliteDatabase, CharField, IntegerField


@patch("sqlite3.connect")
def test_create_tables_ok(mock_connect):
    cm = MagicMock()
    mock_connect.return_value = cm

    int_field = MagicMock()
    int_field.to_sql.return_value = "test_field_int INTEGER"

    char_field = MagicMock()
    char_field.to_sql.return_value = "test_field_char TEXT"

    class TestModel:
        _name = "test_model"
        _data = {
            "test_field_int": {"_meta": int_field},
            "test_field_char": {"_meta": char_field},
        }

    db = SqliteDatabase(":memory:")

    db.connect()
    db.create_tables([TestModel])
    db.close()

    cm.execute.assert_called_once_with(
        "create table if not exists test_model ("
        "test_field_int INTEGER, "
        "test_field_char TEXT);"
    )
    cm.close.assert_called_once()


@patch("sqlite3.connect")
def test_save_entity_ok(mock_connect):
    cm = MagicMock()
    mock_connect.return_value = cm

    db = SqliteDatabase(":memory:")

    class BaseModel(Model):
        class Meta:
            database = db

    class Advert(BaseModel):
        title = CharField(max_length=180)
        price = IntegerField(min_value=0)

    db.connect()
    Advert.create(title="iPhone X", price=100)
    db.close()

    cm.execute.assert_called_once_with(
        "insert into Advert values ('iPhone X', 100)"
    )
    cm.close.assert_called_once()


@patch("sqlite3.connect")
def test_select_entities_ok(mock_connect):
    cm = MagicMock()
    mock_connect.return_value = cm

    db = SqliteDatabase(":memory:")

    class BaseModel(Model):
        class Meta:
            database = db

    class Advert(BaseModel):
        title = CharField(max_length=180)
        price = IntegerField(min_value=0)

    db.connect()
    Advert.select()
    db.close()

    cm.execute.assert_called_once()
    cm.execute.assert_called_with("select * from Advert;")
    cm.close.assert_called_once()


def test_char_field_ok():
    title_field = CharField(max_length=5)
    title_field._name = "title"

    class Advert:
        _data = {"title": {}}
        title = title_field

    a = Advert()
    a.title = "test"

    assert a.title == "test"


def test_char_field_invalid_length():
    title_field = CharField(max_length=5)
    title_field._name = "title"

    class Advert:
        _data = {"title": {}}
        title = title_field

    a = Advert()

    with pytest.raises(ValueError):
        a.title = "test_test_test"

    assert a.title == ""


def test_int_field_ok():
    price_field = IntegerField(min_value=100)
    price_field._name = "price"

    class Advert:
        _data = {"price": {}}
        price = price_field

    a = Advert()
    a.price = 123

    assert a.price == 123


def test_int_field_invalid_value():
    price_field = IntegerField(min_value=100)
    price_field._name = "price"

    class Advert:
        _data = {"price": {}}
        price = price_field

    a = Advert()
    with pytest.raises(ValueError):
        a.price = 99
