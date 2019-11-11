from courses.models import Record
from orders.creator import OrderCreator
from tinkoff.client import TinkoffBank
from users.models import User

f213 = User.objects.last()
rec = Record.objects.last()

order = OrderCreator(user=f213, item=rec, price='150')()

client = TinkoffBank(order)

print(client.get_initial_payment_url())
