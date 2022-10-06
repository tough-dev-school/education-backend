import simplejson as json
from anymail.backends.console import EmailBackend


class ConsoleEmailBackend(EmailBackend):
    """Dev backend to print external ESP template context along with default django output
    """
    def write_message(self, message):
        context = json.dumps(message.merge_global_data, sort_keys=True, indent=4, ensure_ascii=False)

        msg = message.message()
        msg_data = msg.as_bytes()
        charset = (
            msg.get_charset().get_output_charset() if msg.get_charset() else 'utf-8'
        )
        msg_data = msg_data.decode(charset)
        self.stream.write(f'{msg_data}\n')
        self.stream.write(f'{context}\n')
        self.stream.write('-' * 79)
        self.stream.write('\n')
