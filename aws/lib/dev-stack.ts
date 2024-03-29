import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { CfnParameters } from './cfn-parameters';
import {
    aws_ec2 as ec2,
    Tags,
    Aws,
    aws_ecs as ecs,
    aws_ecr as ecr,
    aws_logs as logs,
    aws_iam as iam,
} from 'aws-cdk-lib';
import { MediaStore } from './media-store';
import { MessageQueue } from './message-queue';
import { ScriptWriter } from './script-writer';
import { AudioGenerator } from './audio-generator';
import { SlackBots } from './slack-bots';
import { OpenApi } from './open-api';
import { ModelCache } from './model-cache';

export class WetToastTalkShowDevStack extends cdk.Stack {
    constructor(scope: Construct, id: string, props?: cdk.StackProps) {
        super(scope, id, props);

        const params = new CfnParameters(this);

        const natGatewayProvider = ec2.NatProvider.instance({
            instanceType: new ec2.InstanceType('t3.nano'),
        });
        const vpc = new ec2.Vpc(this, 'VPC', {
            vpcName: 'VPC',
            ipAddresses: ec2.IpAddresses.cidr('10.0.0.0/16'),
            enableDnsHostnames: true,
            enableDnsSupport: true,
            maxAzs: 2,
            natGatewayProvider,
            natGateways: 1,
            subnetConfiguration: [
                {
                    name: 'Public',
                    subnetType: ec2.SubnetType.PUBLIC,
                },
                {
                    name: 'Private',
                    subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS,
                },
            ],
        });
        Tags.of(vpc).add('Name', Aws.STACK_NAME);

        const s3BucketAcessPoint = vpc.addGatewayEndpoint('s3Endpoint', {
            service: ec2.GatewayVpcEndpointAwsService.S3,
        });
        s3BucketAcessPoint.addToPolicy(
            new iam.PolicyStatement({
                principals: [new iam.AnyPrincipal()],
                actions: ['s3:*'],
                resources: ['*'],
            }),
        );

        const mediaStore = new MediaStore(this, 'MediaStore', true);
        const modelCache = new ModelCache(this, 'ModelCache', {
            bucketName: params.modelCacheBucketName,
        });
        const messageQueue = new MessageQueue(this, 'MessageQueue', true);

        const slackBots = new SlackBots(this, 'SlackBots', {
            emergencyAlertSystemUrl: params.emergencyAlertSystemUrl,
            radioOperatorUrl: params.radioOperatorUrl,
            dev: true,
        });

        const openApi = new OpenApi(this, 'OpenApi', {
            openApiKey: params.openApiKey,
        });

        const logGroup = new logs.LogGroup(this, 'LogGroup', {
            logGroupName: Aws.STACK_NAME,
        });

        const image = ecs.ContainerImage.fromEcrRepository(
            ecr.Repository.fromRepositoryName(this, 'EcrRepository', params.ecrRepositoryName.valueAsString),
            params.imageTag.valueAsString,
        );

        const gpuImage = ecs.ContainerImage.fromEcrRepository(
            ecr.Repository.fromRepositoryName(this, 'GpuEcrRepository', params.ecrGpuRepositoryName.valueAsString),
            params.imageTag.valueAsString,
        );

        new ScriptWriter(this, 'ScriptWriter', {
            vpc,
            mediaStore,
            messageQueue,
            image,
            instanceType: params.scriptWriterInstanceType,
            logGroup,
            slackBots,
            openApi,
            dev: true,
        });

        new AudioGenerator(this, 'AudioGenerator', {
            vpc,
            mediaStore,
            messageQueue,
            image: gpuImage,
            instanceType: params.audioGeneratorInstanceType,
            logGroup,
            slackBots,
            modelCache,
            dev: true,
        });
    }
}
