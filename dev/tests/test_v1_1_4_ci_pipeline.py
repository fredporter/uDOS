"""
uDOS v1.1.4.4 - Continuous Integration Pipeline Test Suite

Tests automated CI/CD pipelines for multi-platform testing, builds, and deployment.
Validates GitHub Actions workflows, build automation, and deployment processes.

Test Coverage:
- GitHub Actions Configuration (8 tests)
- Test Automation (9 tests)
- Multi-Platform Builds (10 tests)
- Deployment Pipelines (8 tests)
- Quality Gates (7 tests)
- Monitoring Integration (6 tests)
"""

import unittest
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum


# ============================================================================
# CI/CD CONFIGURATION
# ============================================================================

class PipelineStatus(Enum):
    """Pipeline execution status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    SKIPPED = "skipped"


class Platform(Enum):
    """Build platforms"""
    MACOS = "macos"
    WINDOWS = "windows"
    LINUX = "linux"
    IOS = "ios"
    ANDROID = "android"
    WEB = "web"


class DeploymentEnvironment(Enum):
    """Deployment environments"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


@dataclass
class GitHubActionsWorkflow:
    """GitHub Actions workflow configuration"""
    name: str
    triggers: List[str]
    jobs: Dict[str, Dict[str, Any]]
    workflow_file: str
    enabled: bool = True

    def validate(self) -> List[str]:
        """Validate workflow configuration"""
        errors = []

        if not self.name:
            errors.append("Workflow name is required")

        if not self.triggers:
            errors.append("At least one trigger required")

        if not self.jobs:
            errors.append("At least one job required")

        for job_name, job_config in self.jobs.items():
            if "runs-on" not in job_config:
                errors.append(f"Job '{job_name}' missing 'runs-on'")

            if "steps" not in job_config:
                errors.append(f"Job '{job_name}' missing 'steps'")

        return errors

    def to_yaml(self) -> str:
        """Generate YAML workflow file"""
        # Simple YAML generation without external library
        yaml_lines = [f"name: {self.name}", ""]

        # Triggers
        yaml_lines.append("on:")
        for trigger in self.triggers:
            yaml_lines.append(f"  - {trigger}")
        yaml_lines.append("")

        # Jobs
        yaml_lines.append("jobs:")
        for job_name, job_config in self.jobs.items():
            yaml_lines.append(f"  {job_name}:")
            yaml_lines.append(f"    runs-on: {job_config.get('runs-on', 'ubuntu-latest')}")
            yaml_lines.append("    steps:")
            for step in job_config.get('steps', []):
                if 'name' in step:
                    yaml_lines.append(f"      - name: {step['name']}")
                if 'uses' in step:
                    yaml_lines.append(f"        uses: {step['uses']}")
                if 'run' in step:
                    yaml_lines.append(f"        run: {step['run']}")

        return "\n".join(yaml_lines)


class CIConfiguration:
    """CI/CD pipeline configuration manager"""

    def __init__(self):
        self.workflows: Dict[str, GitHubActionsWorkflow] = {}
        self.secrets: Set[str] = set()
        self.environments: Dict[str, Dict[str, Any]] = {}

    def add_workflow(self, workflow: GitHubActionsWorkflow) -> bool:
        """Add workflow to configuration"""
        errors = workflow.validate()
        if errors:
            return False

        self.workflows[workflow.name] = workflow
        return True

    def add_secret(self, secret_name: str) -> None:
        """Register required secret"""
        self.secrets.add(secret_name)

    def configure_environment(
        self,
        env_name: str,
        url: str,
        protection_rules: Optional[Dict[str, Any]] = None
    ) -> None:
        """Configure deployment environment"""
        self.environments[env_name] = {
            "url": url,
            "protection_rules": protection_rules or {},
            "created_at": datetime.now()
        }

    def get_workflow(self, name: str) -> Optional[GitHubActionsWorkflow]:
        """Get workflow by name"""
        return self.workflows.get(name)

    def list_required_secrets(self) -> List[str]:
        """List all required secrets"""
        return sorted(list(self.secrets))


# ============================================================================
# TEST AUTOMATION
# ============================================================================

@dataclass
class TestJob:
    """Automated test job configuration"""
    job_id: str
    platform: Platform
    python_version: str
    test_files: List[str]
    parallel: bool = True
    timeout_minutes: int = 30
    coverage: bool = True

    def get_matrix_config(self) -> Dict[str, Any]:
        """Get test matrix configuration"""
        return {
            "platform": self.platform.value,
            "python-version": self.python_version,
            "test-files": self.test_files
        }


