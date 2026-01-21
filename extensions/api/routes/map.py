"""
Map Routes Blueprint
====================

Map/GeoTile endpoints: world, cities, tile operations, layers.
~10 endpoints for map navigation.
"""

from flask import Blueprint, jsonify, request, g
import logging

from ..services import init_udos_systems

api_logger = logging.getLogger("uDOS.API")

# Create blueprint
map_bp = Blueprint("map", __name__, url_prefix="/api/map")


def get_map_data_bridge():
    """Get map data bridge service."""
    from ..services.executor import _services

    return _services.get("map_data_bridge")


# ============================================================================
# MAP ENDPOINTS
# ============================================================================


@map_bp.route("/world", methods=["GET"])
def get_world_map():
    """Get complete world map data."""
    init_udos_systems()
    correlation_id = getattr(g, "correlation_id", "N/A")

    try:
        api_logger.info(f"[{correlation_id}] Getting world map data")

        map_bridge = get_map_data_bridge()
        if map_bridge is None:
            return (
                jsonify(
                    {"status": "error", "message": "Map data bridge not initialized"}
                ),
                500,
            )

        map_data = map_bridge.get_world_map_data()

        api_logger.info(f"[{correlation_id}] ✓ Retrieved world map data")
        return jsonify({"status": "success", "data": map_data})
    except Exception as e:
        api_logger.error(
            f"[{correlation_id}] Error getting world map: {e}", exc_info=True
        )
        return jsonify({"status": "error", "message": str(e)}), 500


@map_bp.route("/cities", methods=["GET"])
def get_map_cities():
    """Get list of cities, optionally filtered by layer."""
    init_udos_systems()
    correlation_id = getattr(g, "correlation_id", "N/A")

    try:
        layer = request.args.get("layer", type=int)

        api_logger.info(f"[{correlation_id}] Getting cities (layer={layer})")

        map_bridge = get_map_data_bridge()
        if map_bridge is None:
            return (
                jsonify(
                    {"status": "error", "message": "Map data bridge not initialized"}
                ),
                500,
            )

        cities = map_bridge.get_cities(layer)

        api_logger.info(f"[{correlation_id}] ✓ Retrieved {len(cities)} cities")
        return jsonify({"status": "success", "data": cities, "count": len(cities)})
    except Exception as e:
        api_logger.error(f"[{correlation_id}] Error getting cities: {e}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500


@map_bp.route("/city/<tile_code>", methods=["GET"])
def get_city_by_tile(tile_code: str):
    """Get city data by TILE code."""
    init_udos_systems()
    correlation_id = getattr(g, "correlation_id", "N/A")

    try:
        api_logger.info(f"[{correlation_id}] Getting city by TILE: {tile_code}")

        map_bridge = get_map_data_bridge()
        if map_bridge is None:
            return (
                jsonify(
                    {"status": "error", "message": "Map data bridge not initialized"}
                ),
                500,
            )

        city = map_bridge.get_city_by_tile(tile_code)

        if city:
            api_logger.info(f"[{correlation_id}] ✓ Found city: {city['name']}")
            return jsonify({"status": "success", "data": city})
        else:
            api_logger.warning(f"[{correlation_id}] City not found: {tile_code}")
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": f"City not found for TILE {tile_code}",
                    }
                ),
                404,
            )
    except Exception as e:
        api_logger.error(f"[{correlation_id}] Error getting city: {e}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500


@map_bp.route("/tile/<tile_code>/parse", methods=["GET"])
def parse_tile(tile_code: str):
    """Parse TILE code into components."""
    init_udos_systems()
    correlation_id = getattr(g, "correlation_id", "N/A")

    try:
        api_logger.info(f"[{correlation_id}] Parsing TILE: {tile_code}")

        map_bridge = get_map_data_bridge()
        if map_bridge is None:
            return (
                jsonify(
                    {"status": "error", "message": "Map data bridge not initialized"}
                ),
                500,
            )

        parsed = map_bridge.parse_tile_code(tile_code)

        if parsed:
            api_logger.info(f"[{correlation_id}] ✓ Parsed TILE: {tile_code}")
            return jsonify({"status": "success", "data": parsed})
        else:
            api_logger.warning(f"[{correlation_id}] Invalid TILE code: {tile_code}")
            return (
                jsonify(
                    {"status": "error", "message": f"Invalid TILE code: {tile_code}"}
                ),
                400,
            )
    except Exception as e:
        api_logger.error(f"[{correlation_id}] Error parsing TILE: {e}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500


@map_bp.route("/tile/<tile_code>/adjacent", methods=["GET"])
def get_adjacent(tile_code: str):
    """Get adjacent TILE codes."""
    init_udos_systems()
    correlation_id = getattr(g, "correlation_id", "N/A")

    try:
        api_logger.info(f"[{correlation_id}] Getting adjacent tiles for: {tile_code}")

        map_bridge = get_map_data_bridge()
        if map_bridge is None:
            return (
                jsonify(
                    {"status": "error", "message": "Map data bridge not initialized"}
                ),
                500,
            )

        adjacent = map_bridge.get_adjacent_tiles(tile_code)

        api_logger.info(f"[{correlation_id}] ✓ Retrieved adjacent tiles")
        return jsonify({"status": "success", "data": adjacent})
    except Exception as e:
        api_logger.error(
            f"[{correlation_id}] Error getting adjacent tiles: {e}", exc_info=True
        )
        return jsonify({"status": "error", "message": str(e)}), 500


@map_bp.route("/layers", methods=["GET"])
def get_layers():
    """Get all layer definitions."""
    init_udos_systems()
    correlation_id = getattr(g, "correlation_id", "N/A")

    try:
        api_logger.info(f"[{correlation_id}] Getting layer definitions")

        map_bridge = get_map_data_bridge()
        if map_bridge is None:
            return (
                jsonify(
                    {"status": "error", "message": "Map data bridge not initialized"}
                ),
                500,
            )

        layers = map_bridge.get_layers()

        api_logger.info(f"[{correlation_id}] ✓ Retrieved {len(layers)} layers")
        return jsonify({"status": "success", "data": layers})
    except Exception as e:
        api_logger.error(f"[{correlation_id}] Error getting layers: {e}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500
