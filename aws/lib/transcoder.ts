import { aws_ec2 as ec2, aws_iam as iam, CfnParameter, aws_ecs as ecs, aws_logs as logs, Aws } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { MediaStore } from './media-store';
import { Cluster } from './cluster';

interface TranscoderProps {
    readonly vpc: ec2.Vpc;
    readonly mediaStore: MediaStore;
    readonly image: ecs.EcrImage;
    readonly instanceType: CfnParameter;
    readonly logGroup: logs.LogGroup;
}

export class Transcoder extends Construct {
    constructor(scope: Construct, id: string, props: TranscoderProps) {
        super(scope, id);

        new Cluster(this, 'TranscoderCluster', {
            vpc: props.vpc,
            clusterName: 'TranscoderCluster',
            image: props.image,
            instanceType: props.instanceType,
            minCapacity: 0,
            maxCapacity: 1,
            logGroup: props.logGroup,
            hardwareType: ecs.AmiHardwareType.STANDARD,
        });

        const taskRole = new iam.Role(this, 'EcsTaskRole', {
            roleName: 'TranscoderTaskRole',
            assumedBy: new iam.ServicePrincipal('ecs-tasks.amazonaws.com'),
        });
        props.mediaStore.bucket.grantReadWrite(taskRole);

        const ecsTaskDefinition = new ecs.Ec2TaskDefinition(this, 'EcsTaskDefinition', {
            family: 'wet-toast-transcoder',
            taskRole: taskRole,
        });

        // t3.medium: 2 vCPU, 4 GiB
        ecsTaskDefinition.addContainer('Container', {
            image: props.image,
            containerName: 'transcoder',
            command: ['disc-jockey', 'transcode'],
            memoryLimitMiB: 4096, // 4 GB
            cpu: 2048, // 2 vCPUs
            logging: ecs.LogDriver.awsLogs({ logGroup: props.logGroup, streamPrefix: Aws.STACK_NAME }),
            environment: {
                AWS_REGION: Aws.REGION,
                WT_MEDIA_STORE__S3__BUCKET_NAME: props.mediaStore.bucket.bucketName,
            },
        });

        // Cron job twice a day at 1:00 AM and 1:00 PM UTC

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
