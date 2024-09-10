from typing import List, Optional

class InputSpec:
    def __init__(
        self,
        data: str,
        purposes: Optional[List[str]] = None,
        security_tags: Optional[List[str]] = None,
        third_parties: Optional[List[str]] = None,
        third_party_purposes: Optional[List[str]] = None
    ):
        self.data = data
        self.purposes = purposes or []
        self.security_tags = security_tags or []
        self.third_parties = third_parties or []
        self.third_party_purposes = third_party_purposes or []

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return (
            f"InputSpec("
            f"data='{self.data}', "
            f"purpose={repr(self.purposes)}, "
            f"security_tag={repr(self.security_tags)}, "
            f"third_party={repr(self.third_parties)}, "
            f"third_party_purpose={repr(self.third_party_purposes)})"
        )