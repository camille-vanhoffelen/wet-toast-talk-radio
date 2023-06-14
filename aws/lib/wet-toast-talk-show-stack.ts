import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { CfnParameters } from './cfn-parameters';
import {
    aws_ec2 as ec2,
    aws_ssm as ssm,
    Tags,
    Aws,
    aws_iam as iam,
    aws_ecs as ecs,
    aws_ecr as ecr,
    aws_logs as logs,
} from 'aws-cdk-lib';
import { WetToastBucket } from './wet-toast-bucket';
import { TranscodeService } from './transcode-service';
// import * as sqs from 'aws-cdk-lib/aws-sqs';

export class WetToastTalkShowStack extends cdk.Stack {
    constructor(scope: Construct, id: string, props?: cdk.StackProps) {
        super(scope, id, props);

        const params = new CfnParameters(this);

        const natGatewayProvider = ec2.NatProvider.instance({
            instanceType: new ec2.InstanceType('t3.nano'),
        });
        const vpc = new ec2.Vpc(this, 'VPC', {
            vpcName: 'VPC',
            cidr: '10.0.0.0/16',
            enableDnsHostnames: false,
            enableDnsSupport: false,
            maxAzs: 2,
            natGatewayProvider,
            natGateways: 1,
            subnetConfiguration: [
                {
                    name: 'Public',
                    subnetType: ec2.SubnetType.PUBLIC,
                },
                {
                    name: 'Privae',
                    subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS,
                },
            ],
        });
        Tags.of(vpc).add('Name', Aws.STACK_NAME);

        const wetToastBucket = new WetToastBucket(this, 'WetToastBucket');

        const logGroup = new logs.LogGroup(this, 'LogGroup', {
            logGroupName: Aws.STACK_NAME,
        });

        const cluster = new ecs.Cluster(this, 'Cluster', { vpc, clusterName: 'wet-toast-talk-radio' });

        const image = ecs.ContainerImage.fromEcrRepository(
            ecr.Repository.fromRepositoryName(this, 'ECRRepository', params.ecrRepositoryName.valueAsString),
            params.imageTag.valueAsString,
        );

        new TranscodeService(this, 'TranscodeService', {
            vpc,
            wetToastBucket,
            cluster,
            image,
            instanceType: params.transcoderInstanceType,
            logGroup,
        });
    }
}
