from apps.dashamail.lists.http import DashamailListsHTTP


class DashamailListsDTO:
    @property
    def api(self) -> DashamailListsHTTP:
        return DashamailListsHTTP()
