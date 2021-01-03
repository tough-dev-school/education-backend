from products.models import Record
from shipping.shipments import RecordShipment
from users.models import User


def ship():
    f213 = User.objects.last()
    record = Record.objects.last()

    RecordShipment(f213, record)()