class TestAutomation:
    """Automated testing system"""

    def __init__(self):
        self.test_jobs: List[TestJob] = []
        self.coverage_threshold = 80.0  # Minimum 80% coverage
        self.test_results: Dict[str, Dict[str, Any]] = {}

    def add_test_job(self, job: TestJob) -> str:
        """Add test job to automation"""
        self.test_jobs.append(job)
        return job.job_id

    def execute_tests(
        self,
        job_id: str,
        parallel_workers: int = 4
    ) -> Dict[str, Any]:
        """Execute test job"""
        job = next((j for j in self.test_jobs if j.job_id == job_id), None)
        if not job:
            return {"success": False, "error": "Job not found"}

        # Simulate test execution
        result = {
            "success": True,
            "job_id": job_id,
            "platform": job.platform.value,
            "python_version": job.python_version,
            "tests_run": len(job.test_files) * 10,  # Simulate 10 tests per file
            "tests_passed": len(job.test_files) * 10,
            "tests_failed": 0,
            "duration_seconds": 5.0,
            "coverage_percent": 95.0 if job.coverage else None,
            "parallel_workers": parallel_workers if job.parallel else 1,
            "status": "success"
        }

        self.test_results[job_id] = result
        return result

    def get_coverage_report(self) -> Dict[str, float]:
        """Get coverage report across all jobs"""
        coverage_data = {}

        for job_id, result in self.test_results.items():
            if result.get("coverage_percent"):
                coverage_data[job_id] = result["coverage_percent"]

        return coverage_data

    def check_coverage_threshold(self) -> bool:
        """Check if coverage meets threshold"""
        coverage = self.get_coverage_report()
        if not coverage:
            return False

        avg_coverage = sum(coverage.values()) / len(coverage)
        return avg_coverage >= self.coverage_threshold

    def generate_test_matrix(self) -> List[Dict[str, Any]]:
        """Generate test matrix for CI"""
        matrix = []

        for job in self.test_jobs:
            matrix.append(job.get_matrix_config())

        return matrix


# ============================================================================
# BUILD AUTOMATION
# ============================================================================

@dataclass
class BuildArtifact:
    """Build artifact metadata"""
    artifact_id: str
    platform: Platform
    version: str
    build_number: int
    file_path: str
    file_size_mb: float
    checksum: str
    created_at: datetime = field(default_factory=datetime.now)


class BuildPipeline:
    """Multi-platform build automation"""

    def __init__(self):
        self.builds: Dict[str, BuildArtifact] = {}
        self.build_queue: List[Dict[str, Any]] = []
        self.version = "1.1.4"
        self.build_counter = 0

    def queue_build(
        self,
        platform: Platform,
        version: Optional[str] = None,
        release: bool = False
    ) -> str:
        """Queue build for platform"""
        build_id = f"build_{self.build_counter}"
        self.build_counter += 1

        self.build_queue.append({
            "build_id": build_id,
            "platform": platform,
            "version": version or self.version,
            "release": release,
            "queued_at": datetime.now()
        })

        return build_id

    def execute_build(self, build_id: str) -> BuildArtifact:
        """Execute queued build"""
        build_config = next(
            (b for b in self.build_queue if b["build_id"] == build_id),
            None
        )

        if not build_config:
            raise ValueError(f"Build {build_id} not found in queue")

        platform = build_config["platform"]
        version = build_config["version"]

        # Generate artifact
        artifact = BuildArtifact(
            artifact_id=build_id,
            platform=platform,
            version=version,
            build_number=self.build_counter,
            file_path=self._get_artifact_path(platform, version),
            file_size_mb=self._get_artifact_size(platform),
            checksum=f"sha256_{build_id}"
        )

        self.builds[build_id] = artifact

        # Remove from queue
        self.build_queue = [b for b in self.build_queue if b["build_id"] != build_id]

        return artifact

    def _get_artifact_path(self, platform: Platform, version: str) -> str:
        """Get artifact file path"""
        extensions = {
            Platform.MACOS: "dmg",
            Platform.WINDOWS: "exe",
            Platform.LINUX: "AppImage",
            Platform.IOS: "ipa",
            Platform.ANDROID: "apk",
            Platform.WEB: "tar.gz"
        }

        ext = extensions.get(platform, "zip")
        return f"dist/uDOS-{version}-{platform.value}.{ext}"

    def _get_artifact_size(self, platform: Platform) -> float:
        """Get estimated artifact size in MB"""
        sizes = {
            Platform.MACOS: 50.0,
            Platform.WINDOWS: 45.0,
            Platform.LINUX: 40.0,
            Platform.IOS: 30.0,
            Platform.ANDROID: 25.0,
            Platform.WEB: 10.0
        }
        return sizes.get(platform, 35.0)

    def get_build_status(self, build_id: str) -> str:
        """Get build status"""
        if build_id in self.builds:
            return "completed"
        elif any(b["build_id"] == build_id for b in self.build_queue):
            return "queued"
        else:
            return "not_found"

    def list_artifacts(self, platform: Optional[Platform] = None) -> List[BuildArtifact]:
        """List build artifacts"""
        artifacts = list(self.builds.values())

        if platform:
            artifacts = [a for a in artifacts if a.platform == platform]

        return sorted(artifacts, key=lambda a: a.created_at, reverse=True)


