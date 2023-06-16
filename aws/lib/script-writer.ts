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

interface ScriptWriterProps {
    readonly vpc: ec2.Vpc;
    readonly mediaStore: MediaStore;
    readonly queue: sqs.Queue;
    readonly image: ecs.EcrImage;
    readonly instanceType: CfnParameter;
    readonly logGroup: logs.LogGroup;
}

export class ScriptWriter extends Construct {
    constructor(scope: Construct, id: string, props: ScriptWriterProps) {
        super(scope, id);

        new Cluster(this, 'ScriptWriterCluster', {
            vpc: props.vpc,
            clusterName: 'ScriptWriterCluster',
            image: props.image,
            instanceType: props.instanceType,
            minCapacity: 0,
            maxCapacity: 1,
            logGroup: props.logGroup,
            hardwareType: ecs.AmiHardwareType.STANDARD,
        });

        const taskRole = new iam.Role(this, 'EcsTaskRole', {
            roleName: 'ScriptWriterTaskRole',
            assumedBy: new iam.ServicePrincipal('ecs-tasks.amazonaws.com'),
        });
        props.mediaStore.bucket.grantReadWrite(taskRole);
        props.queue.grantSendMessages(taskRole);
        props.queue.grantPurge(taskRole);

        const ecsTaskDefinition = new ecs.Ec2TaskDefinition(this, 'EcsTaskDefinition', {
            family: 'wet-toast-script-writer',
            taskRole: taskRole,
        });

        // t2.micro: 1 vCPU, 1 GiB
        ecsTaskDefinition.addContainer('Container', {
            image: props.image,
            containerName: 'script-writer',
            command: ['scriptwriter', 'run'],
            memoryLimitMiB: 900, // 1 GB
            cpu: 1024, // 1 vCPUs
            logging: ecs.LogDriver.awsLogs({ logGroup: props.logGroup, streamPrefix: Aws.STACK_NAME }),
            environment: {
                AWS_REGION: Aws.REGION,
                WT_MEDIA_STORE__S3__BUCKET_NAME: props.mediaStore.bucket.bucketName,
                WT_MESSAGE_QUEUE__SQS__STREAM_QUEUE_NAME: props.queue.queueName,
            },
        });

        // CRON  TBD

        // const schedule = events.Schedule.cron({
        //     minute: '0',
        //     hour: '1',
        //     day: '*',
        //     month: '*',
        //     year: '*',
        // });
        // const rule = new events.Rule(this, 'MyScheduledTaskRule', {
        //     schedule,
        // });
        // rule.addTarget(
        //     new targets.EcsTask({
        //         cluster: cluster.ecsCluster,
        //         taskDefinition: ecsTaskDefinition,
        //         taskCount: 1,
        //         subnetSelection: { subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS },
        //         role: taskRole,
        //     }),
        // );
    }
}
