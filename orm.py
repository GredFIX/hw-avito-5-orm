from simple_orm import SqliteDatabase, Model, CharField, IntegerField

db = SqliteDatabase(":memory:")


class BaseModel(Model):
    class Meta:
        database = db


class Advert(BaseModel):
    title = CharField(max_length=180)
    price = IntegerField(min_value=0)


if __name__ == '__main__':
    db.connect()
    db.create_tables([Advert])
    Advert.create(title='iPhone X', price=100)
    adverts = Advert.select()
    assert adverts[0] == 'iPhone X | 100'
