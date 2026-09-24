from app.schemas.v1.process import ProcessRequest
def test_process_schema_v1():
    r=ProcessRequest(organization_id='one',community_id='g10',reference_period='2026-W38',requested_assets=['LINKEDIN'],interactions=[{'author':'Ana','channel':'general','type':'testimonio','text':'Un logro'}])
    assert r.schema_version == 'v1'
