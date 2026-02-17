from wizard.services.publish_service import PublishService


def test_publish_service_persists_jobs_and_manifests(tmp_path):
    repo_root = tmp_path
    service = PublishService(repo_root=repo_root)

    job = service.create_job(source_workspace="memory/vault", provider="wizard")
    manifest_id = job["manifest_id"]

    service_reloaded = PublishService(repo_root=repo_root)
    loaded_job = service_reloaded.get_job(job["publish_job_id"])
    loaded_manifest = service_reloaded.get_manifest(manifest_id)

    assert loaded_job is not None
    assert loaded_job["publish_job_id"] == job["publish_job_id"]
    assert loaded_manifest is not None
    assert loaded_manifest["manifest_id"] == manifest_id


def test_publish_service_provider_availability(tmp_path):
    repo_root = tmp_path
    service = PublishService(repo_root=repo_root)

    capabilities = service.get_capabilities()
    assert capabilities["providers"]["wizard"]["available"] is True
    assert capabilities["providers"]["dev"]["available"] is False
    assert capabilities["providers"]["oc_app"]["available"] is False

    dev_dir = repo_root / "dev"
    dev_dir.mkdir(parents=True, exist_ok=True)
    service_with_dev = PublishService(repo_root=repo_root)
    capabilities_with_dev = service_with_dev.get_capabilities()
    assert capabilities_with_dev["providers"]["dev"]["available"] is True


def test_publish_provider_registry_and_module_gate(tmp_path):
    repo_root = tmp_path
    (repo_root / "sonic").mkdir(parents=True, exist_ok=True)
    service = PublishService(repo_root=repo_root)

    registry = service.get_provider_registry()
    assert registry["sonic"]["module"] == "sonic"
    assert registry["sonic"]["publish_lane"] == "artifact"

    job = service.create_job(source_workspace="sonic/datasets", provider="sonic")
    assert job["module"] == "sonic"
    assert job["publish_lane"] == "artifact"
    assert job["module_gate"]["matched_source_prefix"] == "sonic"

    try:
        service.create_job(source_workspace="memory/vault", provider="sonic")
        assert False, "expected module gate failure"
    except RuntimeError as exc:
        assert "module-aware publish gating blocked" in str(exc)


def test_oc_app_contract_and_render_payload(tmp_path):
    service = PublishService(repo_root=tmp_path)
    contract = service.get_oc_app_contract()
    assert contract["provider"] == "oc_app"
    assert contract["host_contract_version"] == "1.0.0"
    assert contract["render_contract_version"] == "1.0.0"
    assert "oc_app:render" in contract["session_boundary"]["required_scopes"]

    render = service.render_oc_app(
        {
            "contract_version": "1.0.0",
            "content": "# Header",
            "content_type": "markdown",
            "entrypoint": "main",
            "assets": [{"path": "assets/app.js", "media_type": "application/javascript"}],
            "session": {
                "session_id": "sess_1",
                "principal_id": "user_1",
                "token_lease_id": "lease_1",
                "scopes": ["oc_app:render"],
            },
        }
    )
    assert render["provider"] == "oc_app"
    assert render["entrypoint"] == "main"
    assert render["assets_manifest"]["count"] == 1
    assert render["cache"]["html_etag"]
    assert render["session"]["token_lease_validated"] is True
