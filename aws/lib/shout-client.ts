import {
    aws_ec2 as ec2,
    aws_sqs as sqs,
    aws_iam as iam,
    CfnParameter,
    aws_ecs as ecs,
    aws_logs as logs,
    Aws,
} from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { MediaStore } from './media-store';
import { Cluster } from './cluster';
import { VoscastServer } from './voscast-server';
import { SlackBots } from './slack-bots';

interface ShoutClientProps {
    readonly vpc: ec2.Vpc;
    readonly mediaStore: MediaStore;
    readonly queue: sqs.Queue;
    readonly image: ecs.EcrImage;
    readonly instanceType: CfnParameter;
    readonly logGroup: logs.LogGroup;
    readonly slackBots: SlackBots;
    readonly voscastServer: VoscastServer;
}

export class ShoutClient extends Construct {
    constructor(scope: Construct, id: string, props: ShoutClientProps) {
        super(scope, id);

        const cluster = new Cluster(this, 'ShoutClientCluster', {
            vpc: props.vpc,
            clusterName: 'ShoutClientCluster',
            image: props.image,
            instanceType: props.instanceType,
            minCapacity: 0,
            maxCapacity: 1,
            logGroup: props.logGroup,
            hardwareType: ecs.AmiHardwareType.STANDARD,
        });

        const taskRole = new iam.Role(this, 'EcsTaskRole', {
            roleName: 'ShoutClientTaskRole',
            assumedBy: new iam.ServicePrincipal('ecs-tasks.amazonaws.com'),
            inlinePolicies: {
                SecretManager: new iam.PolicyDocument({
                    statements: [
                        new iam.PolicyStatement({
                            actions: ['secretsmanager:GetSecretValue'],
                            resources: [
                                'arn:aws:secretsmanager:us-east-1:289115055556:secret:wet-toast-talk-radio/voscast-password-k293v1',
                            ],
                        }),
                    ],
                }),
            },
        });
        props.mediaStore.bucket.grantReadWrite(taskRole);
        props.queue.grantConsumeMessages(taskRole);
        props.slackBots.grantReadSlackBotSecrets(taskRole);
        props.voscastServer.grantReadPasswordSecret(taskRole);

        const ecsTaskDefinition = new ecs.Ec2TaskDefinition(this, 'EcsTaskDefinition', {
            family: 'wet-toast-shout-client',
            taskRole: taskRole,
        });

        const environment = {
            ...props.slackBots.envVars(),
            AWS_REGION: Aws.REGION,
            WT_MEDIA_STORE__S3__BUCKET_NAME: props.mediaStore.bucket.bucketName,
            WT_MESSAGE_QUEUE__SQS__STREAM_QUEUE_NAME: props.queue.queueName,
            WT_DISC_JOCKEY__SHOUT_CLIENT__PASSWORD: props.voscastServer.password(),
            WT_DISC_JOCKEY__SHOUT_CLIENT__HOSTNAME: props.voscastServer.hostname(),
            WT_DISC_JOCKEY__SHOUT_CLIENT__PORT: props.voscastServer.port(),
        };

        // t3.small : 2 vCPU, 2 GiB
        ecsTaskDefinition.addContainer('Container', {
            image: props.image,
            containerName: 'shout-client',
            command: ['disc-jockey', 'stream'],
            memoryLimitMiB: 1900, // 2 GB
            cpu: 2048, // 2 vCPUs
            logging: ecs.LogDriver.awsLogs({ logGroup: props.logGroup, streamPrefix: Aws.STACK_NAME }),
            environment,
        });

        new ecs.Ec2Service(this, 'Service', {
            serviceName: 'wet-toast-shout-client-service',
            cluster: cluster.ecsCluster,
            taskDefinition: ecsTaskDefinition,
            desiredCount: 0,
            capacityProviderStrategies: [
                {
                    capacityProvider: cluster.capacityProvider.capacityProviderName,
                    weight: 1,
                },
            ],
        });
    }
}
