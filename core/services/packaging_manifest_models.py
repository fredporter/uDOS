"""Canonical packaging manifest v2 typed models."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field
from pydantic.aliases import AliasChoices
from typing import Literal


class VersionSource(BaseModel):
    model_config = ConfigDict(extra="forbid")

    path: str = "version.json"
    field_priority: list[str] = Field(default_factory=lambda: ["display", "version"])


class BuildIdPolicy(BaseModel):
    model_config = ConfigDict(extra="forbid")

    prefix: str = "build"
    timestamp_format: str = "%Y%m%d-%H%M%S"
    random_suffix_length: int = 6


class SigningPolicy(BaseModel):
    model_config = ConfigDict(extra="forbid")

    required: bool = False
    algorithm: str = "sha256"
    detached_signature_ext: str = ".sig"
    public_key_env: str = "WIZARD_SONIC_SIGN_PUBKEY"


class OfflineAssets(BaseModel):
    model_config = ConfigDict(extra="forbid")

    root: str = Field(default="distribution/offline-assets", validation_alias=AliasChoices("root", "source_root"))
    cache_namespace: str = Field(
        default="memory/wizard/offline-assets",
        validation_alias=AliasChoices("cache_namespace", "cache_root"),
    )


class DependencyProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    runtime_packages: list[str] = Field(default_factory=list)
    build_packages: list[str] = Field(default_factory=list)


class GlobalPackagingPolicy(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version_source: VersionSource = Field(default_factory=VersionSource)
    build_id_policy: BuildIdPolicy = Field(default_factory=BuildIdPolicy)
    signing_policy: SigningPolicy = Field(default_factory=SigningPolicy)
    offline_assets: OfflineAssets = Field(
        default_factory=OfflineAssets,
        validation_alias=AliasChoices("offline_assets", "offline_asset_roots"),
    )


class WindowsThinGuiBuild(BaseModel):
    model_config = ConfigDict(extra="forbid")

    workspace: str = "wizard/dashboard"
    target: str = "msi"
    release: bool = True


class WindowsMediaGameImageSteps(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scripts_root: str = "distribution/windows10-entertainment/scripts"
    mode_switch_script: str = "distribution/windows10-entertainment/scripts/mode-switch.ps1"
    install_media_shell_script: str = "distribution/windows10-entertainment/scripts/install-media-shell.ps1"
    install_game_launcher_script: str = "distribution/windows10-entertainment/scripts/install-game-launcher.ps1"
    media_policies_script: str = "distribution/windows10-entertainment/scripts/media-policies.ps1"
    offline_root: str = "C:\\mount"
    media_identifier: str = "{media}"
    game_identifier: str = "{game}"
    media_partition: str = "\\Device\\HarddiskVolume3"
    game_partition: str = "\\Device\\HarddiskVolume4"
    boot_timeout_seconds: int = 5


class WindowsShellDefaults(BaseModel):
    model_config = ConfigDict(extra="forbid")

    kodi: str = "C:\\Program Files\\Kodi\\kodi.exe"
    playnite: str = "C:\\Program Files\\Playnite\\Playnite.FullscreenApp.exe"
    steam: str = "C:\\Program Files (x86)\\Steam\\steam.exe -bigpicture"
    custom: str = "C:\\udos\\MediaShell\\udos-media.exe"
    default_game_launcher_path: str = "C:\\Program Files\\Playnite\\Playnite.FullscreenApp.exe"


class WindowsPlatformConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    default_dependency_profile: str = "windows10-entertainment"
    dependency_profiles: dict[str, DependencyProfile] = Field(
        default_factory=lambda: {"windows10-entertainment": DependencyProfile()}
    )
    thin_gui_build: WindowsThinGuiBuild = Field(
        default_factory=WindowsThinGuiBuild,
        validation_alias=AliasChoices("thin_gui_build", "tauri_build"),
    )
    media_game_image_steps: WindowsMediaGameImageSteps = Field(default_factory=WindowsMediaGameImageSteps)
    shell_defaults: WindowsShellDefaults = Field(default_factory=WindowsShellDefaults)


class MacOSAppBundle(BaseModel):
    model_config = ConfigDict(extra="forbid")

    app_name: str = "uDOS Wizard.app"
    bundle_id: str = "com.udos.wizard"


class MacOSSigningIdentity(BaseModel):
    model_config = ConfigDict(extra="forbid")

    identity_env: str = "UDOS_MACOS_SIGNING_IDENTITY"
    team_id_env: str = "UDOS_MACOS_TEAM_ID"


class MacOSNotarization(BaseModel):
    model_config = ConfigDict(extra="forbid")

    enabled: bool = False
    apple_id_env: str = "UDOS_MACOS_NOTARY_APPLE_ID"
    app_password_env: str = "UDOS_MACOS_NOTARY_APP_PASSWORD"
    team_id_env: str = "UDOS_MACOS_TEAM_ID"


class MacOSDmgPackaging(BaseModel):
    model_config = ConfigDict(extra="forbid")

    enabled: bool = True
    volume_name: str = "uDOS Wizard"
    output_dir: str = "distribution/builds/macos"


class MacOSPlatformConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    default_dependency_profile: str = "wizard-app"
    dependency_profiles: dict[str, DependencyProfile] = Field(
        default_factory=lambda: {"wizard-app": DependencyProfile()}
    )
    app_bundle: MacOSAppBundle = Field(default_factory=MacOSAppBundle)
    signing_identity: MacOSSigningIdentity = Field(default_factory=MacOSSigningIdentity)
    notarization: MacOSNotarization = Field(default_factory=MacOSNotarization)
    dmg_packaging: MacOSDmgPackaging = Field(default_factory=MacOSDmgPackaging)


class LinuxAppBundle(BaseModel):
    model_config = ConfigDict(extra="forbid")

    build_script: str = "distribution/alpine-core/build-sonic-stick.sh"
    default_profile: str = "alpine-core+sonic"
    builds_root: str = "distribution/builds"
    runtime_dependencies: list[str] = Field(default_factory=lambda: ["sqlite3"])


class LinuxKioskWrapper(BaseModel):
    model_config = ConfigDict(extra="forbid")

    service_name: str = "udos-kiosk-wrapper"
    wrapper_script: str = "distribution/linux/kiosk-wrapper.sh"
    enabled_by_default: bool = False


class LinuxPlatformConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    default_dependency_profile: str = "alpine-core+sonic"
    dependency_profiles: dict[str, DependencyProfile] = Field(
        default_factory=lambda: {
            "alpine-core+sonic": DependencyProfile(runtime_packages=["sqlite3"]),
            "udos-ui-thin-gui": DependencyProfile(
                runtime_packages=[
                    "cage",
                    "wayland",
                    "libxkbcommon",
                    "mesa",
                    "libinput",
                    "seatd",
                ],
                build_packages=[
                    "cargo",
                    "rustc",
                    "nodejs",
                    "npm",
                    "python3",
                    "python3-dev",
                    "gtk+3.0-dev",
                    "webkit2gtk-dev",
                ],
            ),
        }
    )
    app_bundle: LinuxAppBundle = Field(default_factory=LinuxAppBundle)
    kiosk_wrapper: LinuxKioskWrapper = Field(default_factory=LinuxKioskWrapper)


class PackagingPlatforms(BaseModel):
    model_config = ConfigDict(extra="forbid")

    windows: WindowsPlatformConfig = Field(default_factory=WindowsPlatformConfig)
    macos: MacOSPlatformConfig = Field(default_factory=MacOSPlatformConfig)
    linux: LinuxPlatformConfig = Field(default_factory=LinuxPlatformConfig)


class PackagingManifestV2(BaseModel):
    model_config = ConfigDict(extra="forbid")

    manifest_schema: Literal["udos.packaging.manifest.v2"] = Field(
        default="udos.packaging.manifest.v2",
        alias="schema",
    )
    global_: GlobalPackagingPolicy = Field(default_factory=GlobalPackagingPolicy, alias="global")
    platforms: PackagingPlatforms = Field(default_factory=PackagingPlatforms)
