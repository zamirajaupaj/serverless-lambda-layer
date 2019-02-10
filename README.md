### Lambda Layer Serverless Framework

[![Join the chat at https://gitter.im/Zamira-Jaupaj/LambdaLayer](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/Zamira-Jaupaj/LambdaLayer)

### Requirements 
* Serverless framework 
* AWS Account 
* Mac, Windows and Linux

### Serverless Framework 
* Installing Node.js
**[check the link Node](https://nodejs.org/)**
You can install `nodejs`. Just run:

```
#  Ubuntu
$ curl -sL https://deb.nodesource.com/setup_8.x | sudo -E bash -
$ sudo apt-get install -y nodejs

#  Debian, as root
$ curl -sL https://deb.nodesource.com/setup_8.x | bash -
$ apt-get install -y nodejs
```
* Installing the Serverless Framework
**[check the link Serverless framework ](https://serverless.com/framework/docs/providers/aws/guide/installation/)**

```
$ npm install -g serverless
$ serverless --version

```
### AWS Account 
*IF YOU don't have yet an account on aws, you need an account to deploy lambda function
**[check the link AWS Account ](https://aws.amazon.com/account/)**

### Quickstart
```
$ pip install virtualenv
$ virtualenv -p python3 layer1
$ source layer1/bin/activate
$ pip install pymssql
$ pip freeze > requirements.txt
$ sls deploy
$ deactive
$ sls remove 

```
### Lambda Function and Layer

![Architecture of Lambda layer](https://raw.githubusercontent.com/zamirajaupaj/serverless-lambda-layer/master/documentation/lambdaLayer.png)


### Trigger Event
```JSON
{ 
 "DbName": "DbName",
 "DbUser": "DbUser",
 "S3BucketName": "S3BucketName",
 "KmsKeyId": "xxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxx",
 "RdsEndpoint": "RdsEndpoint",
 "RdsPort": "1433",
 "ParameterStore": "DbPassword",
 "Region": "eu-west-1",
 "AccountId": "123456789"
 }
```

### Backup RDS to s3 or Restore from s3 to RDS 
*backups from RDS, store them on S3, and then restore them from s3 to RDS. Native backup and restore is *available in all AWS Regions, and for both Single-AZ and Multi-AZ DB instances. Native backup and restore is available for all *editions of Microsoft SQL Server supported on Amazon RDS.

![Architecture Restore Backup](https://raw.githubusercontent.com/zamirajaupaj/serverless-lambda-layer/master/documentation/backupRestore.png)


### IAM Policy Permissions
```JSON
{
  "Effect": "Allow",
  "Action": [
      "s3:GetBucketLocation",
      "s3:DeleteObject",
      "s3:GetObject",
      "s3:GetObjectVersion",
      "s3:ListBucket",
      "s3:PutObject"
  ],
  "Resource": [
      "arn:aws:s3:::bucketname",
      "arn:aws:s3:::bucketname/*"
  ]
}
```
##### SSM 
```JSON
{
  "Effect": "Allow",
  "Action": [
      "ssm:GetParameters",
      "ssm:GetParameter"
  ],
  "Resource": [
      "arn:aws:ssm:region:*"
  ]
}
```

