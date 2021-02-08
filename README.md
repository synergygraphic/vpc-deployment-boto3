# vpc-deployment-boto3

This python file deploys a vpc from  AWSCLI terminal in the us-east-2 region, then a lambda function is triggered automatically to deploy a transit gateway attachment to a  previously deployed hub 

What can we do with these files?

The vpc-deploy.py file will deploy  an Amazon Virtual Private Cloud (Amazon VPC). It enables you to launch AWS resources into a virtual network that has been defined by this code. This virtual network closely resembles a traditional network that you'd operate in your own data center, with the benefits of using the scalable infrastructure of AWS. 

Now let us describe the resources being deployed.

	- 1 x VPC

	- 6 x Subnets

	- 3 Public Subnets, 1 per each AZ based on us-west-2 (Ohio)

	- 3 Private Subntes 1 per each AZ based on us-west-2(Ohio)

	- 1 x Internet Gateway

	- Attached to 3 x subnets identified as public

	- 1 x NAT Gateway

	- Attached to 1 x private subnet identified as private

	- 1 x EC2 Public Bastion

	- 1 x EC2 AppServer

	- 2 x Security Groups

	- One for the Public Bastion host or “JumpHost”

	- One for the AppServer in the Private Subnet for patching and upgrades

	- 2 x NACLs

	- 2 x Route Tables

	- 1 Public Route Table attached to Subnets identified as Public

	- 1 Private Route Table attached to Subnets identified as Private

	- 1 x key 

	- A key for both EC2s to enable ssh access

Any prerequisites?

- You must have your AWSCLI configured to run the python file in the target region
- You must have deployed a transit gateway either by hand or thru a lambda function with is provided here in order to allow the connection from the transit gateway attachment to his hub
- You must set up your cloudtrail logs and cloud watch events in order to capture createsubnet event and create a rule to trigger the lambda function to launch the transit gateway attachment for the newly created vpc to the hub

What do I need to do first?

Open the vpc-deploy.py file (I use Visual Studio Code) and update the variables with data as it pertains to your deployment

	- cidrvpc
	
	- destination_cidr_block
	
	- region
	
	- cidr_public
	
	- cidr_private
	
	- group_name
	
	- group_name2
	
	- keyname
	
	- instanceType
	
	- imageId
	
What to do next?

Once you have all your variables replaced let us go to our terminal. Open your Terminal and download the file in your project folder. Then run the python3 vpc-deploy.py command

The deployment of the vpc has been successfully initiated. You will see the prompts as the vpc resources are being deployed. I strongly recommend to sign in in your AWS Console to check as the new vpc and its resources become available. Note that we commented on the NATgateway part given the fact that for testing purposes NatGateways cost a fair share of money. Once you have your testing 100 percent successful you can uncomment those lines to deploy the NAT gateway along with the VPC. 
Cloudwatch will send the logs to Cloudwatch. The createsubnet event is captured and the lambda function is triggered. We set a waiting time to give the vpc deployment enough time, especially if you are going to deploy it with a NAT Gateway. After roughly 140 seconds the autogateway attachment funcion is going to initiate. It takes a couple minutes for the attachment to become available. 

What to look for?

In the VPC dashboard check for transit gateway attachments and you will see the new attachment available. Also check the private Route Table to verify that the route back to the transit gateway is in the table.
Now your AppServer is capable to connect with the other resources deployed to the other private subnets in the other spokes through the hub. Double check your Security Groups permissions if you have connection problems. 

Contribution guidelines

- Please fork us.
- Please fork yourself



	


