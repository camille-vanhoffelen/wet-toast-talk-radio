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

interface AudioGeneratorProps {
    readonly vpc: ec2.Vpc;
    readonly mediaStore: MediaStore;
    readonly queue: sqs.Queue;
    readonly image: ecs.EcrImage;
    readonly instanceType: CfnParameter;
    readonly logGroup: logs.LogGroup;
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

        const ecsTaskDefinition = new ecs.Ec2TaskDefinition(this, 'EcsTaskDefinition', {
            family: 'wet-toast-audio-generator',
            taskRole: taskRole,
        });

        // t2.micro: 1 vCPU, 1 GiB
        ecsTaskDefinition.addContainer('Container', {
            image: props.image,
            containerName: 'audio-generator',
            // command: ['audio-generator', 'run'],
            command: ['noop'],
            memoryLimitMiB: 1024, // TBD
            cpu: 1024, // TBD
            logging: ecs.LogDriver.awsLogs({ logGroup: props.logGroup, streamPrefix: Aws.STACK_NAME }),
            environment: {
                AWS_REGION: Aws.REGION,
                WT_MEDIA_STORE__S3__BUCKET_NAME: props.mediaStore.bucket.bucketName,
                WT_MESSAGE_QUEUE__SQS__STREAM_QUEUE_NAME: props.queue.queueName,
            },
        });

        const service = new ecs.Ec2Service(this, 'Service', {
            serviceName: 'wet-toast-audio-generator-service',
            cluster: cluster.ecsCluster,
            taskDefinition: ecsTaskDefinition,
            desiredCount: 0,
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
