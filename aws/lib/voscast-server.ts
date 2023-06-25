import { Construct } from 'constructs';
import { aws_secretsmanager as secretmanager, CfnParameter, aws_iam as iam } from 'aws-cdk-lib';

interface VoscastServerProps {
    readonly voscastServerHostname: CfnParameter;
    readonly voscastServerPort: CfnParameter;
    readonly voscastPassword: CfnParameter;
    readonly voscastAutoDjKey: CfnParameter;
}

export class VoscastServer extends Construct {
    private readonly voscastPasswordSecret: secretmanager.ISecret;
    private readonly voscastServerHostname: CfnParameter;
    private readonly voscastServerPort: CfnParameter;
    private readonly voscastPassword: CfnParameter;
    private readonly voscastAutoDjKeySecret: secretmanager.ISecret;
    private readonly voscastAutoDjKey: CfnParameter;

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

        this.voscastAutoDjKeySecret = secretmanager.Secret.fromSecretNameV2(
            this,
            'VoscastAutoDjKeySecret',
            'wet-toast-talk-radio/voscast-autodj-key',
        );

        this.voscastAutoDjKey = props.voscastAutoDjKey;
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

    autoDjKey(): string {
        return this.voscastAutoDjKey.valueAsString;
    }

    grantReadAutoDjKeySecret(grantee: iam.IGrantable) {
        this.voscastAutoDjKeySecret.grantRead(grantee);
    }
}
