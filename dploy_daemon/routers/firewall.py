"""
Router for Firewall commands
"""

import subprocess
import shlex
import json

from fastapi import APIRouter, HTTPException, status
from dploy_daemon.config import settings

from dploy_daemon.models.exceptions import GenericError, SuccessResponse
from dploy_daemon.models.firewall import GetActiveZonesRequest, GetActiveZonesResponse, \
		GetConfigForZoneRequest, GetConfigForZoneResponse, \
		AddServiceToZoneRequest, AddServiceToZoneResponse, \
		RemoveServiceFromZoneRequest, RemoveServiceFromZoneResponse, \
		AddProtocolToZoneRequest, AddProtocolToZoneResponse, \
		RemoveProtocolFromZoneRequest, RemoveProtocolFromZoneResponse

router = APIRouter(
	prefix="/firewall",
	tags=["firewall"],
)

#Get active zones
@router.post("/get-active-zones",
			 responses={
				 status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": GenericError},
				 status.HTTP_200_OK: {"model": GetActiveZonesResponse},
			 })
async def getActiveZones(request: GetActiveZonesRequest) -> GetActiveZonesResponse:
	"""
	Execute get all active zones request
	"""
	try:
		process = subprocess.Popen(f"""echo {shlex.quote(str(request.passwd))} | sudo -S firewall-cmd --get-active-zones""",
						 shell=True,
						 stdout=subprocess.PIPE,
						 stderr=subprocess.PIPE)
		output, error = process.communicate()
		if error:
			raise HTTPException(
				status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
				detail=ferror.decode('utf-8'),
			)

		output = output.decode("utf-8")
		dict_output = {}
		tmp_out = {}
		curr_zone = ""
		for line in output.splitlines():
			if line.startswith(" "):
				key, value = line.strip().split(":")
				tmp_out[key.strip()] = value.strip().split(" ")
			else :
				if curr_zone != "":
					dict_output[curr_zone] = tmp_out
				curr_zone = line.strip()
				tmp_out = {}
		
		dict_output[curr_zone] = tmp_out
		json_output = json.dumps(dict_output, indent=4)

	except Exception as exception:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail=f"Error getting active zones - {exception.decode('utf-8')}",
		)
	return GetActiveZonesResponse(output=json_output)

#Get config for zone
@router.post("/get-zone-config",
			 responses={
				 status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": GenericError},
				 status.HTTP_200_OK: {"model": GetConfigForZoneResponse},
			 })
async def getZoneConfig(request: GetConfigForZoneRequest) -> GetConfigForZoneResponse:
	"""
	Execute get config for zone request
	"""
	try:
		process = subprocess.Popen(f"""echo {shlex.quote(str(request.passwd))} | sudo -S firewall-cmd \
						 --zone={shlex.quote(str(request.zone))} \
						 --list-all""",
						 shell=True,
						 stdout=subprocess.PIPE,
						 stderr=subprocess.PIPE)
		output, error = process.communicate()
		if error:
			raise HTTPException(
				status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
				detail=error.decode('utf-8'),
			)

		dict_output = {}
		output = output.decode("utf-8")
		for line in output.splitlines():
			if line.startswith(" "):
				key, value = line.strip().split(":")
				dict_output[key.strip()] = value.strip().split(" ")
				# if len(dict_output[key.strip()]) == 1:
				# 	dict_output[key.strip()] = dict_output[key.strip()][0]
		
		json_output = json.dumps(dict_output, indent=4)

	except Exception as exception:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail=f"Error getting config for the zone - {exception.decode('utf-8')}",
		)
	return GetConfigForZoneResponse(output=json_output)

#Add service to zone
@router.post("/add-service",
			 responses={
				 status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": GenericError},
				 status.HTTP_201_CREATED: {"model": AddServiceToZoneResponse},
			 })
async def addServiceToZone(request: AddServiceToZoneRequest) -> AddServiceToZoneResponse:
	"""
	Execute add service to zone request
	"""
	try:
		process = subprocess.Popen(f"""echo {shlex.quote(str(request.passwd))} | sudo -S firewall-cmd \
						 --zone={shlex.quote(str(request.zone))} \
						 --add-service={shlex.quote(str(request.service_name))} \
						 {'--permanent' if request.is_permanent else ''}""",
						 shell=True,
						 stdout=subprocess.PIPE,
						 stderr=subprocess.PIPE)
		
		error2 = False
		if(request.is_permanent):
			process2 = subprocess.Popen(f"""echo {shlex.quote(str(request.passwd))} | sudo -S firewall-cmd \
							--zone={shlex.quote(str(request.zone))} \
							--add-service={shlex.quote(str(request.service_name))}""",
							shell=True,
							stdout=subprocess.PIPE,
							stderr=subprocess.PIPE)
			
			output2, error2 = process2.communicate()
		
		output, error = process.communicate()


		if error or error2:
			raise HTTPException(
				status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
				detail=error.decode('utf-8'),
			)

	except OSError as exception:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail=f"Error adding service {request.service_name} to the zone {request.zone} - {exception.strerror.decode('utf-8')}",
		)
	return AddServiceToZoneResponse(output=f"Service {request.service_name} added to zone {request.zone} successfully")

