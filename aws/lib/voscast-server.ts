import { Construct } from 'constructs';
import { aws_secretsmanager as secretmanager, CfnParameter, aws_iam as iam } from 'aws-cdk-lib';

interface VoscastServerProps {
    readonly voscastServerHostname: CfnParameter;
    readonly voscastServerPort: CfnParameter;
    readonly voscastPassword: CfnParameter;
}

export class VoscastServer extends Construct {
    private readonly voscastPasswordSecret: secretmanager.ISecret;
    private readonly voscastServerHostname: CfnParameter;
    private readonly voscastServerPort: CfnParameter;
    private readonly voscastPassword: CfnParameter;

    constructor(scope: Construct, id: string, props: VoscastServerProps) {
        super(scope, id);

        this.voscastPasswordSecret = secretmanager.Secret.fromSecretNameV2(
            this,
            'VoscastPasswordSecret',
            'wet-toast-talk-radio/voscast-password',
        );
        this.voscastServerHostname = props.voscastServerHostname;
        this.voscastServerPort = props.voscastServerPort;
        this.voscastPassword = props.voscastPassword;
    }

    hostname(): string {
        return this.voscastServerHostname.valueAsString;
    }

    port(): string {
        return this.voscastServerPort.valueAsString;
    }

    password(): string {
        return this.voscastPassword.valueAsString;
    }

    grantReadPasswordSecret(grantee: iam.IGrantable) {
        this.voscastPasswordSecret.grantRead(grantee);
    }
}
