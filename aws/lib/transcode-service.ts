import {
    aws_autoscaling as autoscaling,
    aws_ec2 as ec2,
    aws_iam as iam,
    CfnParameter,
    Duration,
    aws_ecs as ecs,
    aws_logs as logs,
    aws_events as events,
    aws_events_targets as targets,
    Aws,
} from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { WetToastBucket } from './wet-toast-bucket';
import { Ec2TaskDefinition } from 'aws-cdk-lib/aws-ecs';

interface TranscodeServiceProps {
    readonly vpc: ec2.Vpc;
    readonly wetToastBucket: WetToastBucket;
    readonly cluster: ecs.Cluster;
    readonly image: ecs.EcrImage;
    readonly instanceType: CfnParameter;
    readonly logGroup: logs.LogGroup;
}

export class TranscodeService extends Construct {
    constructor(scope: Construct, id: string, props: TranscodeServiceProps) {
        super(scope, id);

        const autoScalingGroup = new autoscaling.AutoScalingGroup(this, 'AutoscalingGroup', {
            autoScalingGroupName: 'TranscoderASG',
            vpc: props.vpc,
            signals: autoscaling.Signals.waitForAll({
                timeout: Duration.minutes(10),
            }),
            maxCapacity: 1,
            minCapacity: 0,
            machineImage: ecs.EcsOptimizedImage.amazonLinux2(ecs.AmiHardwareType.STANDARD, {
                cachedInContext: false,
            }),
            instanceType: new ec2.InstanceType(props.instanceType.valueAsString),
            vpcSubnets: {
                subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS,
            },
        });
        autoScalingGroup.userData.addCommands('yum install -y aws-cfn-bootstrap');
        autoScalingGroup.userData.addCommands(
            'echo ECS_INSTANCE_ATTRIBUTES={"asg":"transcoder"} >> /etc/ecs/ecs.config',
        );
        autoScalingGroup.userData.addSignalOnExitCommand(autoScalingGroup);
        // Configure the Auto Scaling group to scale based on ECS task count
        autoScalingGroup.scaleOnMetric('EcsTaskCount', {
            metric: props.cluster.metricCpuReservation(), // You can choose any ECS metric to scale on
            scalingSteps: [
                { upper: 0, change: -1 }, // Scale down by 1 instance when there are no tasks
                { lower: 1, change: +1 }, // Scale up by 1 instance when there is at least 1 task
            ],
        });

        const capacityProvider = new ecs.AsgCapacityProvider(this, 'AsgCapacityProvider', {
            autoScalingGroup,
            enableManagedTerminationProtection: true,
            enableManagedScaling: true,
            maximumScalingStepSize: 1,
            minimumScalingStepSize: 1,
            targetCapacityPercent: 100,
        });

        props.cluster.addAsgCapacityProvider(capacityProvider);

        const taskRole = new iam.Role(this, 'EcsTaskRole', {
            roleName: 'TranscoderTaskRole',
            assumedBy: new iam.ServicePrincipal('ecs-tasks.amazonaws.com'),
        });
        props.wetToastBucket.bucket.grantReadWrite(taskRole);

        const ecsTaskDefinition = new ecs.Ec2TaskDefinition(this, 'EcsTaskDefinition', {
            family: 'WetToastTalkShow',
            placementConstraints: [
                ecs.PlacementConstraint.distinctInstances(),
                ecs.PlacementConstraint.memberOf('attribute:asg==transcoder'),
            ],
        });
        ecsTaskDefinition.addContainer('Container', {
            image: props.image,
            command: ['disc-jockey', 'noop'],
            memoryLimitMiB: 4096, // 4 GB
            cpu: 2048, // 2 vCPUs
            logging: ecs.LogDriver.awsLogs({ logGroup: props.logGroup, streamPrefix: Aws.STACK_NAME }),
        });

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
        //         cluster: props.cluster,
        //         taskDefinition: ecsTaskDefinition,
        //         taskCount: 1,
        //         subnetSelection: { subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS },
        //         role: taskRole,
        //     }),
        // );
    }
}
