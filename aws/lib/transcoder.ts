import {
    aws_ec2 as ec2,
    aws_iam as iam,
    CfnParameter,
    aws_ecs as ecs,
    aws_logs as logs,
    Aws,
    aws_events as events,
    aws_events_targets as targets,
} from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { MediaStore } from './media-store';
import { Cluster } from './cluster';
import { SlackBots } from './slack-bots';

interface TranscoderProps {
    readonly vpc: ec2.Vpc;
    readonly mediaStore: MediaStore;
    readonly image: ecs.EcrImage;
    readonly instanceType: CfnParameter;
    readonly logGroup: logs.LogGroup;
    readonly slackBots: SlackBots;
}

export class Transcoder extends Construct {
    constructor(scope: Construct, id: string, props: TranscoderProps) {
        super(scope, id);

        const cluster = new Cluster(this, 'TranscoderCluster', {
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
        props.slackBots.grantReadSlackBotSecrets(taskRole);

        const ecsTaskDefinition = new ecs.Ec2TaskDefinition(this, 'EcsTaskDefinition', {
            family: 'wet-toast-transcoder',
            taskRole: taskRole,
        });

        const environment = {
            ...props.slackBots.envVars(),
            AWS_DEFAULT_REGION: Aws.REGION,
            WT_MEDIA_STORE__S3__BUCKET_NAME: props.mediaStore.bucket.bucketName,
            WT_DISC_JOCKEY__MEDIA_TRANSCODER__CLEAN_TMP_DIR: 'true',
        };

        // t3.medium: 2 vCPU, 4 GiB
        ecsTaskDefinition.addContainer('Container', {
            image: props.image,
            containerName: 'transcoder',
            command: ['disc-jockey', 'transcode'],
            memoryLimitMiB: 3800, // 4 GB
            cpu: 2048, // 2 vCPUs
            logging: ecs.LogDriver.awsLogs({ logGroup: props.logGroup, streamPrefix: Aws.STACK_NAME }),
            environment,
        });

        // Cron job twice a day at 12h00 UTC and 18h00 UTC
        const schedule = events.Schedule.cron({
            minute: '0',
            hour: '12,18',
            day: '*',
            month: '*',
            year: '*',
        });
        const rule = new events.Rule(this, 'MyScheduledTaskRule', {
            schedule,
        });
        rule.addTarget(
            new targets.EcsTask({
                cluster: cluster.ecsCluster,
                taskDefinition: ecsTaskDefinition,
                taskCount: 1,
                role: taskRole,
            }),
        );
    }
}
