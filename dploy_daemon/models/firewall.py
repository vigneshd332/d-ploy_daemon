"""
Models for the Firewall API
"""

from typing import Optional
from pydantic import BaseModel, Field, Json

from dploy_daemon.config import settings

class GetAllZonesRequest(BaseModel):
    """
    Request model for list all All firewall rules
    """
    pass

class GetAllZonesResponse(BaseModel):
    """
    Response model for list all All firewall rules
    """

    output: Json = Field(..., description="Response from firewall for get All zones")
    # output: str = Field(..., description="Response from firewall for get All zones")

class GetConfigForZoneRequest(BaseModel):
	"""
	Request model for get config for zone
	"""
	pass

class GetConfigForZoneResponse(BaseModel):
	"""
	Response model for get config for zone
	"""

	output: Json = Field(..., description="Response from firewall for get config for zone")
	# output: str = Field(..., description="Response from firewall for get config for zone")

class ServiceRequest(BaseModel):
	"""
	Request model for add/remove service
	"""

	service_name: str = Field(..., description="Service to add")

class ServiceResponse(BaseModel):
	"""
	Response model for add/remove service to zone
	"""

	output: str = Field(..., description="Response from firewall for adding/removing service")

class PortRequest(BaseModel):
	"""
	Request model for add/remove port/protocol
	"""

	port_protocol: str = Field(..., description="Port/Protocol to add")

class PortResponse(BaseModel):
	"""
	Response model for add/remove service
	"""

	output: str = Field(..., description="Response from firewall for adding/removing port/protocol")

class PortForwardingRequest(BaseModel):
	"""
	Request model for add/remove port forwarding
	"""
	port : str = Field(..., description="Port to forward requests from")
	protocol : str = Field(..., description="Protocol of requests to forward")
	to_port : str = Field(..., description="Port to forward requests to")

class PortForwardingResponse(BaseModel):
	"""
	Response model for add/remove port forwarding
	"""

	output: str = Field(..., description="Response from firewall for adding/removing port forwarding")

class SourceRequest(BaseModel):
	"""
	Request model for add source
	"""

	source_address: str = Field(..., description="Source address to add")

class SourceResponse(BaseModel):
	"""
	Response model for add source
	"""

	output: str = Field(..., description="Response from firewall for adding/removing source address in zone")
