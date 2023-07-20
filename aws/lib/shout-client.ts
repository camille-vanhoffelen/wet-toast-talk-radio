import { aws_ec2 as ec2, aws_iam as iam, CfnParameter, aws_ecs as ecs, aws_logs as logs, Aws } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { MediaStore } from './media-store';
import { Cluster } from './cluster';
import { VoscastServer } from './voscast-server';
import { SlackBots } from './slack-bots';
import { MessageQueue } from './message-queue';

interface ShoutClientProps {
    readonly vpc: ec2.Vpc;
    readonly mediaStore: MediaStore;
    readonly messageQueue: MessageQueue;
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
        props.messageQueue.grantConsumeMessages(taskRole);
        props.slackBots.grantReadSlackBotSecrets(taskRole);
        props.voscastServer.grantReadPasswordSecret(taskRole);
        props.voscastServer.grantReadAutoDjKeySecret(taskRole);

        const ecsTaskDefinition = new ecs.Ec2TaskDefinition(this, 'EcsTaskDefinition', {
            family: 'wet-toast-shout-client',
            taskRole: taskRole,
        });

        const environment = {
            ...props.slackBots.envVars(),
            ...props.messageQueue.envVars(),
            AWS_DEFAULT_REGION: Aws.REGION,
            WT_MEDIA_STORE__S3__BUCKET_NAME: props.mediaStore.bucket.bucketName,
            WT_DISC_JOCKEY__SHOUT_CLIENT__PASSWORD: props.voscastServer.password(),
            WT_DISC_JOCKEY__SHOUT_CLIENT__HOSTNAME: props.voscastServer.hostname(),
            WT_DISC_JOCKEY__SHOUT_CLIENT__PORT: props.voscastServer.port(),
            WT_DISC_JOCKEY__SHOUT_CLIENT__AUTODJ_KEY: props.voscastServer.autoDjKey(),
        };

        // t3.micro: 2 vCPU, 1 GiB
        ecsTaskDefinition.addContainer('Container', {
            image: props.image,
            containerName: 'shout-client',
            command: ['disc-jockey', 'stream'],
            memoryLimitMiB: 950, // 2 GB
            cpu: 2048, // 2 vCPUs
            logging: ecs.LogDriver.awsLogs({ logGroup: props.logGroup, streamPrefix: Aws.STACK_NAME }),
            environment,
        });

        new ecs.Ec2Service(this, 'Service', {
            serviceName: 'wet-toast-shout-client-service',
            cluster: cluster.ecsCluster,
            taskDefinition: ecsTaskDefinition,
            desiredCount: 1,
            capacityProviderStrategies: [
                {
                    capacityProvider: cluster.capacityProvider.capacityProviderName,
                    weight: 1,
                },
            ],
            minHealthyPercent: 0,
            maxHealthyPercent: 100,
        });
    }
}
