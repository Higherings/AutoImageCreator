# AutoImageCreator
Easy to configure AMI generator for EC2 Instances in AWS
It uses CloudFormation and Lambda

It will create AMIs for EC2 Instances with an specified Tag and Value (they also need to have Tag Name, because it will ignore AutoScaling instances)

> Version 2.6.1

### Files:
- autoImageCreator-template.yml, CloudFormation template to Run in your account, it is already in a public S3 bucket

- autoimagecreator.py, Lambda code that actually do the job of AMI Creation, source code only for reviewing

- autoimagecreator.zip, zip file used by the template to deploy de Lambda, it is already in a public S3 Bucket

## How To Deploy
Use AWS CloudFormation to deploy the following template:

https://higher-artifacts.s3.amazonaws.com/autoImageCreator-template.yml

### Parameters:
- *Env Tag*, use to identified the component of the template

- *Selection Tag*, sets the Tag used to identified Instances of which AMIs will be created

- *Selection Tag Value*, sets the Value of the Tag to identified instances

- *Reboot*, set it 1 to Reboot when creating the AMI, or 0 to not Reboot

- *Frequency*, specify how often the AMIs will be created (in days)

- *Time*, specify at what time the AMIs will be created

- *History*, specify how many old AMIs do you want to keep (the Lambda will remove only the AMIs it created)

`If you edit the template remember to use LF end of lines.`

`Update KMS user policy to include Lambda Role if using KMS encrypted EBSs with not default Service Keys.`

## To-Do
- Make a more restrict EC2 policy for the Lambda so it can only create AMIs and nothing more

- A better error management