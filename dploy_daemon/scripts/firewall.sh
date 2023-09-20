systemctl stop docker.socket
systemctl stop docker.service

firewall-cmd --zone=public --add-masquerade --permanent

# 2. Recreate DOCKER-USER iptables chain with firewalld. Ignore warnings, do not ignore errors
firewall-cmd --permanent --direct --remove-chain ipv4 filter DOCKER-USER
firewall-cmd --permanent --direct --remove-rules ipv4 filter DOCKER-USER
firewall-cmd --permanent --direct --add-chain ipv4 filter DOCKER-USER

# 3. Add iptables rules to DOCKER-USER chain - unrestricted outbound, restricted inbound to private IPs
firewall-cmd --permanent --direct --add-rule ipv4 filter DOCKER-USER 1 -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT -m comment --comment 'Allow containers to connect to the outside world'
firewall-cmd --permanent --direct --add-rule ipv4 filter DOCKER-USER 1 -j RETURN -s 127.0.0.0/8 -m comment --comment 'allow internal docker communication, loopback addresses'
firewall-cmd --permanent --direct --add-rule ipv4 filter DOCKER-USER 1 -j RETURN -s 172.16.0.0/12 -m comment --comment 'allow internal docker communication, private range'

# 3.1 optional: for wider internal networks
firewall-cmd --permanent --direct --add-rule ipv4 filter DOCKER-USER 1 -j RETURN -s 10.0.0.0/8 -m comment --comment 'allow internal docker communication, private range'
#firewall-cmd --permanent --direct --add-rule ipv4 filter DOCKER-USER 1 -j RETURN -s 192.168.0.0/16 -m comment --comment 'allow internal docker communication, private range'

# 4. Block all other IPs. This rule has lowest precedence, so you can add rules before this one later.
firewall-cmd --permanent --direct --add-rule ipv4 filter DOCKER-USER 10 -j REJECT -m comment --comment 'reject all other traffic to DOCKER-USER'

# 5. Activate rules
firewall-cmd --complete-reload

# 6. Start Docker
systemctl start docker.socket
systemctl start docker.service
