from typing import TypedDict


class WildScanState(TypedDict, total=False):
    scan_job_id: str
    raw_listings: list[dict]
    normalized_listings: list[dict]
    new_listings: list[dict]
    duplicate_count: int
    triaged_listings: list[dict]
    triaged_out_count: int
    text_analyses: list[dict]
    image_analyses: list[dict]
    classified_listings: list[dict]
    scored_listings: list[dict]
    red_count: int
    amber_count: int
    yellow_count: int
    clear_count: int
    briefs_generated: list[dict]
    errors: list[str]
    processing_time_ms: int
