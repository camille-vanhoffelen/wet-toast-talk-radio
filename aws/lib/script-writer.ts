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
import { OpenApi } from './open-api';
import { resourceName } from './resource-name';
import { MessageQueue } from './message-queue';

interface ScriptWriterProps {
    readonly vpc: ec2.Vpc;
    readonly mediaStore: MediaStore;
    readonly messageQueue: MessageQueue;
    readonly image: ecs.EcrImage;
    readonly instanceType: CfnParameter;
    readonly logGroup: logs.LogGroup;
    readonly slackBots: SlackBots;
    readonly openApi: OpenApi;
    readonly dev?: boolean | undefined;
}

export class ScriptWriter extends Construct {
    constructor(scope: Construct, id: string, props: ScriptWriterProps) {
        super(scope, id);

        const cluster = new Cluster(this, 'ScriptWriterCluster', {
            vpc: props.vpc,
            clusterName: 'ScriptWriterCluster',
            image: props.image,
            instanceType: props.instanceType,
            minCapacity: 0,
            maxCapacity: 1,
            logGroup: props.logGroup,
            hardwareType: ecs.AmiHardwareType.STANDARD,
            dev: props.dev,
        });

        const roleName = resourceName('ScriptWriterTaskRole', props.dev);
        const taskRole = new iam.Role(this, 'EcsTaskRole', {
            roleName,
            assumedBy: new iam.ServicePrincipal('ecs-tasks.amazonaws.com'),
        });
        props.mediaStore.bucket.grantReadWrite(taskRole);
        props.messageQueue.grantSendMessages(taskRole);
        props.messageQueue.grantPurge(taskRole);
        props.slackBots.grantReadSlackBotSecrets(taskRole);
        props.openApi.grantReadKeySecret(taskRole);

        const family = resourceName('wet-toast-script-writer', props.dev);
        const ecsTaskDefinition = new ecs.Ec2TaskDefinition(this, 'EcsTaskDefinition', {
            family,
            taskRole: taskRole,
        });

        const environment = {
            ...props.slackBots.envVars(),
            ...props.messageQueue.envVars(),
            AWS_DEFAULT_REGION: Aws.REGION,
            WT_MEDIA_STORE__S3__BUCKET_NAME: props.mediaStore.bucket.bucketName,
            WT_SCRIPTWRITER__LLM__OPENAI_API_KEY: props.openApi.key(),
        };

        const containerName = resourceName('script-writer', props.dev);
        // t2.micro: 1 vCPU, 1 GiB
        ecsTaskDefinition.addContainer('Container', {
            image: props.image,
            containerName,
            command: ['scriptwriter', 'run'],
            memoryLimitMiB: 900, // 1 GB
            cpu: 1024, // 1 vCPUs
            logging: ecs.LogDriver.awsLogs({ logGroup: props.logGroup, streamPrefix: Aws.STACK_NAME }),
            environment,
        });

        // Cron job once a day at 6h00 UTC
        const schedule = events.Schedule.cron({
            minute: '0',
            hour: '6',
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
