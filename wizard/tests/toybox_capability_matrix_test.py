from wizard.routes.container_launcher_routes import ContainerLauncher
from wizard.services.toybox.elite_adapter import parse_elite_line


def test_toybox_profiles_include_elite_runtime_lane():
    cfg = ContainerLauncher.CONTAINER_CONFIGS
    assert "elite" in cfg
    elite = cfg["elite"]
    assert elite["port"] == 7422
    assert elite["browser_route"] == "/ui/elite"
    assert "wizard.services.toybox.elite_adapter" in " ".join(elite["launch_command"])


def test_elite_event_parser_emits_expected_canonical_events():
    jump_events = parse_elite_line("Hyperspace jump complete")
    assert any(e.get("type") == "ELITE_HYPERSPACE_JUMP" for e in jump_events)

    dock_events = parse_elite_line("Docking complete at station")
    assert any(e.get("type") == "ELITE_DOCKED" for e in dock_events)

    mission_events = parse_elite_line("Mission complete: courier run")
    assert any(e.get("type") == "ELITE_MISSION_COMPLETE" for e in mission_events)

    trade_events = parse_elite_line("Profit: 450")
    profit_event = next((e for e in trade_events if e.get("type") == "ELITE_TRADE_PROFIT"), None)
    assert profit_event is not None
    assert int(profit_event.get("payload", {}).get("profit", 0)) == 450