# ============================================================================
# DEPLOYMENT AUTOMATION
# ============================================================================

@dataclass
class Deployment:
    """Deployment record"""
    deployment_id: str
    environment: DeploymentEnvironment
    version: str
    artifact_id: str
    status: PipelineStatus
    deployed_at: Optional[datetime] = None
    deployed_by: str = "ci-pipeline"
    rollback_id: Optional[str] = None


class DeploymentPipeline:
    """Automated deployment management"""

    def __init__(self):
        self.deployments: Dict[str, Deployment] = {}
        self.active_deployments: Dict[str, str] = {}  # env -> deployment_id
        self.deployment_counter = 0

    def deploy(
        self,
        environment: DeploymentEnvironment,
        artifact_id: str,
        version: str,
        auto_rollback: bool = True
    ) -> Deployment:
        """Deploy artifact to environment"""
        deployment_id = f"deploy_{self.deployment_counter}"
        self.deployment_counter += 1

        # Check if there's an active deployment to potentially rollback to
        rollback_id = self.active_deployments.get(environment.value)

        deployment = Deployment(
            deployment_id=deployment_id,
            environment=environment,
            version=version,
            artifact_id=artifact_id,
            status=PipelineStatus.SUCCESS,
            deployed_at=datetime.now(),
            rollback_id=rollback_id
        )

        self.deployments[deployment_id] = deployment
        self.active_deployments[environment.value] = deployment_id

        return deployment

    def rollback(self, environment: DeploymentEnvironment) -> Optional[Deployment]:
        """Rollback to previous deployment"""
        current_deployment_id = self.active_deployments.get(environment.value)
        if not current_deployment_id:
            return None

        current = self.deployments.get(current_deployment_id)
        if not current or not current.rollback_id:
            return None

        # Mark current as rolled back
        current.status = PipelineStatus.CANCELLED

        # Restore previous
        previous = self.deployments.get(current.rollback_id)
        if previous:
            previous.status = PipelineStatus.SUCCESS
            self.active_deployments[environment.value] = current.rollback_id

        return previous

    def get_active_deployment(
        self,
        environment: DeploymentEnvironment
    ) -> Optional[Deployment]:
        """Get currently active deployment"""
        deployment_id = self.active_deployments.get(environment.value)
        if deployment_id:
            return self.deployments.get(deployment_id)
        return None

    def get_deployment_history(
        self,
        environment: DeploymentEnvironment,
        limit: int = 10
    ) -> List[Deployment]:
        """Get deployment history for environment"""
        deployments = [
            d for d in self.deployments.values()
            if d.environment == environment
        ]

        deployments.sort(key=lambda d: d.deployed_at or datetime.min, reverse=True)
        return deployments[:limit]

    def health_check(self, deployment_id: str) -> Dict[str, Any]:
        """Perform health check on deployment"""
        deployment = self.deployments.get(deployment_id)
        if not deployment:
            return {"healthy": False, "error": "Deployment not found"}

        # Simulate health check
        return {
            "healthy": True,
            "deployment_id": deployment_id,
            "environment": deployment.environment.value,
            "version": deployment.version,
            "uptime_seconds": 3600,
            "response_time_ms": 50,
            "error_rate": 0.0
        }


# ============================================================================
# QUALITY GATES
# ============================================================================

@dataclass
class QualityCheck:
    """Quality gate check"""
    check_name: str
    check_type: str  # lint, security, performance, compliance
    status: PipelineStatus
    score: float  # 0-100
    threshold: float
    details: Dict[str, Any] = field(default_factory=dict)


