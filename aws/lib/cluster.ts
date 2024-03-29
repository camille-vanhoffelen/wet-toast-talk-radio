import {
    aws_autoscaling as autoscaling,
    aws_ec2 as ec2,
    aws_iam as iam,
    CfnParameter,
    Duration,
    aws_ecs as ecs,
    aws_logs as logs,
} from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { resourceName } from './resource-name';

interface ClusterProps {
    readonly vpc: ec2.Vpc;
    readonly clusterName: string;
    readonly image: ecs.EcrImage;
    readonly instanceType: CfnParameter;
    readonly minCapacity: number;
    readonly maxCapacity: number;
    readonly logGroup: logs.LogGroup;
    readonly hardwareType: ecs.AmiHardwareType;
    readonly spotPrice?: string;
    readonly blockDevices?: autoscaling.BlockDevice[];
    readonly dev?: boolean | undefined;
}

export class Cluster extends Construct {
    readonly ecsCluster: ecs.Cluster;
    readonly autoScalingGroup: autoscaling.AutoScalingGroup;
    readonly capacityProvider: ecs.AsgCapacityProvider;

    constructor(scope: Construct, id: string, props: ClusterProps) {
        super(scope, id);

        const clusterName = resourceName(props.clusterName, props.dev);
        const autoScalingGroupName = resourceName(id + 'ASG', props.dev);

        this.ecsCluster = new ecs.Cluster(this, 'Cluster', { vpc: props.vpc, clusterName });
        const autoScalingGroup = new autoscaling.AutoScalingGroup(this, 'AutoscalingGroup', {
            autoScalingGroupName,
            vpc: props.vpc,
            signals: autoscaling.Signals.waitForAll({
                timeout: Duration.minutes(10),
            }),
            maxCapacity: props.maxCapacity,
            minCapacity: props.minCapacity,
            machineImage: ecs.EcsOptimizedImage.amazonLinux2(props.hardwareType, {
                cachedInContext: false,
            }),
            role: new iam.Role(this, 'ASGRole', {
                assumedBy: new iam.ServicePrincipal('ec2.amazonaws.com'),
                managedPolicies: [
                    iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AmazonEC2RoleforSSM'),
                    iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AmazonEC2ContainerServiceforEC2Role'),
                ],
            }),
            instanceType: new ec2.InstanceType(props.instanceType.valueAsString),
            vpcSubnets: {
                subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS,
            },
            newInstancesProtectedFromScaleIn: true,
            spotPrice: props.spotPrice,
            blockDevices: props.blockDevices,
        });
        autoScalingGroup.userData.addCommands('yum install -y aws-cfn-bootstrap');
        autoScalingGroup.userData.addSignalOnExitCommand(autoScalingGroup);

        this.capacityProvider = new ecs.AsgCapacityProvider(this, 'AsgCapacityProvider', {
            autoScalingGroup,
            enableManagedTerminationProtection: true,
            enableManagedScaling: true,
        });
        this.ecsCluster.addAsgCapacityProvider(this.capacityProvider);
        this.ecsCluster.addDefaultCapacityProviderStrategy([
            {
                capacityProvider: this.capacityProvider.capacityProviderName,
                weight: 1,
            },
        ]);
    }
}
