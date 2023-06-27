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
import { Transcoder } from './transcoder';
import { MessageQueue } from './message-queue';
import { Playlist } from './playlist';
import { ShoutClient } from './shout-client';
import { ScriptWriter } from './script-writer';
import { AudioGenerator } from './audio-generator';
import { VoscastServer } from './voscast-server';
import { SlackBots } from './slack-bots';
import { OpenApi } from './open-api';
import { ModelCache } from './model-cache';

export class WetToastTalkShowStack extends cdk.Stack {
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

        const mediaStore = new MediaStore(this, 'MediaStore');
        const modelCache = new ModelCache(this, 'ModelCache', {
            bucketName: params.modelCacheBucketName,
        });
        const messageQueue = new MessageQueue(this, 'MessageQueue');

        const slackBots = new SlackBots(this, 'SlackBots', {
            emergencyAlertSystemUrl: params.emergencyAlertSystemUrl,
            radioOperatorUrl: params.radioOperatorUrl,
        });
        const voscastServer = new VoscastServer(this, 'VoscastServer', {
            voscastServerHostname: params.voscastHostname,
            voscastServerPort: params.voscastPort,
            voscastPassword: params.voscastPassword,
            voscastAutoDjKey: params.voscastAutoDjKey,
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
        });

        new Transcoder(this, 'Transcoder', {
            vpc,
            mediaStore,
            image,
            instanceType: params.transcoderInstanceType,
            logGroup,
            slackBots,
        });

        new Playlist(this, 'Playlist', {
            vpc,
            mediaStore,
            messageQueue,
            image,
            instanceType: params.playlistInstanceType,
            logGroup,
            slackBots,
        });

        new ShoutClient(this, 'ShoutClient', {
            vpc,
            mediaStore,
            messageQueue,
            image,
            instanceType: params.shoutClientInstanceType,
            logGroup,
            slackBots,
            voscastServer,
        });
    }
}
