import {
    aws_ec2 as ec2,
    aws_sqs as sqs,
    aws_iam as iam,
    CfnParameter,
    aws_ecs as ecs,
    aws_logs as logs,
    aws_autoscaling as autoscaling,
    Aws,
} from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { MediaStore } from './media-store';
import { Cluster } from './cluster';
import { SlackBots } from './slack-bots';
import { ModelCache } from './model-cache';
import { MathExpression } from 'aws-cdk-lib/aws-cloudwatch';
import { resourceName } from './resource-name';

interface AudioGeneratorProps {
    readonly vpc: ec2.Vpc;
    readonly mediaStore: MediaStore;
    readonly queue: sqs.Queue;
    readonly image: ecs.EcrImage;
    readonly instanceType: CfnParameter;
    readonly logGroup: logs.LogGroup;
    readonly slackBots: SlackBots;
    readonly modelCache: ModelCache;
    readonly dev?: boolean | undefined;
}

export class AudioGenerator extends Construct {
    constructor(scope: Construct, id: string, props: AudioGeneratorProps) {
        super(scope, id);

        let maxNumInstances = 2;
        if (props.dev) {
            maxNumInstances = 1;
        }

        const cluster = new Cluster(this, 'AudioGeneratorCluster', {
            vpc: props.vpc,
            clusterName: 'AudioGeneratorCluster',
            image: props.image,
            instanceType: props.instanceType,
            minCapacity: 0,
            maxCapacity: maxNumInstances, // TBD
            logGroup: props.logGroup,
            hardwareType: ecs.AmiHardwareType.GPU,
            spotPrice: '0.25',
            blockDevices: [
                {
                    deviceName: '/dev/xvda',
                    volume: autoscaling.BlockDeviceVolume.ebs(150, {
                        deleteOnTermination: true,
                    }),
                },
            ],
            dev: props.dev,
        });

        const roleName = resourceName('AudioGeneratorTaskRole', props.dev);
        const taskRole = new iam.Role(this, 'EcsTaskRole', {
            roleName,
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
        props.modelCache.bucket.grantRead(taskRole);

        const family = resourceName('wet-toast-audio-generator', props.dev);
        const ecsTaskDefinition = new ecs.Ec2TaskDefinition(this, 'EcsTaskDefinition', {
            family,
            taskRole: taskRole,
        });

        const environment = {
            ...props.slackBots.envVars(),
            AWS_DEFAULT_REGION: Aws.REGION,
            WT_MEDIA_STORE__S3__BUCKET_NAME: props.mediaStore.bucket.bucketName,
            WT_MESSAGE_QUEUE__SQS__STREAM_QUEUE_NAME: props.queue.queueName,
            WT_AUDIO_GENERATOR__USE_S3_MODEL_CACHE: 'true',
        };

        const containerName = resourceName('audio-generator', props.dev);
        // g4dn.xlarge: 4 vCPU, 16 GiB
        ecsTaskDefinition.addContainer('Container', {
            image: props.image,
            containerName,
            command: ['audio-generator', 'run'],
            memoryLimitMiB: 15000,
            cpu: 4096, // 4 vCPU
            logging: ecs.LogDriver.awsLogs({ logGroup: props.logGroup, streamPrefix: Aws.STACK_NAME }),
            environment,
            gpuCount: 1,
        });

        const serviceName = resourceName('wet-toast-audio-generator-service', props.dev);
        const service = new ecs.Ec2Service(this, 'Service', {
            serviceName,
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
            maxCapacity: maxNumInstances,
        });

        const scalingSteps: autoscaling.ScalingInterval[] = [
            { upper: 0, change: 0 },
            { lower: 1, change: maxNumInstances },
        ];

        // for (let i = 1; i < maxNumInstances + 1; i++) {
        // scalingSteps.push({ lower: i, change: i });
        // }

        scaling.scaleOnMetric('MyScalingMetric', {
            metric: new MathExpression({
                expression: 'visibleMessages + notVisibleMessages',
                usingMetrics: {
                    visibleMessages: props.queue.metricApproximateNumberOfMessagesVisible(),
                    notVisibleMessages: props.queue.metricApproximateNumberOfMessagesNotVisible(),
                },
            }),
            adjustmentType: autoscaling.AdjustmentType.EXACT_CAPACITY,
            scalingSteps,
        });
    }
}
