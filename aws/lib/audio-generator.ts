import {
    aws_ec2 as ec2,
    aws_sqs as sqs,
    aws_iam as iam,
    CfnParameter,
    aws_ecs as ecs,
    aws_logs as logs,
    aws_autoscaling as autoscaling,
    Aws,
    Duration,
} from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { MediaStore } from './media-store';
import { Cluster } from './cluster';
import { SlackBots } from './slack-bots';

interface AudioGeneratorProps {
    readonly vpc: ec2.Vpc;
    readonly mediaStore: MediaStore;
    readonly queue: sqs.Queue;
    readonly image: ecs.EcrImage;
    readonly instanceType: CfnParameter;
    readonly logGroup: logs.LogGroup;
    readonly slackBots: SlackBots;
}

export class AudioGenerator extends Construct {
    constructor(scope: Construct, id: string, props: AudioGeneratorProps) {
        super(scope, id);

        // TBD
        const numTasks = 2;

        const cluster = new Cluster(this, 'AudioGeneratorCluster', {
            vpc: props.vpc,
            clusterName: 'AudioGeneratorCluster',
            image: props.image,
            instanceType: props.instanceType,
            minCapacity: 0,
            maxCapacity: numTasks, // TBD
            logGroup: props.logGroup,
            hardwareType: ecs.AmiHardwareType.GPU,
            spotPrice: '0.25',
        });

        const taskRole = new iam.Role(this, 'EcsTaskRole', {
            roleName: 'AudioGeneratorTaskRole',
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

        const ecsTaskDefinition = new ecs.Ec2TaskDefinition(this, 'EcsTaskDefinition', {
            family: 'wet-toast-audio-generator',
            taskRole: taskRole,
        });

        const environment = {
            ...props.slackBots.envVars(),
            AWS_REGION: Aws.REGION,
            WT_MEDIA_STORE__S3__BUCKET_NAME: props.mediaStore.bucket.bucketName,
            WT_MESSAGE_QUEUE__SQS__STREAM_QUEUE_NAME: props.queue.queueName,
            WT_AUDIO_GENERATOR__USE_S3_MODEL_CACHE: 'true',
        };

        // g4dn.xlarge: 4 vCPU, 16 GiB
        ecsTaskDefinition.addContainer('Container', {
            image: props.image,
            containerName: 'audio-generator',
            command: ['audio-generator', 'run'],
            memoryLimitMiB: 1500,
            cpu: 3584, // 3.5 vCPU
            logging: ecs.LogDriver.awsLogs({ logGroup: props.logGroup, streamPrefix: Aws.STACK_NAME }),
            environment,
        });

        const service = new ecs.Ec2Service(this, 'Service', {
            serviceName: 'wet-toast-audio-generator-service',
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

        const scaling = service.autoScaleTaskCount({
            minCapacity: 0,
            maxCapacity: numTasks, // TBD
        });

        // Setup scaling metric and cooldown period
        scaling.scaleOnMetric('QueueMessagesVisibleScaling', {
            metric: props.queue.metricApproximateNumberOfMessagesVisible(),
            adjustmentType: autoscaling.AdjustmentType.CHANGE_IN_CAPACITY,
            cooldown: Duration.seconds(300),
            scalingSteps: [
                { upper: 0, change: -numTasks },
                { lower: 1, change: +numTasks },
            ],
        });
    }
}
