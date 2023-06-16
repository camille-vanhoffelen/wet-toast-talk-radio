import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { CfnParameters } from './cfn-parameters';
import { aws_ec2 as ec2, Tags, Aws, aws_ecs as ecs, aws_ecr as ecr, aws_logs as logs } from 'aws-cdk-lib';
import { MediaStore } from './media-store';
import { Transcoder } from './transcoder';
import { MessageQueue } from './message-queue';
import { Playlist } from './playlist';
import { ShoutClient } from './shout-client';
import { ScriptWriter } from './script-writer';
import { AudioGenerator } from './audio-generator';
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

        const mediaStore = new MediaStore(this, 'MediaStore');
        const messageQueue = new MessageQueue(this, 'MessageQueue');

        const logGroup = new logs.LogGroup(this, 'LogGroup', {
            logGroupName: Aws.STACK_NAME,
        });

        const image = ecs.ContainerImage.fromEcrRepository(
            ecr.Repository.fromRepositoryName(this, 'ECRRepository', params.ecrRepositoryName.valueAsString),
            params.imageTag.valueAsString,
        );
        new ScriptWriter(this, 'ScriptWriter', {
            vpc,
            mediaStore,
            queue: messageQueue.audiogenQueue,
            image,
            instanceType: params.scriptWriterInstanceType,
            logGroup,
        });

        new AudioGenerator(this, 'AudioGenerator', {
            vpc,
            mediaStore,
            queue: messageQueue.audiogenQueue,
            image,
            instanceType: params.audioGeneratorInstanceType,
            logGroup,
        });

        new Transcoder(this, 'Transcoder', {
            vpc,
            mediaStore,
            image,
            instanceType: params.transcoderInstanceType,
            logGroup,
        });

        new Playlist(this, 'Playlist', {
            vpc,
            mediaStore,
            queue: messageQueue.streamQueue,
            image,
            instanceType: params.playlistInstanceType,
            logGroup,
        });

        new ShoutClient(this, 'ShoutClient', {
            vpc,
            mediaStore,
            queue: messageQueue.streamQueue,
            image,
            instanceType: params.shoutClientInstanceType,
            logGroup,
        });
    }
}
