"""Connection recovery and polling cadence with no network or real waits."""

from unittest.mock import Mock

import requests

from dashboard.service_status import ServiceStatus


HEALTH = {"status": "ok", "database": "ok"}


def test_cold_start_retries_then_recovers_without_a_page_reload():
    check = Mock(side_effect=[requests.Timeout(), requests.Timeout(), HEALTH])
    status = ServiceStatus()

    assert not status.poll(check, now=0)
    assert status.health is None
    assert not status.poll(check, now=14)
    assert check.call_count == 1
    assert not status.poll(check, now=15)
    assert status.poll(check, now=30)
    assert status.health == HEALTH
    assert status.error is None
    assert status.waiting_since is None
    assert check.call_count == 3


def test_connected_sessions_do_not_repeat_health_checks_on_every_interaction():
    check = Mock(return_value=HEALTH)
    status = ServiceStatus()

    assert status.poll(check, now=0)
    for now in (1, 15, 30, 59):
        assert not status.poll(check, now=now)
    assert check.call_count == 1
    assert not status.poll(check, now=60)
    assert check.call_count == 2


def test_lost_connection_disables_actions_and_starts_a_new_retry_window():
    check = Mock(side_effect=[HEALTH, requests.ConnectionError(), HEALTH])
    status = ServiceStatus()

    assert status.poll(check, now=0)
    assert status.poll(check, now=60)
    assert status.health is None
    assert status.waiting_since == 60
    assert not status.timed_out(179)
    assert not status.poll(check, now=74)
    assert status.poll(check, now=75)
    assert status.health == HEALTH


def test_prolonged_outage_shows_failure_and_slows_retries_but_can_recover():
    check = Mock(side_effect=requests.Timeout())
    status = ServiceStatus()

    for now in range(0, 120, 15):
        status.poll(check, now=now)
    assert not status.timed_out(119)
    assert status.timed_out(120)
    attempts = check.call_count
    assert not status.poll(check, now=120)
    assert not status.poll(check, now=164)
    assert check.call_count == attempts
    assert not status.poll(check, now=165)
    assert check.call_count == attempts + 1

    check.side_effect = None
    check.return_value = HEALTH
    assert status.poll(check, now=225)
    assert not status.timed_out(225)


def test_manual_retry_bypasses_backoff_and_restarts_the_two_minute_window():
    check = Mock(side_effect=requests.Timeout())
    status = ServiceStatus()
    status.poll(check, now=0)
    status.poll(check, now=120)
    status.retry()

    status.poll(check, now=121)
    assert check.call_count == 3
    assert not status.timed_out(240)
    assert status.timed_out(241)


def test_each_dashboard_session_has_its_own_connection_state():
    first_session = ServiceStatus()
    second_session = ServiceStatus()
    first_session.poll(Mock(return_value=HEALTH), now=0)

    assert first_session.health == HEALTH
    assert second_session.health is None
    assert second_session.last_checked is None
