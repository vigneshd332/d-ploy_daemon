"""
Models for the Firewall API
"""

from typing import Optional
from pydantic import BaseModel, Field, Json


class GetActiveZonesRequest(BaseModel):
    """
    Request model for list all active firewall rules
    """
    passwd: str = Field(..., description="Password for sudo")

class GetActiveZonesResponse(BaseModel):
    """
    Response model for list all active firewall rules
    """

    output: Json = Field(..., description="Response from firewall for get active zones")
    # output: str = Field(..., description="Response from firewall for get active zones")

class GetConfigForZoneRequest(BaseModel):
	"""
	Request model for get config for zone
	"""

	passwd: str = Field(..., description="Password for sudo")
	zone: str = Field(..., description="Zone to get config for")

class GetConfigForZoneResponse(BaseModel):
	"""
	Response model for get config for zone
	"""

	output: Json = Field(..., description="Response from firewall for get config for zone")
	# output: str = Field(..., description="Response from firewall for get config for zone")

class AddServiceToZoneRequest(BaseModel):
	"""
	Request model for add service to zone
	"""

	passwd: str = Field(..., description="Password for sudo")
	zone: str = Field(..., description="Zone to add service to")
	service_name: str = Field(..., description="Service to add")
	is_permanent: bool = Field(False, description="Add permanently")

class AddServiceToZoneResponse(BaseModel):
	"""
	Response model for add service to zone
	"""

	output: str = Field(..., description="Response from firewall for add service to zone")

class RemoveServiceFromZoneRequest(BaseModel):
	"""
	Request model for add service to zone
	"""

	passwd: str = Field(..., description="Password for sudo")
	zone: str = Field(..., description="Zone to remove service from")
	service_name: str = Field(..., description="Service to remove")
	is_permanent: bool = Field(False, description="Remove permanently")

class RemoveServiceFromZoneResponse(BaseModel):
	"""
	Response model for add service to zone
	"""

	output: str = Field(..., description="Response from firewall for remove service from zone")

class AddProtocolToZoneRequest(BaseModel):
	"""
	Request model for add port/protocol to zone
	"""

	passwd: str = Field(..., description="Password for sudo")
	zone: str = Field(..., description="Zone to add port/protocol to")
	port_protocol: str = Field(..., description="Port/Protocol to add")
	is_permanent: bool = Field(False, description="Add permanently")

class AddProtocolToZoneResponse(BaseModel):
	"""
	Response model for add service to zone
	"""

	output: str = Field(..., description="Response from firewall for add port/protocol to zone")

class RemoveProtocolFromZoneRequest(BaseModel):
	"""
	Request model for remove port/protocol from zone
	"""

	passwd: str = Field(..., description="Password for sudo")
	zone: str = Field(..., description="Zone to remove port/protocol from")
	port_protocol: str = Field(..., description="Port/Protocol to remove")
	is_permanent: bool = Field(False, description="Remove permanently")

class RemoveProtocolFromZoneResponse(BaseModel):
	"""
	Response model for remove port/protocol from zone
	"""

	output: str = Field(..., description="Response from firewall for remove port/protocol from zone")