import boto3
import time

ec2Client = boto3.client('ec2')
ec2 = boto3.resource('ec2')

def main():
    
    cidrvpc='192.168.10.0/24'
    destination_cidr_block='0.0.0.0/0'
    region = "us-east-2"
    
    #Tags
    tags_vpc={"Name":"Proyecto10","TGW":"tgw-0ce597bb60c6ab894"}
    tags_igw ={"Name":"Proyecto10"}
    tags_rt_public ={"Name":"Proyecto10RtPublic"}
    tags_rt_private ={"Name":"Proyecto10RtPrivate","Type":"private","TGW":"tgw-0ce597bb60c6ab894"}
    tags_sn_public ={"Name":"Proyecto10SNPublic","Type":"public"}
    tags_sn_private ={"Name":"Proyecto10SNPrivate","Type":"private","TGW":"tgw-0ce597bb60c6ab894"}
    tags_sg_private ={"Name":"Proyecto10SGPrivate"}
    tags_sg_public ={"Name":"Proyecto10SGPublic"}
    tags_nalc_private ={"Name":"Proyecto10NAlcPrivate"}
    tags_nalc_public ={"Name":"Proyecto10NAlcPublic"}
    tags_ec2_private ={"Name":"Proyecto10InstancePrivate"}
    tags_ec2_public ={"Name":"Proyecto10InstancePublic"}

    #CIDR SUB NETS
    cidr_public=["192.168.10.0/27","192.168.10.32/27","192.168.10.64/27",]
    cidr_private=["192.168.10.128/27","192.168.10.160/27","192.168.10.192/27",]

    group_name="FullPublicAccess"
    group_name2="FullPrivateAccess"

    #authorize_ingress format 
    #authorize_ingress=[[CidrIp,IpProtocol,FromPort,ToPort],[CidrIp,IpProtocol,FromPort,ToPort],....]
    authorize_ingress=[["0.0.0.0/0","tcp",0,65535],["0.0.0.0/0","icmp",-1,-1]]

    keyname= "project10Key"
    #Variable InstanceType
    instanceType='t2.micro'
    #Variable ImageID
    imageId='ami-0d7e7122be7c5afd8'
    #Variable region
    region="us-east-2"

    vpc = create_vpc(ec2,cidrvpc,tags_vpc)
    print("It has been created vpc: ",vpc)
    enable_dns_hosname(ec2Client,vpc)
    igw = create_igw_and_vpcAttach(ec2,vpc,tags_igw)
    print("It has been created igw: ",igw)
    routetable_public= create_routetable(ec2,vpc,tags_rt_public) 
    print("It has been created rt: ",routetable_public)
    route = routetable_public.create_route(DestinationCidrBlock=destination_cidr_block, GatewayId=igw.id)
    routetable_private= create_routetable(ec2,vpc,tags_rt_private) 
    print("It has been created rt: ",routetable_private)
    subnets_publics=create_subnets_in_azs(ec2,vpc,routetable_public,cidr_public,region,tags_sn_public)
    print("It has been created subnets with ids: ", subnets_publics)
    subnets_privates=create_subnets_in_azs(ec2,vpc,routetable_private,cidr_private,region,tags_sn_private)
    print("It has been created subnets with ids: ", subnets_privates)
    sg_public=create_secury_group(ec2,vpc,authorize_ingress,group_name,tags_sg_public)
    print("It has been created sg: ", sg_public)
    sg_private=create_secury_group(ec2,vpc,authorize_ingress,group_name2,tags_sg_private)
    print("It has been created sg: ", sg_private)
    NALC_public=createNALC(ec2,vpc,tags_nalc_public)
    print("It has been created ALC: ", NALC_public)
    NALC_private=createNALC(ec2,vpc,tags_nalc_private)
    print("It has been created ALC: ", NALC_private)
    
    key=create_key_access(keyname)
    print("It has been created .PEM Access: ", key)
    instance_public=create_instance(imageId,instanceType,sg_public.group_id,subnets_publics[0],keyname,tags_ec2_public)
    print("It has been created Instance", instance_public)
    instance_private=create_instance(imageId,instanceType,sg_public.group_id,subnets_privates[0],keyname,tags_ec2_private,False)
    print("It has been created Instance", instance_private)
    
    #For NAT Gateway -Un-comment the next line in order to deploy the NAT Gateway
    #allocation = ec2Client.allocate_address(Domain='vpc')


