Set_SNMP_Community = """
    <config>    
        <native xmlns="http://cisco.com/ns/yang/ned/ios">
            <snmp-server operation='merge'>
                <community>
                    <name>Secure</name>
                    <RW/>
                </community>
            </snmp-server>
        </native>
    </config>
"""
Delete_SNMP_Community = """
    <config>    
        <native xmlns="http://cisco.com/ns/yang/ned/ios">
            <snmp-server operation='delete'>
                <community>
                    <name>Secure</name>
                    <RW/>
                </community>
            </snmp-server>
        </native>
    </config>
"""
Get_SNMP_Config = """
    <native xmlns="http://cisco.com/ns/yang/ned/ios">
        <snmp-server>
        </snmp-server>
    </native>
"""