class QualityGates:
    """Quality gate enforcement"""

    def __init__(self):
        self.checks: List[QualityCheck] = []
        self.passing_threshold = 80.0

    def run_linting(self, files: List[str]) -> QualityCheck:
        """Run code linting checks"""
        check = QualityCheck(
            check_name="Code Linting",
            check_type="lint",
            status=PipelineStatus.SUCCESS,
            score=95.0,
            threshold=self.passing_threshold,
            details={
                "files_checked": len(files),
                "issues_found": 2,
                "issues_fixed": 2
            }
        )

        self.checks.append(check)
        return check

    def run_security_scan(self, dependencies: List[str]) -> QualityCheck:
        """Run security vulnerability scan"""
        check = QualityCheck(
            check_name="Security Scan",
            check_type="security",
            status=PipelineStatus.SUCCESS,
            score=100.0,
            threshold=100.0,  # No vulnerabilities allowed
            details={
                "dependencies_scanned": len(dependencies),
                "vulnerabilities_found": 0,
                "severity_critical": 0,
                "severity_high": 0,
                "severity_medium": 0
            }
        )

        self.checks.append(check)
        return check

    def run_performance_benchmark(self, test_suite: str) -> QualityCheck:
        """Run performance benchmarks"""
        check = QualityCheck(
            check_name="Performance Benchmark",
            check_type="performance",
            status=PipelineStatus.SUCCESS,
            score=92.0,
            threshold=85.0,
            details={
                "test_suite": test_suite,
                "avg_response_time_ms": 45,
                "p95_response_time_ms": 120,
                "throughput_rps": 1000,
                "memory_usage_mb": 150
            }
        )

        self.checks.append(check)
        return check

    def run_compliance_check(self, standards: List[str]) -> QualityCheck:
        """Run compliance validation"""
        check = QualityCheck(
            check_name="Compliance Check",
            check_type="compliance",
            status=PipelineStatus.SUCCESS,
            score=100.0,
            threshold=100.0,
            details={
                "standards_checked": standards,
                "compliant": True,
                "violations": []
            }
        )

        self.checks.append(check)
        return check

    def evaluate_gates(self) -> bool:
        """Evaluate if all quality gates pass"""
        if not self.checks:
            return False

        for check in self.checks:
            if check.score < check.threshold:
                return False

            if check.status == PipelineStatus.FAILED:
                return False

        return True

    def get_quality_report(self) -> Dict[str, Any]:
        """Generate quality report"""
        return {
            "total_checks": len(self.checks),
            "passed_checks": sum(1 for c in self.checks if c.score >= c.threshold),
            "failed_checks": sum(1 for c in self.checks if c.score < c.threshold),
            "average_score": sum(c.score for c in self.checks) / len(self.checks) if self.checks else 0,
            "all_gates_passed": self.evaluate_gates(),
            "checks": [
                {
                    "name": c.check_name,
                    "type": c.check_type,
                    "score": c.score,
                    "threshold": c.threshold,
                    "passed": c.score >= c.threshold
                }
                for c in self.checks
            ]
        }


# ============================================================================
# MONITORING & NOTIFICATIONS
# ============================================================================

@dataclass
class PipelineMetric:
    """Pipeline performance metric"""
    metric_name: str
    value: float
    unit: str
    timestamp: datetime = field(default_factory=datetime.now)
    tags: Dict[str, str] = field(default_factory=dict)


class MonitoringIntegration:
    """Pipeline monitoring and alerting"""

    def __init__(self):
        self.metrics: List[PipelineMetric] = []
        self.notifications: List[Dict[str, Any]] = []
        self.alert_channels = ["slack", "email"]

    def record_metric(
        self,
        metric_name: str,
        value: float,
        unit: str,
        tags: Optional[Dict[str, str]] = None
    ) -> None:
        """Record pipeline metric"""
        metric = PipelineMetric(
            metric_name=metric_name,
            value=value,
            unit=unit,
            tags=tags or {}
        )

        self.metrics.append(metric)

    def send_notification(
        self,
        title: str,
        message: str,
        severity: str,  # info, warning, error
        channels: Optional[List[str]] = None
    ) -> None:
        """Send notification to configured channels"""
        notification = {
            "title": title,
            "message": message,
            "severity": severity,
            "channels": channels or self.alert_channels,
            "sent_at": datetime.now()
        }

        self.notifications.append(notification)

    def get_metric_stats(self, metric_name: str) -> Dict[str, float]:
        """Get statistics for a metric"""
        values = [
            m.value for m in self.metrics
            if m.metric_name == metric_name
        ]

        if not values:
            return {}

        return {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values),
            "latest": values[-1]
        }

    def get_build_trends(self, days: int = 7) -> Dict[str, Any]:
        """Get build trend analysis"""
        cutoff = datetime.now() - timedelta(days=days)

        recent_builds = [
            m for m in self.metrics
            if m.metric_name == "build_duration" and m.timestamp >= cutoff
        ]

        return {
            "period_days": days,
            "total_builds": len(recent_builds),
            "avg_duration": sum(m.value for m in recent_builds) / len(recent_builds) if recent_builds else 0,
            "success_rate": 0.98  # Simulated
        }

    def check_alerts(self) -> List[Dict[str, Any]]:
        """Check for alert conditions"""
        alerts = []

        # Check build duration
        build_stats = self.get_metric_stats("build_duration")
        if build_stats and build_stats.get("latest", 0) > 600:  # 10 minutes
            alerts.append({
                "type": "build_duration",
                "severity": "warning",
                "message": f"Build taking longer than expected: {build_stats['latest']}s"
            })

        # Check test failures
        test_stats = self.get_metric_stats("test_failures")
        if test_stats and test_stats.get("latest", 0) > 0:
            alerts.append({
                "type": "test_failures",
                "severity": "error",
                "message": f"Tests failing: {test_stats['latest']} failures"
            })

        return alerts


# ============================================================================
# TEST SUITES
# ============================================================================

