"""
Router for Firewall commands
"""

import subprocess
import shlex
import json

from fastapi import APIRouter, HTTPException, status
from dploy_daemon.config import settings

from dploy_daemon.dependencies import restart_docker, restart_firewalld

from dploy_daemon.models.exceptions import GenericError, SuccessResponse
from dploy_daemon.models.firewall import GetAllZonesRequest, GetAllZonesResponse, \
		GetConfigForZoneRequest, GetConfigForZoneResponse, \
		ServiceRequest, ServiceResponse, \
		PortRequest, PortResponse, \
		SourceRequest, SourceResponse, \
		PortForwardingRequest, PortForwardingResponse

router = APIRouter(
	prefix="/firewall",
	tags=["firewall"],
)

#Get All zones
@router.get("/get-all-zones",
			 responses={
				 status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": GenericError},
				 status.HTTP_200_OK: {"model": GetAllZonesResponse},
			 })
async def getAllZones() -> GetAllZonesResponse:
	"""
	Execute get all the zones request
	"""
	try:
		process = subprocess.Popen(f"""echo {shlex.quote(str(settings.sudo_passwd))} | sudo -p '' -S firewall-cmd --list-all-zones""",
						 shell=True,
						 stdout=subprocess.PIPE,
						 stderr=subprocess.PIPE)

		output, error = process.communicate()
		if error:
			raise HTTPException(
				status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
				detail=error.decode('utf-8'),
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

	except OSError as exception:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail=f"Error getting All zones - {exception.decode('utf-8')}",
		)
	return GetAllZonesResponse(output=json_output)

#Get config for zone
@router.get("/get-zone-config",
			 responses={
				 status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": GenericError},
				 status.HTTP_200_OK: {"model": GetConfigForZoneResponse},
			 })