#Remove service from zone
@router.post("/remove-service",
			 responses={
				 status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": GenericError},
				 status.HTTP_200_OK: {"model": RemoveServiceFromZoneResponse},
			 })
async def removeServiceFromZone(request: RemoveServiceFromZoneRequest) -> RemoveServiceFromZoneResponse:
	"""
	Execute remove service from zone request
	"""
	try:
		process = subprocess.Popen(f"""echo {shlex.quote(str(request.passwd))} | sudo -S firewall-cmd \
						 --zone={shlex.quote(str(request.zone))} \
						 --remove-service={shlex.quote(str(request.service_name))} \
						 {'--permanent' if request.is_permanent else ''}""",
						 shell=True,
						 stdout=subprocess.PIPE,
						 stderr=subprocess.PIPE)
		
		error2 = False
		if(request.is_permanent):
			process2 = subprocess.Popen(f"""echo {shlex.quote(str(request.passwd))} | sudo -S firewall-cmd \
							--zone={shlex.quote(str(request.zone))} \
							--remove-service={shlex.quote(str(request.service_name))}""",
							shell=True,
							stdout=subprocess.PIPE,
							stderr=subprocess.PIPE)
			
			output2, error2 = process2.communicate()

		output, error = process.communicate()
		if error or error2:
			raise HTTPException(
				status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
				detail=error.decode('utf-8'),
			)

	except OSError as exception:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail=f"Error removing service {request.service_name} from the zone {request.zone} - {exception.strerror.decode('utf-8')}",
		)
	return RemoveServiceFromZoneResponse(output=f"Service {request.service_name} removed from zone {request.zone} successfully")

#Add port/protocol to zone
@router.post("/add-port-protocol",
			 responses={
				 status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": GenericError},
				 status.HTTP_201_CREATED: {"model": AddProtocolToZoneResponse},
			 })
async def addPortToZone(request: AddProtocolToZoneRequest) -> AddProtocolToZoneResponse:
	"""
	Execute add Port/Protocol to zone request
	"""
	try:
		process = subprocess.Popen(f"""echo {shlex.quote(str(request.passwd))} | sudo -S firewall-cmd \
						 --zone={shlex.quote(str(request.zone))} \
						 --add-port={shlex.quote(str(request.port_protocol))} \
						 {'--permanent' if request.is_permanent else ''}""",
						 shell=True,
						 stdout=subprocess.PIPE,
						 stderr=subprocess.PIPE)
		
		error2 = False
		if(request.is_permanent):
			process2 = subprocess.Popen(f"""echo {shlex.quote(str(request.passwd))} | sudo -S firewall-cmd \
							--zone={shlex.quote(str(request.zone))} \
							--add-port={shlex.quote(str(request.port_protocol))}""",
							shell=True,
							stdout=subprocess.PIPE,
							stderr=subprocess.PIPE)
			
			output2, error2 = process2.communicate()
		
		output, error = process.communicate()
		if error or error2:
			raise HTTPException(
				status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
				detail=error.decode('utf-8'),
			)

	except OSError as exception:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail=f"Error adding port/protocol {request.port_protocol} to the zone {request.zone} - {exception.strerror.decode('utf-8')}",
		)
	return AddProtocolToZoneResponse(output=f"Port/Protocol {request.port_protocol} added to zone {request.zone} successfully")

#Remove port/protocol from zone
@router.post("/remove-port-protocol",
			 responses={
				 status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": GenericError},
				 status.HTTP_200_OK: {"model": RemoveProtocolFromZoneResponse},
			 })
async def removePortFromZone(request: RemoveProtocolFromZoneRequest) -> RemoveProtocolFromZoneResponse:
	"""
	Execute remove port/protocol from zone request
	"""
	try:
		process = subprocess.Popen(f"""echo {shlex.quote(str(request.passwd))} | sudo -S firewall-cmd \
						 --zone={shlex.quote(str(request.zone))} \
						 --remove-port={shlex.quote(str(request.port_protocol))} \
						 {'--permanent' if request.is_permanent else ''}""",
						 shell=True,
						 stdout=subprocess.PIPE,
						 stderr=subprocess.PIPE)
		
		error2 = False
		if(request.is_permanent):
			process2 = subprocess.Popen(f"""echo {shlex.quote(str(request.passwd))} | sudo -S firewall-cmd \
							--zone={shlex.quote(str(request.zone))} \
							--remove-port={shlex.quote(str(request.port_protocol))}""",
							shell=True,
							stdout=subprocess.PIPE,
							stderr=subprocess.PIPE)
			
			output2, error2 = process2.communicate()
		
		output, error = process.communicate()
		if error:
			raise HTTPException(
				status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
				detail=error.decode('utf-8'),
			)

	except OSError as exception:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail=f"Error removing port/protocol {request.port_protocol} from the zone {request.zone} - {exception.strerror.decode('utf-8')}",
		)
	return RemoveProtocolFromZoneResponse(output=f"Port/Protocol {request.port_protocol} removed from zone {request.zone} successfully")
