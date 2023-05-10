tput bold; echo "REGISTER FTD"; tput sgr0
python3 create-acp.py
python3 create-acp-rule.py
python3 add-device.py
python3 add-ha-pair.py

echo; tput bold; echo "CREATE SECURITY ZONE"; tput sgr0
python3 create-sec-zone.py

echo; tput bold; echo "CREATE STANDARD NETWORK OBJECT"; tput sgr0
python3 create-standard-obj-host.py
python3 create-standard-obj-network.py
python3 create-standard-obj-netgroup.py

echo; tput bold; echo "CREATE OVERRIDABLE NETWORK OBJECT"; tput sgr0
python3 create-override-obj.py
python3 add-override-obj-host.py
python3 add-override-obj-network.py
python3 add-override-obj-netgroup.py

echo; tput bold; echo "CONFIGURE PHYSICAL INTERFACE"; tput sgr0
python3 config-intf-name.py
python3 config-intf-enable.py
python3 config-intf-sec-zone.py
python3 config-intf-ip-addr.py

echo; tput bold; echo "CREATE & CONFIGURE SUBINTERFACE"; tput sgr0
python3 create-etherchannel.py
python3 enable-mainintf-of-subintf.py
python3 create-subintf.py

echo; tput bold; echo "CREATE VIRTUAL ROUTER"; tput sgr0
python3 create-virtual-router.py

echo; tput bold; echo "CREATE STATIC ROUTE"; tput sgr0
python3 create-static-route-global.py
python3 create-static-route-vr.py

echo; tput bold; echo "ADD BGP ROUTING"; tput sgr0
python3 add-bgp-general.py
python3 add-bgp-peer-vr.py
read -p "Please finish rest of BGP configuration manually, then press ENTER to continue ..."

echo; tput bold; echo "SETUP POLICY"; tput sgr0
python3 set-acp-inheritance.py