async def getZoneConfig(zone) -> GetConfigForZoneResponse:
	"""
	Execute get config for zone request
	"""
	try:
		process = subprocess.Popen(f"""echo {shlex.quote(str(settings.sudo_passwd))} | sudo -p '' -S firewall-cmd \
						 --zone={shlex.quote(str(zone))} \
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

	except OSError as exception:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail=f"Error getting config for the zone - {exception.decode('utf-8')}",
		)
	return GetConfigForZoneResponse(output=json_output)

#Add service
@router.post("/add-service",
			 responses={
				 status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": GenericError},
				 status.HTTP_201_CREATED: {"model": ServiceResponse},
			 })
async def addService(request: ServiceRequest) -> ServiceResponse:
	"""
	Execute add service request
	"""
	try:
		process = subprocess.Popen(f"""echo {shlex.quote(str(settings.sudo_passwd))} | sudo -p '' -S firewall-cmd \
						 --zone={shlex.quote(str(settings.dploy_zone))} \
						 --add-service={shlex.quote(str(request.service_name))} \
						 --permanent && \
						 sudo -p '' -S firewall-cmd \
						 --zone=public \
						 --add-service={shlex.quote(str(request.service_name))} \
						 --permanent && \
						 echo {shlex.quote(str(settings.sudo_passwd))} | sudo -p '' -S firewall-cmd --complete-reload""",
						 shell=True,
						 stdout=subprocess.PIPE,
						 stderr=subprocess.PIPE)
		
		_, error = process.communicate()

		if error and "ALREADY_ENABLED" not in error.decode('utf-8'):
			raise HTTPException(
				status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
				detail=error.decode('utf-8'),
			)
		
		restart_docker()
		restart_firewalld()

	except OSError as exception:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail=f"Error adding service {request.service_name} - {exception.strerror.decode('utf-8')}",
		)
	return ServiceResponse(output=f"Service {request.service_name} added successfully")

#Remove service
@router.post("/remove-service",
			 responses={
				 status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": GenericError},
				 status.HTTP_200_OK: {"model": ServiceResponse},
			 })
async def removeService(request: ServiceRequest) -> ServiceResponse:
	"""
	Execute remove service request
	"""
	try:
		process = subprocess.Popen(f"""echo {shlex.quote(str(settings.sudo_passwd))} | sudo -p '' -S firewall-cmd \
						 --zone={shlex.quote(str(settings.dploy_zone))} \
						 --remove-service={shlex.quote(str(request.service_name))} \
						 --permanent && \
						 sudo -p '' -S firewall-cmd \
						 --zone=public \
						 --remove-service={shlex.quote(str(request.service_name))} \
						 --permanent && \
						 echo {shlex.quote(str(settings.sudo_passwd))} | sudo -p '' -S firewall-cmd --complete-reload""",
						 shell=True,
						 stdout=subprocess.PIPE,
						 stderr=subprocess.PIPE)
		
		_, error = process.communicate()
		if error and "NOT_ENABLED" not in error.decode('utf-8'):
			raise HTTPException(
				status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
				detail=error.decode('utf-8'),
			)

		restart_docker()
		restart_firewalld()

	except OSError as exception:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail=f"Error removing service {request.service_name}  - {exception.strerror.decode('utf-8')}",
		)
	return ServiceResponse(output=f"Service {request.service_name} removed successfully")

#Add port(s)
@router.post("/add-ports",
			 responses={
				 status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": GenericError},
				 status.HTTP_201_CREATED: {"model": PortResponse},
			 })
async def addPorts(request: PortRequest) -> PortResponse:
	"""
	Execute add port(s) in range request
	"""
	try:
		process = subprocess.Popen(f"""echo {shlex.quote(str(settings.sudo_passwd))} | sudo -p '' -S firewall-cmd \
						 --zone={shlex.quote(str(settings.dploy_zone))} \
						 --add-port={shlex.quote(str(request.port_protocol))} \
						 --permanent && \
						 sudo -p '' -S firewall-cmd \
						 --zone=public \
						 --add-port={shlex.quote(str(request.port_protocol))} \
						 --permanent && \
						 echo {shlex.quote(str(settings.sudo_passwd))} | sudo -p '' -S firewall-cmd --complete-reload""",
						 shell=True,
						 stdout=subprocess.PIPE,
						 stderr=subprocess.PIPE)
		
		_, error = process.communicate()
		if error and "ALREADY_ENABLED" not in error.decode('utf-8'):
			raise HTTPException(
				status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
				detail=error.decode('utf-8'),
			)
		
		restart_docker()
		restart_firewalld()

	except OSError as exception:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail=f"Error adding port(s) {request.port_protocol} - {exception.strerror.decode('utf-8')}",
		)
	return PortResponse(output=f"port(s) {request.port_protocol} added successfully")

#Remove port(s) from zone
@router.post("/remove-ports",
			 responses={
				 status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": GenericError},
				 status.HTTP_200_OK: {"model": PortResponse},
			 })
async def removePorts(request: PortRequest) -> PortResponse:
	"""
	Execute remove port(s) in range request
	"""
	try:
		process = subprocess.Popen(f"""echo {shlex.quote(str(settings.sudo_passwd))} | sudo -p '' -S firewall-cmd \
						 --zone={shlex.quote(str(settings.dploy_zone))} \
						 --remove-port={shlex.quote(str(request.port_protocol))} \
						 --permanent && \
						 sudo -p '' -S firewall-cmd \
						 --zone=public \
						 --remove-port={shlex.quote(str(request.port_protocol))} \
						 --permanent && \
						 echo {shlex.quote(str(settings.sudo_passwd))} | sudo -p '' -S firewall-cmd --complete-reload""",
						 shell=True,
						 stdout=subprocess.PIPE,
						 stderr=subprocess.PIPE)
		
		_, error = process.communicate()
		if error and "NOT_ENABLED" not in error.decode('utf-8'):
			raise HTTPException(
				status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
				detail=error.decode('utf-8'),
			)
		
		restart_docker()
		restart_firewalld()

	except OSError as exception:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail=f"Error removing port(s) {request.port_protocol}  - {exception.strerror.decode('utf-8')}",
		)
	return PortResponse(output=f"port(s) {request.port_protocol} removed successfully")

#Add Port Forwarding
@router.post("/add-port-forwarding",
			 responses={
				 status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": GenericError},
				 status.HTTP_201_CREATED: {"model": PortForwardingResponse},
				})
async def addPortForwarding(request: PortForwardingRequest) -> PortForwardingResponse:
	"""
	Execute add port forwarding request
	"""
	try:
		process = subprocess.Popen(f"""echo {shlex.quote(str(settings.sudo_passwd))} | sudo -p '' -S firewall-cmd \
						 --zone={shlex.quote(str(settings.dploy_zone))} \
						 --add-forward-port=port={shlex.quote(str(request.port))}:proto={shlex.quote(str(request.protocol))}:toport={shlex.quote(str(request.to_port))} \
						 --permanent && \
						 sudo -p '' -S firewall-cmd \
						 --zone=public \
						 --add-forward-port=port={shlex.quote(str(request.port))}:proto={shlex.quote(str(request.protocol))}:toport={shlex.quote(str(request.to_port))} \
						 --permanent && \
						 echo {shlex.quote(str(settings.sudo_passwd))} | sudo -p '' -S firewall-cmd --complete-reload""",
						 shell=True,
						 stdout=subprocess.PIPE,
						 stderr=subprocess.PIPE)
		
		_, error = process.communicate()
		if error and "ALREADY_ENABLED" not in error.decode('utf-8'):
			raise HTTPException(
				status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
				detail=error.decode('utf-8'),
			)
		
		restart_docker()
		restart_firewalld()

	except OSError as exception:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail=f"Error adding port forwarding from {request.port} to {request.to_port} - {exception.strerror.decode('utf-8')}",
		)
	return PortForwardingResponse(output=f"Port forwarding from {request.port} to {request.to_port} added successfully")

#Remove Port Forwarding
@router.post("/remove-port-forwarding",
			 responses={
				 status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": GenericError},
				 status.HTTP_200_OK: {"model": PortForwardingResponse},
				})
async def removePortForwarding(request: PortForwardingRequest) -> PortForwardingResponse:
	"""
	Execute remove port forwarding request
	"""
	try:
		process = subprocess.Popen(f"""echo {shlex.quote(str(settings.sudo_passwd))} | sudo -p '' -S firewall-cmd \
						 --zone={shlex.quote(str(settings.dploy_zone))} \
						 --remove-forward-port=port={shlex.quote(str(request.port))}:proto={shlex.quote(str(request.protocol))}:toport={shlex.quote(str(request.to_port))} \
						 --permanent && \
						 sudo -p '' -S firewall-cmd \
						 --zone=public \
						 --remove-forward-port=port={shlex.quote(str(request.port))}:proto={shlex.quote(str(request.protocol))}:toport={shlex.quote(str(request.to_port))} \
						 --permanent && \
						 echo {shlex.quote(str(settings.sudo_passwd))} | sudo -p '' -S firewall-cmd --complete-reload""",
						 shell=True,
						 stdout=subprocess.PIPE,
						 stderr=subprocess.PIPE)
		
		_, error = process.communicate()
		if error and "NOT_ENABLED" not in error.decode('utf-8'):
			raise HTTPException(
				status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
				detail=error.decode('utf-8'),
			)
		
		restart_docker()
		restart_firewalld()

	except OSError as exception:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail=f"Error removing port forwarding from {request.port} to {request.to_port}  - {exception.strerror.decode('utf-8')}",
		)
	return PortForwardingResponse(output=f"Port forwarding from {request.port} to {request.to_port} removed successfully")

#Add source address to whitelist
@router.post("/add-source-wtlst",
			 responses={
				 status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": GenericError},
				 status.HTTP_201_CREATED: {"model": SourceResponse},
			 })
async def addSource(request: SourceRequest) -> SourceResponse:
	"""
	Execute add source address to whitelist request
	"""
	try:
		# Check if the address to add contains /0
		if "/0" in request.source_address:
			request.source_address = "0.0.0.0/0"

		if "0.0.0.0/0" in request.source_address:
			process2 = subprocess.Popen(f"""echo {shlex.quote(str(settings.sudo_passwd))} | sudo -p '' -S firewall-cmd \
							   --zone=public \
							   --add-source={shlex.quote(str(request.source_address))} \
							   --permanent && \
							   echo {shlex.quote(str(settings.sudo_passwd))} | sudo -p '' -S firewall-cmd --complete-reload""",
							   shell=True,
							   stdout=subprocess.PIPE,
							   stderr=subprocess.PIPE)

			_, error2 = process2.communicate()
			if error2 and "ALREADY_ENABLED" not in error2.decode('utf-8'):
				raise HTTPException(
					status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
					detail=error2.decode('utf-8'),
				)
			
		else :
			# set default zone to internal and add IP to dpoy_zone
			process = subprocess.Popen(f"""echo {shlex.quote(str(settings.sudo_passwd))} | sudo -p '' -S firewall-cmd \
							--zone={shlex.quote(str(settings.dploy_zone)) if '/0' not in request.source_address else 'public'} \
							--add-source={shlex.quote(str(request.source_address))} \
							--permanent && \
							echo {shlex.quote(str(settings.sudo_passwd))} | sudo -p '' -S firewall-cmd \
							--set-default-zone=internal && \
							echo {shlex.quote(str(settings.sudo_passwd))} | sudo -p '' -S firewall-cmd --complete-reload""",
							shell=True,
							stdout=subprocess.PIPE,
							stderr=subprocess.PIPE)
			
			_, error = process.communicate()
			if error and "ALREADY_ENABLED" not in error.decode('utf-8') and "ZONE_ALREADY_SET" not in error.decode('utf-8'):
				raise HTTPException(
					status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
					detail=error.decode('utf-8'),
				)
		
		# If some /0 in whitelist, set default zone to public
		check_ip = await getZoneConfig("public")
		check_ip = check_ip.dict()
		if "0.0.0.0/0" in check_ip['output']['sources']:
			process1 = subprocess.Popen(f"""echo {shlex.quote(str(settings.sudo_passwd))} | sudo -p '' -S firewall-cmd \
								--set-default-zone=public && \
								echo {shlex.quote(str(settings.sudo_passwd))} | sudo -p '' -S firewall-cmd --complete-reload""",
								shell=True,
								stdout=subprocess.PIPE,
								stderr=subprocess.PIPE)

			_, error1 = process1.communicate()
			if error1 and "ZONE_ALREADY_SET" not in error1.decode('utf-8'):
				raise HTTPException(
					status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
					detail=error1.decode('utf-8'),
				)
			
		restart_docker()
		restart_firewalld()

	except OSError as exception:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail=f"Error adding source {request.source_address} to whitelist - {exception.strerror.decode('utf-8')}",
		)
	return SourceResponse(output=f"Source {request.source_address} added to whitelist successfully")

# Remove source address from whitelist
@router.post("/remove-source-wtlst",
			 responses={
				 status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": GenericError},
				 status.HTTP_200_OK: {"model": SourceResponse},
			 })
async def removeSource(request: SourceRequest) -> SourceResponse:
	"""
	Execute remove source address from whitelist request
	"""
	try:
		# Check if the address to remove contains /0, if yes set default zone to internal
		if "/0" in request.source_address:
			request.source_address = "0.0.0.0/0"

		check_ip = await getZoneConfig("public")
		check_ip = check_ip.dict()
		if "0.0.0.0/0" in request.source_address and "0.0.0.0/0" in check_ip['output']['sources']:
			process1 = subprocess.Popen(f"""echo {shlex.quote(str(settings.sudo_passwd))} | sudo -p '' -S firewall-cmd \
							   --zone=public \
							   --remove-source={shlex.quote(str(request.source_address))} \
							   --permanent && \
							   echo {shlex.quote(str(settings.sudo_passwd))} | sudo -p '' -S firewall-cmd --complete-reload""",
							   shell=True,
							   stdout=subprocess.PIPE,
							   stderr=subprocess.PIPE)

			_, error1 = process1.communicate()
			if error1 and "NOT_ENABLED" not in error1.decode('utf-8'):
				raise HTTPException(
					status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
					detail=error1.decode('utf-8'),
				)

			process2 = subprocess.Popen(f"""echo {shlex.quote(str(settings.sudo_passwd))} | sudo -p '' -S firewall-cmd \
							   --set-default-zone=internal && \
							   echo {shlex.quote(str(settings.sudo_passwd))} | sudo -p '' -S firewall-cmd --complete-reload""",
							   shell=True,
							   stdout=subprocess.PIPE,
							   stderr=subprocess.PIPE)

			_, error2 = process2.communicate()
			if error2:
				raise HTTPException(
					status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
					detail=error2.decode('utf-8'),
				)

		else :
			process = subprocess.Popen(f"""echo {shlex.quote(str(settings.sudo_passwd))} | sudo -p '' -S firewall-cmd \
							--zone={shlex.quote(str(settings.dploy_zone))} \
							--remove-source={shlex.quote(str(request.source_address))} \
							--permanent && \
							echo {shlex.quote(str(settings.sudo_passwd))} | sudo -p '' -S firewall-cmd --complete-reload""",
							shell=True,
							stdout=subprocess.PIPE,
							stderr=subprocess.PIPE)
			
			_, error = process.communicate()
			if error and "NOT_ENABLED" not in error.decode('utf-8'):
				raise HTTPException(
					status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
					detail=error.decode('utf-8'),
				)
		
		# Check if the whitelist IPs are empty, if yes set default zone to public
		check_ip = await getZoneConfig(settings.dploy_zone)
		check_ip = check_ip.dict()
		if check_ip['output']['sources'] == ['']:
			process1 = subprocess.Popen(f"""echo {shlex.quote(str(settings.sudo_passwd))} | sudo -p '' -S firewall-cmd \
							   --set-default-zone=public && \
							   echo {shlex.quote(str(settings.sudo_passwd))} | sudo -p '' -S firewall-cmd --complete-reload""",
							   shell=True,
							   stdout=subprocess.PIPE,
							   stderr=subprocess.PIPE)

			_, error1 = process1.communicate()
			if error1:
				raise HTTPException(
					status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
					detail=error1.decode('utf-8'),
				)
		
		restart_docker()
		restart_firewalld()
		
	except OSError as exception:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail=f"Error removing source {request.source_address} from whitelist - {exception.strerror.decode('utf-8')}",
		)
	return SourceResponse(output=f"Source {request.source_address} removed from whitelist successfully")

#Add source address to blacklist
@router.post("/add-source-blklst",
			 responses={
				 status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": GenericError},
				 status.HTTP_201_CREATED: {"model": SourceResponse},
			 })
async def addSourceBlk(request: SourceRequest) -> SourceResponse:
	"""
	Execute add source address to blacklist request
	"""
	try:
		if "/0" in request.source_address:
			raise HTTPException(
				status_code=status.HTTP_403_FORBIDDEN,
				detail="Addess with /0 should not be added to blacklist",
			)
		
		process = subprocess.Popen(f"""echo {shlex.quote(str(settings.sudo_passwd))} | sudo -p '' -S firewall-cmd \
						 --permanent \
						 --zone={shlex.quote(str(settings.dploy_blacklist_zone))} \
						 --add-source={shlex.quote(str(request.source_address))} && \
						 echo {shlex.quote(str(settings.sudo_passwd))} | sudo -p '' -S firewall-cmd --complete-reload""",
						 shell=True,
						 stdout=subprocess.PIPE,
						 stderr=subprocess.PIPE)
		
		_, error = process.communicate()
		if error and "ALREADY_ENABLED" not in error.decode('utf-8'):
			raise HTTPException(
				status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
				detail=error.decode('utf-8'),
			)

		restart_docker()
		restart_firewalld()

	except OSError as exception:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail=f"Error adding source {request.source_address} - {exception.strerror.decode('utf-8')}",
		)
	return SourceResponse(output=f"Source {request.source_address} added to blacklist successfully")

#Remove source address from blacklist
@router.post("/remove-source-blklst",
			 responses={
				 status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": GenericError},
				 status.HTTP_200_OK: {"model": SourceResponse},
			 })
async def removeSourceBlk(request: SourceRequest) -> SourceResponse:
	"""
	Execute remove source address from blacklist request
	"""
	try:
		process = subprocess.Popen(f"""echo {shlex.quote(str(settings.sudo_passwd))} | sudo -p '' -S firewall-cmd \
						 --permanent \
						 --zone={shlex.quote(str(settings.dploy_blacklist_zone))} \
						 --remove-source={shlex.quote(str(request.source_address))} && \
						 echo {shlex.quote(str(settings.sudo_passwd))} | sudo -p '' -S firewall-cmd --complete-reload""",
						 shell=True,
						 stdout=subprocess.PIPE,
						 stderr=subprocess.PIPE)
		
		_, error = process.communicate()
		if error and "NOT_ENABLED" not in error.decode('utf-8'):
			raise HTTPException(
				status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
				detail=error.decode('utf-8'),
			)
	
		restart_docker()
		restart_firewalld()
		
	except OSError as exception:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail=f"Error removing source {request.source_address} from blacklist - {exception.strerror.decode('utf-8')}",
		)
	return SourceResponse(output=f"Source {request.source_address} removed from blacklist successfully")
