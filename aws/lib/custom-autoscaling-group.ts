import {
    aws_autoscaling as autoscaling,
    aws_ec2 as ec2,
    aws_iam as iam,
    CfnParameter,
    Duration,
    aws_ecs as ecs,
} from 'aws-cdk-lib';
import { Construct } from 'constructs';

interface CustomAutoScalingGroupProps {
    readonly vpc: ec2.Vpc;
    readonly instanceCount: CfnParameter;
    readonly instanceType: CfnParameter;
    readonly autoscalingGroupSubnetGroupName: string;
}

export class CustomAutoScalingGroup extends Construct {
    readonly autoScalingGoup: autoscaling.AutoScalingGroup;
    readonly securityGroup: ec2.SecurityGroup;

    constructor(scope: Construct, id: string, props: CustomAutoScalingGroupProps) {
        super(scope, id);

        this.securityGroup = new ec2.SecurityGroup(this, 'SecurityGroup', { vpc: props.vpc });

        this.autoScalingGoup = new autoscaling.AutoScalingGroup(this, id, {
            vpc: props.vpc,
            signals: autoscaling.Signals.waitForAll({
                timeout: Duration.minutes(10),
            }),
            maxCapacity: props.instanceCount.valueAsNumber,
            minCapacity: props.instanceCount.valueAsNumber,
            machineImage: ecs.EcsOptimizedImage.amazonLinux2(ecs.AmiHardwareType.STANDARD, {
                cachedInContext: false,
            }),
            instanceType: new ec2.InstanceType(props.instanceType.valueAsString),
            role: new iam.Role(this, 'GroupRole', {
                assumedBy: new iam.ServicePrincipal('ec2.amazonaws.com'),
                managedPolicies: [
                    iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AmazonEC2RoleforSSM'),
                    iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AmazonEC2ContainerServiceforEC2Role'),
                ],
            }),
            vpcSubnets: {
                subnetGroupName: props.autoscalingGroupSubnetGroupName,
            },
            securityGroup: this.securityGroup,
        });

        this.autoScalingGoup.userData.addCommands('yum install -y aws-cfn-bootstrap');
        this.autoScalingGoup.userData.addSignalOnExitCommand(this.autoScalingGoup);
    }
}