class TestGitHubActions(unittest.TestCase):
    """Test GitHub Actions workflow configuration"""

    def setUp(self):
        self.ci_config = CIConfiguration()

    def test_create_workflow(self):
        """Test workflow creation"""
        workflow = GitHubActionsWorkflow(
            name="Test Suite",
            triggers=["push", "pull_request"],
            jobs={
                "test": {
                    "runs-on": "ubuntu-latest",
                    "steps": [
                        {"name": "Checkout", "uses": "actions/checkout@v3"},
                        {"name": "Run tests", "run": "pytest"}
                    ]
                }
            },
            workflow_file=".github/workflows/test.yml"
        )

        self.assertEqual(workflow.name, "Test Suite")
        self.assertIn("push", workflow.triggers)

    def test_workflow_validation(self):
        """Test workflow validation"""
        workflow = GitHubActionsWorkflow(
            name="Invalid",
            triggers=["push"],
            jobs={
                "test": {
                    "steps": []  # Missing runs-on
                }
            },
            workflow_file="test.yml"
        )

        errors = workflow.validate()
        self.assertGreater(len(errors), 0)

    def test_add_workflow_to_config(self):
        """Test adding workflow to configuration"""
        workflow = GitHubActionsWorkflow(
            name="Build",
            triggers=["push"],
            jobs={
                "build": {
                    "runs-on": "ubuntu-latest",
                    "steps": [{"name": "Build", "run": "make"}]
                }
            },
            workflow_file="build.yml"
        )

        success = self.ci_config.add_workflow(workflow)
        self.assertTrue(success)
        self.assertIn("Build", self.ci_config.workflows)

    def test_register_secrets(self):
        """Test secret registration"""
        self.ci_config.add_secret("DEPLOY_KEY")
        self.ci_config.add_secret("API_TOKEN")

        secrets = self.ci_config.list_required_secrets()
        self.assertEqual(len(secrets), 2)
        self.assertIn("DEPLOY_KEY", secrets)

    def test_configure_environment(self):
        """Test environment configuration"""
        self.ci_config.configure_environment(
            "production",
            url="https://udos.app",
            protection_rules={"required_reviewers": 2}
        )

        self.assertIn("production", self.ci_config.environments)
        env = self.ci_config.environments["production"]
        self.assertEqual(env["url"], "https://udos.app")

    def test_workflow_yaml_generation(self):
        """Test YAML generation"""
        workflow = GitHubActionsWorkflow(
            name="Test",
            triggers=["push"],
            jobs={
                "test": {
                    "runs-on": "ubuntu-latest",
                    "steps": []
                }
            },
            workflow_file="test.yml"
        )

        yaml_content = workflow.to_yaml()
        self.assertIn("name: Test", yaml_content)
        self.assertIn("runs-on: ubuntu-latest", yaml_content)

    def test_get_workflow(self):
        """Test retrieving workflow"""
        workflow = GitHubActionsWorkflow(
            name="Deploy",
            triggers=["release"],
            jobs={"deploy": {"runs-on": "ubuntu-latest", "steps": []}},
            workflow_file="deploy.yml"
        )

        self.ci_config.add_workflow(workflow)
        retrieved = self.ci_config.get_workflow("Deploy")

        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.name, "Deploy")

    def test_workflow_triggers(self):
        """Test workflow trigger configuration"""
        workflow = GitHubActionsWorkflow(
            name="Multi-Trigger",
            triggers=["push", "pull_request", "schedule"],
            jobs={"test": {"runs-on": "ubuntu-latest", "steps": []}},
            workflow_file="multi.yml"
        )

        self.assertEqual(len(workflow.triggers), 3)
        self.assertIn("schedule", workflow.triggers)


