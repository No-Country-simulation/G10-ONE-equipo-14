from enum import StrEnum


class AssetState(StrEnum):
    PENDING_REVIEW = "PENDING_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class InvalidAssetTransition(ValueError):
    pass


_DECISION_TRANSITIONS = {
    AssetState.PENDING_REVIEW: {AssetState.APPROVED, AssetState.REJECTED},
}


def decide(current: str, target: str) -> str:
    current_state = AssetState(current)
    target_state = AssetState(target)
    if target_state not in _DECISION_TRANSITIONS.get(current_state, set()):
        raise InvalidAssetTransition(
            f"Asset cannot transition from {current_state.value} to {target_state.value}."
        )
    return target_state.value


def state_after_edit(current: str) -> str:
    current_state = AssetState(current)
    if current_state is AssetState.APPROVED:
        raise InvalidAssetTransition("Approved assets are immutable.")
    if current_state in {AssetState.PENDING_REVIEW, AssetState.REJECTED}:
        return AssetState.PENDING_REVIEW.value
    raise InvalidAssetTransition(f"Asset in state {current_state.value} cannot be edited.")


def require_publishable(current: str) -> None:
    current_state = AssetState(current)
    if current_state is not AssetState.APPROVED:
        raise InvalidAssetTransition("Only approved assets can be published.")
