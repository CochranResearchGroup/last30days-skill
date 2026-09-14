"""Provider-free hotfix control behavior through the public interface."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "dev/last30days/scripts"))

from hotfix_control import GitSnapshotV1, HotfixCaseV1, HotfixController, HotfixError

BASE = "a" * 40


def case(**changes):
    return HotfixCaseV1(
        **{
            "work_item": "WI-007",
            "incident": "fixture-incident-1",
            "reporter": "fixture-operator",
            "observed_at": "2026-09-14T00:00:00+00:00",
            "expected": "fixture returns correct value",
            "observed": "fixture returns incorrect value",
            "evidence": "fixture://regression",
            "production_identity": "fixture-service/v1",
            "impact": "incorrect",
            "surfaces": ("app.py",),
            "overlaps": (),
            "containment": "fixture effects disabled",
            "rollback_commit": BASE,
            "rollback_evidence": "fixture://rollback-ready",
            "non_goals": "No production or provider effects",
            "stop_conditions": "Any effect outside fixture root",
            **changes,
        }
    )


def test_dormant_slot_activates_only_after_qualification_and_owns_no_live_authority():
    controller = HotfixController()
    assert controller.state == "dormant"
    assert controller.resources == ()
    assert controller.live_authority is False
    controller.report(case())
    controller.qualify()
    controller.activate(GitSnapshotV1(main_commit=BASE, remote_commit=BASE, clean=True))
    assert controller.state == "active"
    assert controller.base_commit == BASE
    assert controller.resources == ()
    assert controller.live_authority is False
    assert [entry["state"] for entry in controller.history] == [
        "reported",
        "qualified",
        "active",
    ]


def prepared(*, lanes=(), overlaps=(), reconcile=True):
    """A qualified, reviewed fixture with actual controller transitions."""
    from hotfix_control import (
        FakeRuntimeAdapter,
        HotfixCandidateV1,
        HotfixIntegrationReceiptV1,
        HotfixReconciliationReportV1,
        digest,
    )

    incident = case(overlaps=overlaps)
    controller = HotfixController()
    controller.report(incident)
    controller.qualify()
    controller.activate(
        GitSnapshotV1(main_commit=BASE, remote_commit=BASE, clean=True, lanes=lanes)
    )
    candidate = HotfixCandidateV1(
        case_digest=digest(incident),
        base_commit=BASE,
        head_commit="b" * 40,
        changed_files=("app.py",),
        regression_before="fixture://before",
        regression_after="fixture://after",
        focused_tests=("unit",),
        fallback_tests=("contract",),
        compatibility="fixture-compatible",
        rollback_commit=BASE,
        review="fixture://review",
        blocking_findings=(),
    )
    integration = HotfixIntegrationReceiptV1(
        candidate_digest=digest(candidate),
        base_commit=BASE,
        head_commit="b" * 40,
        merge_commit="c" * 40,
        target_commit="c" * 40,
        priority_review="fixture://review",
        ancestry_verified=True,
    )
    controller.candidate(candidate)
    controller.integrate(integration)
    if reconcile:
        controller.reconcile(
            HotfixReconciliationReportV1(merge_commit="c" * 40, lanes=())
        )
    return controller, FakeRuntimeAdapter(
        integrated_commit="c" * 40, rollback_commit=BASE
    )


def test_failed_verification_preserves_failure_then_allows_one_exact_rollback():
    from dataclasses import replace

    from hotfix_control import HotfixCloseoutReceiptV1, digest

    controller, runtime = prepared()
    controller.stage(runtime.staging())
    controller.authorize(runtime.authorization())
    controller.deploy(runtime.deployment())
    controller.verify(replace(runtime.verification(), ready=False))
    assert controller.state == "verification_failed"
    assert controller.history[-1]["evidence"]["ready"] is False
    with pytest.raises(HotfixError):
        controller.deploy(runtime.deployment())
    controller.rollback(runtime.rollback())
    assert controller.state == "rolled_back"
    with pytest.raises(HotfixError):
        controller.rollback(runtime.rollback())
    with pytest.raises(HotfixError):
        controller.close(
            HotfixCloseoutReceiptV1(
                case_digest=digest(case()),
                outcome="fixed",
                cleanup_verified=True,
                evidence="fixture://wrong",
                residual_risks="defect remains",
            )
        )
    controller.close(
        HotfixCloseoutReceiptV1(
            case_digest=digest(case()),
            outcome="rolled_back",
            cleanup_verified=True,
            evidence="fixture://restored",
            residual_risks="defect remains",
        )
    )
    assert controller.state == "closed"
    assert controller.live_authority is False


@pytest.mark.parametrize(
    "fault",
    [
        "unverified",
        "stale",
        "dirty",
        "second",
        "rollback",
        "overlap",
        "path",
        "boolean",
        "extra",
    ],
)
def test_activation_rejects_ambiguous_or_unsafe_evidence_without_acquiring_resources(
    fault,
):
    controller = HotfixController()
    with pytest.raises(HotfixError):
        supplied_case = case(
            **{
                "unverified": {"impact": "unverified"},
                "rollback": {"rollback_evidence": ""},
                "overlap": {"overlaps": ("unregistered-feature",)},
                "path": {"surfaces": ("../outside.py",)},
            }.get(fault, {})
        )
        if fault == "extra":
            supplied_case = HotfixCaseV1.from_dict(
                {**supplied_case.to_dict(), "deploy": True}
            )
        controller.report(supplied_case)
        controller.qualify()
        controller.activate(
            GitSnapshotV1(
                main_commit=BASE,
                remote_commit="b" * 40 if fault == "stale" else BASE,
                clean=False
                if fault == "dirty"
                else (1 if fault == "boolean" else True),
            )
        )
        if fault == "second":
            controller.report(case(incident="second-incident"))
    assert controller.resources == ()
    assert not controller.live_authority


def test_hotfix_lifecycle_keeps_source_runtime_authority_and_cleanup_proofs_distinct():
    from hotfix_control import (
        FakeRuntimeAdapter,
        FeatureLaneV1,
        HotfixCandidateV1,
        HotfixCloseoutReceiptV1,
        HotfixIntegrationReceiptV1,
        HotfixReconciliationReportV1,
        LaneDispositionV1,
        digest,
    )

    qualified = case(overlaps=("feature",))
    controller = HotfixController()
    controller.report(qualified)
    controller.qualify()
    controller.activate(
        GitSnapshotV1(
            main_commit=BASE,
            remote_commit=BASE,
            clean=True,
            lanes=(
                FeatureLaneV1(
                    lane="feature",
                    head_commit=BASE,
                    remote_commit=BASE,
                    surfaces=("app.py",),
                ),
            ),
        )
    )
    assert controller.conflicts == {"feature": "paused"}
    candidate = HotfixCandidateV1(
        case_digest=digest(qualified),
        base_commit=BASE,
        head_commit="b" * 40,
        changed_files=("app.py",),
        regression_before="fixture://failed-before",
        regression_after="fixture://passed-after",
        focused_tests=("fixture-unit",),
        fallback_tests=("fixture-presubmit",),
        compatibility="fixture compatible",
        rollback_commit=BASE,
        review="fixture accepted",
        blocking_findings=(),
    )
    controller.candidate(candidate)
    controller.integrate(
        HotfixIntegrationReceiptV1(
            candidate_digest=digest(candidate),
            base_commit=BASE,
            head_commit="b" * 40,
            merge_commit="c" * 40,
            target_commit="c" * 40,
            priority_review="fixture://review-1",
            ancestry_verified=True,
        )
    )
    assert controller.state == "integrated"
    controller.reconcile(
        HotfixReconciliationReportV1(
            merge_commit="c" * 40,
            lanes=(
                LaneDispositionV1(
                    lane="feature",
                    disposition="reconciled",
                    old_commit=BASE,
                    new_commit="d" * 40,
                    integrated_commit="c" * 40,
                    validation="fixture://retested",
                ),
            ),
        )
    )
    runtime = FakeRuntimeAdapter(integrated_commit="c" * 40, rollback_commit=BASE)
    controller.stage(runtime.staging())
    assert controller.state == "staging_accepted"
    controller.authorize(runtime.authorization())
    assert controller.state == "deploy_authorized"
    assert controller.live_authority is False
    controller.deploy(runtime.deployment())
    assert controller.state == "deployed"
    controller.verify(runtime.verification())
    assert controller.state == "deployed_verified"
    controller.close(
        HotfixCloseoutReceiptV1(
            case_digest=digest(qualified),
            outcome="fixed",
            cleanup_verified=True,
            evidence="fixture://closed",
            residual_risks="simulated only",
        )
    )
    assert controller.state == "closed"
    assert controller.history[-1]["evidence"]["outcome"] == "fixed"
    assert controller.resources == ()


@pytest.mark.parametrize(
    "action", ["authorize", "deploy", "verify", "rollback", "close"]
)
def test_missing_prerequisite_cannot_be_skipped(action):
    from hotfix_control import HotfixCloseoutReceiptV1, digest

    controller, runtime = prepared()
    receipt = (
        HotfixCloseoutReceiptV1(
            case_digest=digest(case()),
            outcome="fixed",
            cleanup_verified=True,
            evidence="fixture://close",
            residual_risks="fixture",
        )
        if action == "close"
        else getattr(
            runtime,
            {
                "authorize": "authorization",
                "deploy": "deployment",
                "verify": "verification",
                "rollback": "rollback",
            }[action],
        )()
    )
    before = controller.history
    with pytest.raises(HotfixError, match="transition_denied"):
        getattr(controller, action)(receipt)
    assert controller.history == before


def test_bad_artifact_cleanup_and_rollback_failure_are_terminally_visible():
    from dataclasses import replace

    from hotfix_control import HotfixCloseoutReceiptV1, digest

    controller, runtime = prepared()
    controller.stage(runtime.staging())
    with pytest.raises(HotfixError, match="authorization_mismatch"):
        controller.authorize(replace(runtime.authorization(), artifact_digest="0" * 64))
    controller.authorize(runtime.authorization())
    controller.deploy(runtime.deployment())
    controller.rollback(replace(runtime.rollback(), ready=False))
    assert controller.state == "blocked"
    with pytest.raises(HotfixError):
        controller.rollback(runtime.rollback())
    with pytest.raises(HotfixError):
        controller.close(
            HotfixCloseoutReceiptV1(
                case_digest=digest(case()),
                outcome="blocked",
                cleanup_verified=False,
                evidence="fixture://failed",
                residual_risks="restore failed",
            )
        )
    controller.close(
        HotfixCloseoutReceiptV1(
            case_digest=digest(case()),
            outcome="blocked",
            cleanup_verified=True,
            evidence="fixture://cleanup",
            residual_risks="restore failed",
        )
    )
    assert controller.state == "closed"


@pytest.mark.parametrize("state", ["cancelled", "blocked"])
def test_explicit_disposition_retains_evidence_and_never_claims_a_fix(state):
    from hotfix_control import HotfixCloseoutReceiptV1, digest

    controller = HotfixController()
    controller.report(case())
    controller.stop(state, "fixture://bounded-disposition")
    assert controller.state == state
    controller.close(
        HotfixCloseoutReceiptV1(
            case_digest=digest(case()),
            outcome=state,
            cleanup_verified=True,
            evidence="fixture://cleanup",
            residual_risks="unfixed",
        )
    )
    assert controller.state == "closed"


@pytest.mark.parametrize(
    "fault", ["missing", "unaffected", "stale", "duplicate", "empty_validation"]
)
def test_every_registered_overlap_requires_an_attributable_disposition(fault):
    from hotfix_control import (
        FeatureLaneV1,
        HotfixReconciliationReportV1,
        LaneDispositionV1,
    )

    lane = FeatureLaneV1(
        lane="feature", head_commit=BASE, remote_commit=BASE, surfaces=("app.py",)
    )
    controller, runtime = prepared(
        lanes=(lane,), overlaps=("feature",), reconcile=False
    )
    before = controller.history
    with pytest.raises(HotfixError):
        disposition = LaneDispositionV1(
            lane="feature",
            disposition="unaffected" if fault == "unaffected" else "paused",
            old_commit="e" * 40 if fault == "stale" else BASE,
            new_commit=BASE,
            integrated_commit="c" * 40,
            validation="" if fault == "empty_validation" else "fixture://pause",
        )
        controller.reconcile(
            HotfixReconciliationReportV1(
                merge_commit="c" * 40,
                lanes=()
                if fault == "missing"
                else (
                    (disposition, disposition)
                    if fault == "duplicate"
                    else (disposition,)
                ),
            )
        )
    assert controller.history == before
    with pytest.raises(HotfixError, match="missing_reconciliation"):
        controller.stage(runtime.staging())


def test_strict_records_round_trip_without_coercion_or_mutable_history_aliases():
    from hotfix_control import FeatureLaneV1

    snapshot = GitSnapshotV1(
        main_commit=BASE,
        remote_commit=BASE,
        clean=True,
        lanes=(
            FeatureLaneV1(
                lane="feature",
                head_commit=BASE,
                remote_commit=BASE,
                surfaces=("app.py",),
            ),
        ),
    )
    assert GitSnapshotV1.from_dict(snapshot.to_dict()) == snapshot
    data = snapshot.to_dict()
    data["lanes"][0]["undeclared_authority"] = True
    with pytest.raises(HotfixError):
        GitSnapshotV1.from_dict(data)
    controller, _ = prepared()
    history = controller.history
    history[-1]["evidence"]["mode"] = "live"
    assert controller.history[-1]["evidence"]["mode"] == "drill"


def test_fake_review_rejects_failing_regression_and_non_drill_evidence():
    from hotfix_control import FakeGitAdapter, FakeReviewAdapter

    incident = case()
    snapshot = GitSnapshotV1(main_commit=BASE, remote_commit=BASE, clean=True)
    assert FakeGitAdapter(snapshot).snapshot() == snapshot
    review = FakeReviewAdapter()
    with pytest.raises(HotfixError, match="regression_failed"):
        review.candidate(
            incident,
            snapshot,
            head_commit="b" * 40,
            changed_files=("app.py",),
            regression_passed=False,
        )
    candidate = review.candidate(
        incident,
        snapshot,
        head_commit="b" * 40,
        changed_files=("app.py",),
        regression_passed=True,
    )
    controller = HotfixController()
    controller.report(incident)
    controller.qualify()
    controller.activate(snapshot)
    controller.candidate(candidate)
    assert controller.state == "fix_ready"
    with pytest.raises(HotfixError):
        type(candidate).from_dict({**candidate.to_dict(), "mode": "live"})


@pytest.mark.parametrize(
    "features,hotfixes,accepted", [(3, 0, True), (4, 0, False), (0, 1, False)]
)
def test_reserved_hotfix_never_increases_feature_wip_or_duplicates_an_existing_slot(
    features, hotfixes, accepted
):
    from hotfix_control import FeatureLaneV1

    lanes = tuple(
        FeatureLaneV1(
            lane=f"lane-{index}",
            head_commit=BASE,
            remote_commit=BASE,
            surfaces=(f"independent-{index}.py",),
        )
        for index in range(features)
    )
    controller = HotfixController()
    controller.report(case())
    controller.qualify()
    snapshot = GitSnapshotV1(
        main_commit=BASE,
        remote_commit=BASE,
        clean=True,
        lanes=lanes,
        active_hotfixes=hotfixes,
    )
    if accepted:
        controller.activate(snapshot)
        assert controller.feature_wip == features
        assert controller.state == "active"
    else:
        with pytest.raises(
            HotfixError, match="feature_wip_exceeded|hotfix_slot_occupied"
        ):
            controller.activate(snapshot)
        assert controller.state == "qualified"


def test_empty_validation_names_cannot_claim_candidate_readiness():
    from dataclasses import replace

    from hotfix_control import FakeReviewAdapter

    snapshot = GitSnapshotV1(main_commit=BASE, remote_commit=BASE, clean=True)
    candidate = FakeReviewAdapter().candidate(
        case(),
        snapshot,
        head_commit="b" * 40,
        changed_files=("app.py",),
        regression_passed=True,
    )
    with pytest.raises(HotfixError, match="invalid_text"):
        replace(candidate, focused_tests=(" ",))
