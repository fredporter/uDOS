"""
Home Assistant Gateway Service Module — Entry Point
===================================================

Can be run as: python -m wizard.services.home_assistant
"""

from wizard.services.home_assistant.service import HomeAssistantService

if __name__ == "__main__":
    service = HomeAssistantService()
    import uvicorn
    uvicorn.run(service.app, host="0.0.0.0", port=8765)
