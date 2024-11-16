from pydantic import BaseModel

from data_model import SegmentBox


class TOCItem(BaseModel):
    indentation: int
    label: str = ""
    selection_rectangle: SegmentBox
    point_closed: bool = False