class TestTestAutomation(unittest.TestCase):
    """Test automated testing system"""

    def setUp(self):
        self.automation = TestAutomation()

    def test_add_test_job(self):
        """Test adding test job"""
        job = TestJob(
            job_id="test_linux",
            platform=Platform.LINUX,
            python_version="3.9",
            test_files=["test_core.py", "test_gui.py"]
        )

        job_id = self.automation.add_test_job(job)
        self.assertEqual(job_id, "test_linux")

    def test_execute_tests(self):
        """Test executing test job"""
        job = TestJob(
            job_id="test_macos",
            platform=Platform.MACOS,
            python_version="3.10",
            test_files=["test_v1.py"]
        )

        self.automation.add_test_job(job)
        result = self.automation.execute_tests("test_macos")

        self.assertTrue(result["success"] is not False)
        self.assertEqual(result["platform"], "macos")

    def test_parallel_execution(self):
        """Test parallel test execution"""
        job = TestJob(
            job_id="test_parallel",
            platform=Platform.LINUX,
            python_version="3.9",
            test_files=["test1.py", "test2.py", "test3.py"],
            parallel=True
        )

        self.automation.add_test_job(job)
        result = self.automation.execute_tests("test_parallel", parallel_workers=4)

        self.assertEqual(result["parallel_workers"], 4)

    def test_coverage_reporting(self):
        """Test coverage report generation"""
        job1 = TestJob("job1", Platform.LINUX, "3.9", ["test.py"], coverage=True)
        job2 = TestJob("job2", Platform.MACOS, "3.10", ["test.py"], coverage=True)

        self.automation.add_test_job(job1)
        self.automation.add_test_job(job2)

        self.automation.execute_tests("job1")
        self.automation.execute_tests("job2")

        coverage = self.automation.get_coverage_report()
        self.assertEqual(len(coverage), 2)

    def test_coverage_threshold(self):
        """Test coverage threshold checking"""
        job = TestJob("job1", Platform.LINUX, "3.9", ["test.py"], coverage=True)
        self.automation.add_test_job(job)
        self.automation.execute_tests("job1")

        passes_threshold = self.automation.check_coverage_threshold()
        self.assertTrue(passes_threshold)

    def test_generate_test_matrix(self):
        """Test generating test matrix"""
        job1 = TestJob("linux_py39", Platform.LINUX, "3.9", ["test.py"])
        job2 = TestJob("macos_py310", Platform.MACOS, "3.10", ["test.py"])

        self.automation.add_test_job(job1)
        self.automation.add_test_job(job2)

        matrix = self.automation.generate_test_matrix()
        self.assertEqual(len(matrix), 2)

    def test_test_timeout(self):
        """Test timeout configuration"""
        job = TestJob(
            "timeout_test",
            Platform.LINUX,
            "3.9",
            ["test.py"],
            timeout_minutes=45
        )

        self.assertEqual(job.timeout_minutes, 45)

    def test_matrix_config_generation(self):
        """Test matrix configuration"""
        job = TestJob(
            "matrix_test",
            Platform.WINDOWS,
            "3.11",
            ["test1.py", "test2.py"]
        )

        config = job.get_matrix_config()
        self.assertEqual(config["platform"], "windows")
        self.assertEqual(config["python-version"], "3.11")

    def test_test_results_storage(self):
        """Test storing test results"""
        job = TestJob("result_test", Platform.LINUX, "3.9", ["test.py"])
        self.automation.add_test_job(job)

        self.automation.execute_tests("result_test")

        self.assertIn("result_test", self.automation.test_results)


class TestBuildPipeline(unittest.TestCase):
    """Test build automation"""

    def setUp(self):
        self.pipeline = BuildPipeline()

    def test_queue_build(self):
        """Test queueing build"""
        build_id = self.pipeline.queue_build(Platform.MACOS)

        self.assertIn(build_id, [b["build_id"] for b in self.pipeline.build_queue])

    def test_execute_build(self):
        """Test executing build"""
        build_id = self.pipeline.queue_build(Platform.LINUX)
        artifact = self.pipeline.execute_build(build_id)

        self.assertEqual(artifact.platform, Platform.LINUX)
        self.assertIn(build_id, self.pipeline.builds)

    def test_build_artifacts(self):
        """Test build artifact generation"""
        build_id = self.pipeline.queue_build(Platform.WINDOWS, version="1.2.0")
        artifact = self.pipeline.execute_build(build_id)

        self.assertEqual(artifact.version, "1.2.0")
        self.assertIn(".exe", artifact.file_path)

    def test_multiple_platform_builds(self):
        """Test building for multiple platforms"""
        macos_id = self.pipeline.queue_build(Platform.MACOS)
        windows_id = self.pipeline.queue_build(Platform.WINDOWS)
        linux_id = self.pipeline.queue_build(Platform.LINUX)

        self.pipeline.execute_build(macos_id)
        self.pipeline.execute_build(windows_id)
        self.pipeline.execute_build(linux_id)

        self.assertEqual(len(self.pipeline.builds), 3)

    def test_build_status_tracking(self):
        """Test build status"""
        build_id = self.pipeline.queue_build(Platform.IOS)

        status = self.pipeline.get_build_status(build_id)
        self.assertEqual(status, "queued")

        self.pipeline.execute_build(build_id)
        status = self.pipeline.get_build_status(build_id)
        self.assertEqual(status, "completed")

    def test_list_artifacts(self):
        """Test listing artifacts"""
        self.pipeline.queue_build(Platform.MACOS)
        self.pipeline.queue_build(Platform.LINUX)

        build_ids = [b["build_id"] for b in self.pipeline.build_queue]
        for bid in build_ids:
            self.pipeline.execute_build(bid)

        artifacts = self.pipeline.list_artifacts()
        self.assertEqual(len(artifacts), 2)

    def test_platform_specific_artifacts(self):
        """Test filtering artifacts by platform"""
        mac_id = self.pipeline.queue_build(Platform.MACOS)
        win_id = self.pipeline.queue_build(Platform.WINDOWS)

        self.pipeline.execute_build(mac_id)
        self.pipeline.execute_build(win_id)

        mac_artifacts = self.pipeline.list_artifacts(Platform.MACOS)
        self.assertEqual(len(mac_artifacts), 1)
        self.assertEqual(mac_artifacts[0].platform, Platform.MACOS)

    def test_artifact_checksums(self):
        """Test artifact checksum generation"""
        build_id = self.pipeline.queue_build(Platform.ANDROID)
        artifact = self.pipeline.execute_build(build_id)

        self.assertTrue(artifact.checksum.startswith("sha256_"))

    def test_artifact_file_sizes(self):
        """Test artifact size estimation"""
        ios_id = self.pipeline.queue_build(Platform.IOS)
        android_id = self.pipeline.queue_build(Platform.ANDROID)

        ios_artifact = self.pipeline.execute_build(ios_id)
        android_artifact = self.pipeline.execute_build(android_id)

        self.assertGreater(ios_artifact.file_size_mb, 0)
        self.assertGreater(android_artifact.file_size_mb, 0)

    def test_release_builds(self):
        """Test release build configuration"""
        build_id = self.pipeline.queue_build(
            Platform.MACOS,
            version="2.0.0",
            release=True
        )

        build_config = next(b for b in self.pipeline.build_queue if b["build_id"] == build_id)
        self.assertTrue(build_config["release"])


