from uuid import UUID

from pydantic import BaseModel, Field, model_validator


class ClaimEvidence(BaseModel):
    source_interaction_id: UUID
    excerpt: str = Field(min_length=1)


class AssetClaim(BaseModel):
    text: str = Field(min_length=1)
    source_interaction_ids: list[UUID] = Field(min_length=1)
    evidence: list[ClaimEvidence] = Field(min_length=1)

    @model_validator(mode="after")
    def evidence_must_reference_claim_sources(self):
        evidence_source_ids = {
            item.source_interaction_id
            for item in self.evidence
        }

        missing = set(self.source_interaction_ids) - evidence_source_ids
        if missing:
            raise ValueError(
                "Every source_interaction_id must have matching evidence."
            )

        return self


class TraceableAsset(BaseModel):
    schema_version: str = "v1"
    opportunity_id: UUID
    title: str = Field(min_length=1)
    claims: list[AssetClaim] = Field(min_length=1)