def create_vpc(ec2,cidrvpc,tags=[]):
    try:
        vpc = ec2.create_vpc(CidrBlock=cidrvpc)
        time.sleep(2)
        for key in tags:
            vpc.create_tags(Tags=[{"Key": key, "Value": tags[key]}])
        vpc.wait_until_available()
        return vpc
    except Exception as e:
        print (e)
        return None

def enable_dns_hosname(ec2Client,vpc):
    try:
        ec2Client.modify_vpc_attribute( VpcId = vpc.id , EnableDnsSupport = { 'Value': True } )
        ec2Client.modify_vpc_attribute( VpcId = vpc.id , EnableDnsHostnames = { 'Value': True } )
    except Exception as e:
        print (e)
        return None
    
def create_igw_and_vpcAttach(ec2,vpc,tags=[]):
    try:
        internetgateway = ec2.create_internet_gateway()
        time.sleep(2)
        vpc.attach_internet_gateway(InternetGatewayId=internetgateway.id)
        for key in tags:
            internetgateway.create_tags(Tags=[{"Key": key, "Value": tags[key]}])
        return internetgateway
    except Exception as e:
        print (e)
        return None

def create_routetable(ec2,vpc,tags=[]):
    try:
        routetable = vpc.create_route_table()
        time.sleep(2)
        for key in tags:
            routetable.create_tags(Tags=[{"Key": key, "Value": tags[key]}])
        return routetable
    except Exception as e:
        print (e)
        return None
    
def create_subnets_in_azs(ec2,vpc,routetable,subnets_cidr,region,tags=[]):
    try:
        ids_subnets=[]
        zone=1
        cont=1
        for cidr in subnets_cidr:
            az=" "
            if zone ==1:
                az=region+"a"
            elif zone ==2:
                az=region+"b"
            elif zone ==3:
                az=region+"c"
                zone=1
            zone+=1
            subnet = ec2.create_subnet(CidrBlock=cidr, VpcId=vpc.id,AvailabilityZone=az)
            time.sleep(2)
            routetable.associate_with_subnet(SubnetId=subnet.id)
            for key in tags:
                if key =="Name":
                    subnet.create_tags(Tags=[{"Key": key, "Value": tags[key]+str(cont)}])
                else:
                    subnet.create_tags(Tags=[{"Key": key, "Value": tags[key]}])
            ids_subnets.append(subnet.id)
            cont+=1
        return ids_subnets
    except Exception as e:
        print (e)
        return None

def createNALC(ec2,vpc,tags=[]):
    try:    
        networkACL = ec2.create_network_acl( VpcId = vpc.id )
        time.sleep(2)
        for key in tags:
            networkACL.create_tags(Tags=[{"Key": key, "Value": tags[key]}])
        return networkACL
    except Exception as e:
        print (e)
        return None

def create_secury_group(ec2,vpc,authorize_ingress,group_name,tags=[]):
    try:    
        securitygroup = ec2.create_security_group(GroupName= group_name, Description='only allow SSH traffic', VpcId=vpc.id)
        time.sleep(2)
        for ai in authorize_ingress:
            securitygroup.authorize_ingress(CidrIp= ai[0], IpProtocol=ai[1], FromPort=ai[2], ToPort=ai[3])
        for key in tags:
            securitygroup.create_tags(Tags=[{"Key": key, "Value": tags[key]}])
        return securitygroup
    except Exception as e:
        print (e)
        return None


def create_key_access(keyname):
    try:
        # create a file to store the key locally
        outfile = open(keyname + ".pem", 'w')
        # call the boto ec2 function to create a key pair
        key_pair = ec2.create_key_pair(KeyName=keyname)
        # capture the key and store it in a file
        KeyPairOut = str(key_pair.key_material)
        outfile.write(KeyPairOut)
        return KeyPairOut
    except Exception as e:
        print (e)
        return None

def create_instance(imageId,instanceType,group_id,id_subnet,keyname,tags=[],AssociatePublicIpAddress = True):
    try:
        instances = ec2.create_instances(
        ImageId=imageId,
        InstanceType= instanceType,
        MaxCount=1,
        MinCount=1,
        NetworkInterfaces=[{
            'AssociatePublicIpAddress': AssociatePublicIpAddress,
            'SubnetId': id_subnet,
            'DeviceIndex': 0,
            'Groups': [group_id]
        }
        ],
        KeyName=keyname)
        for key in tags:
            instances[0].create_tags(Tags=[{"Key": key, "Value": tags[key]}])
        return instances[0]
    except Exception as e:
        print (e)
        return None

main()