class TestDeploymentPipeline(unittest.TestCase):
    """Test deployment automation"""

    def setUp(self):
        self.deployment = DeploymentPipeline()

    def test_deploy_to_staging(self):
        """Test deploying to staging"""
        deployment = self.deployment.deploy(
            DeploymentEnvironment.STAGING,
            artifact_id="build_123",
            version="1.1.4"
        )

        self.assertEqual(deployment.environment, DeploymentEnvironment.STAGING)
        self.assertEqual(deployment.version, "1.1.4")

    def test_deploy_to_production(self):
        """Test deploying to production"""
        deployment = self.deployment.deploy(
            DeploymentEnvironment.PRODUCTION,
            artifact_id="build_456",
            version="1.1.4"
        )

        self.assertEqual(deployment.status, PipelineStatus.SUCCESS)

    def test_rollback_deployment(self):
        """Test deployment rollback"""
        # First deployment
        self.deployment.deploy(
            DeploymentEnvironment.PRODUCTION,
            artifact_id="build_v1",
            version="1.0.0"
        )

        # Second deployment
        self.deployment.deploy(
            DeploymentEnvironment.PRODUCTION,
            artifact_id="build_v2",
            version="1.1.0"
        )

        # Rollback
        rolled_back = self.deployment.rollback(DeploymentEnvironment.PRODUCTION)

        self.assertIsNotNone(rolled_back)
        self.assertEqual(rolled_back.version, "1.0.0")

    def test_get_active_deployment(self):
        """Test getting active deployment"""
        self.deployment.deploy(
            DeploymentEnvironment.STAGING,
            artifact_id="build_789",
            version="1.2.0"
        )

        active = self.deployment.get_active_deployment(DeploymentEnvironment.STAGING)

        self.assertIsNotNone(active)
        self.assertEqual(active.version, "1.2.0")

    def test_deployment_history(self):
        """Test deployment history tracking"""
        for i in range(5):
            self.deployment.deploy(
                DeploymentEnvironment.STAGING,
                artifact_id=f"build_{i}",
                version=f"1.0.{i}"
            )

        history = self.deployment.get_deployment_history(DeploymentEnvironment.STAGING, limit=3)

        self.assertEqual(len(history), 3)

    def test_health_check(self):
        """Test deployment health check"""
        deployment = self.deployment.deploy(
            DeploymentEnvironment.PRODUCTION,
            artifact_id="build_health",
            version="1.1.4"
        )

        health = self.deployment.health_check(deployment.deployment_id)

        self.assertTrue(health["healthy"])
        self.assertEqual(health["version"], "1.1.4")

    def test_deployment_metadata(self):
        """Test deployment metadata tracking"""
        deployment = self.deployment.deploy(
            DeploymentEnvironment.PRODUCTION,
            artifact_id="build_meta",
            version="1.1.4"
        )

        self.assertIsNotNone(deployment.deployed_at)
        self.assertEqual(deployment.deployed_by, "ci-pipeline")

    def test_multiple_environment_deployments(self):
        """Test deploying to multiple environments"""
        self.deployment.deploy(
            DeploymentEnvironment.DEVELOPMENT,
            "dev_build",
            "1.1.4-dev"
        )

        self.deployment.deploy(
            DeploymentEnvironment.STAGING,
            "staging_build",
            "1.1.4-rc1"
        )

        self.deployment.deploy(
            DeploymentEnvironment.PRODUCTION,
            "prod_build",
            "1.1.4"
        )

        dev = self.deployment.get_active_deployment(DeploymentEnvironment.DEVELOPMENT)
        staging = self.deployment.get_active_deployment(DeploymentEnvironment.STAGING)
        prod = self.deployment.get_active_deployment(DeploymentEnvironment.PRODUCTION)

        self.assertEqual(dev.version, "1.1.4-dev")
        self.assertEqual(staging.version, "1.1.4-rc1")
        self.assertEqual(prod.version, "1.1.4")


