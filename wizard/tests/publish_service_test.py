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
