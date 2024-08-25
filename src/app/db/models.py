from tortoise import fields
from tortoise.models import Model


class InitialData(Model):
    id = fields.IntField(primary_key=True)
    provider_name = fields.CharField(max_length=255)
    initial_value = fields.DecimalField(max_digits=18, decimal_places=2)


class HistoricalTransaction(Model):
    id = fields.IntField(primary_key=True)
    provider_id = fields.ForeignKeyField(
        model_name="models.InitialData", related_name="transactions"
    )
    transaction_value = fields.DecimalField(max_digits=18, decimal_places=2)