class TestQualityGates(unittest.TestCase):
    """Test quality gate enforcement"""

    def setUp(self):
        self.gates = QualityGates()

    def test_run_linting(self):
        """Test code linting check"""
        check = self.gates.run_linting(["file1.py", "file2.py"])

        self.assertEqual(check.check_type, "lint")
        self.assertGreaterEqual(check.score, self.gates.passing_threshold)

    def test_run_security_scan(self):
        """Test security scanning"""
        check = self.gates.run_security_scan(["requests", "flask", "pytest"])

        self.assertEqual(check.check_type, "security")
        self.assertEqual(check.details["vulnerabilities_found"], 0)

    def test_run_performance_benchmark(self):
        """Test performance benchmarking"""
        check = self.gates.run_performance_benchmark("test_suite_v1")

        self.assertEqual(check.check_type, "performance")
        self.assertIn("avg_response_time_ms", check.details)

    def test_run_compliance_check(self):
        """Test compliance validation"""
        check = self.gates.run_compliance_check(["WCAG 2.1", "GDPR"])

        self.assertEqual(check.check_type, "compliance")
        self.assertTrue(check.details["compliant"])

    def test_evaluate_gates(self):
        """Test overall gate evaluation"""
        self.gates.run_linting(["test.py"])
        self.gates.run_security_scan(["pytest"])

        passes = self.gates.evaluate_gates()
        self.assertTrue(passes)

    def test_quality_report_generation(self):
        """Test quality report"""
        self.gates.run_linting(["test.py"])
        self.gates.run_security_scan(["pytest"])
        self.gates.run_performance_benchmark("suite")

        report = self.gates.get_quality_report()

        self.assertEqual(report["total_checks"], 3)
        self.assertTrue(report["all_gates_passed"])

    def test_failing_quality_gate(self):
        """Test failing quality gate"""
        # Manually create a failing check
        failing_check = QualityCheck(
            check_name="Fail Test",
            check_type="lint",
            status=PipelineStatus.FAILED,
            score=50.0,
            threshold=80.0
        )

        self.gates.checks.append(failing_check)

        passes = self.gates.evaluate_gates()
        self.assertFalse(passes)


class TestMonitoringIntegration(unittest.TestCase):
    """Test monitoring and notifications"""

    def setUp(self):
        self.monitoring = MonitoringIntegration()

    def test_record_metric(self):
        """Test recording metrics"""
        self.monitoring.record_metric(
            "build_duration",
            value=300.5,
            unit="seconds",
            tags={"platform": "linux"}
        )

        self.assertEqual(len(self.monitoring.metrics), 1)

    def test_send_notification(self):
        """Test sending notifications"""
        self.monitoring.send_notification(
            title="Build Failed",
            message="Build #123 failed",
            severity="error"
        )

        self.assertEqual(len(self.monitoring.notifications), 1)

    def test_get_metric_stats(self):
        """Test metric statistics"""
        self.monitoring.record_metric("test_duration", 10.0, "s")
        self.monitoring.record_metric("test_duration", 15.0, "s")
        self.monitoring.record_metric("test_duration", 12.0, "s")

        stats = self.monitoring.get_metric_stats("test_duration")

        self.assertEqual(stats["count"], 3)
        self.assertEqual(stats["min"], 10.0)
        self.assertEqual(stats["max"], 15.0)

    def test_build_trends(self):
        """Test build trend analysis"""
        for i in range(10):
            self.monitoring.record_metric("build_duration", 300 + i * 10, "s")

        trends = self.monitoring.get_build_trends(days=7)

        self.assertGreater(trends["total_builds"], 0)
        self.assertGreater(trends["success_rate"], 0)

    def test_alert_checking(self):
        """Test alert condition checking"""
        # Trigger alert with slow build
        self.monitoring.record_metric("build_duration", 700, "s")

        alerts = self.monitoring.check_alerts()

        self.assertGreater(len(alerts), 0)

    def test_notification_channels(self):
        """Test notification channel configuration"""
        self.monitoring.send_notification(
            "Test",
            "Message",
            "info",
            channels=["slack"]
        )

        notification = self.monitoring.notifications[0]
        self.assertIn("slack", notification["channels"])


# ============================================================================
# TEST RUNNER
# ============================================================================

if __name__ == '__main__':
    unittest.main(verbosity=2)
