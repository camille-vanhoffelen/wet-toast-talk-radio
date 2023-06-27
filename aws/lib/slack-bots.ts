import { Construct } from 'constructs';
import { aws_secretsmanager as secretmanager, CfnParameter, aws_iam as iam } from 'aws-cdk-lib';

interface SlackBotsProps {
    readonly emergencyAlertSystemUrl: CfnParameter;
    readonly radioOperatorUrl: CfnParameter;
    readonly dev?: boolean | undefined;
}

export class SlackBots extends Construct {
    private readonly emergencyAlertSystemSecret: secretmanager.ISecret;
    private readonly radioOperatorSecret: secretmanager.ISecret;
    private readonly emergencyAlertSystemUrl: CfnParameter;
    private readonly radioOperatorUrl: CfnParameter;
    private readonly dev?: boolean | undefined;

    constructor(scope: Construct, id: string, props: SlackBotsProps) {
        super(scope, id);
        this.emergencyAlertSystemUrl = props.emergencyAlertSystemUrl;
        this.radioOperatorUrl = props.radioOperatorUrl;
        this.dev = props.dev;

        this.emergencyAlertSystemSecret = secretmanager.Secret.fromSecretNameV2(
            this,
            'EmergencyAlertSystemSecret',
            'wet-toast-talk-show/emergency-alert-system/slack-web-hook-url',
        );
        this.radioOperatorSecret = secretmanager.Secret.fromSecretNameV2(
            this,
            'RadioOperatorSecret',
            'wet-toast-talk-show/radio-operator/slack-web-hook-url',
        );
    }

    grantReadSlackBotSecrets(grantee: iam.IGrantable) {
        this.emergencyAlertSystemSecret.grantRead(grantee);
        this.radioOperatorSecret.grantRead(grantee);
    }

    envVars(): { [key: string]: string } {
        if (this.dev) {
            return {};
        } else {
            return {
                WT_EMERGENCY_ALERT_SYSTEM__WEB_HOOK_URL: this.emergencyAlertSystemUrl.valueAsString,
                WT_RADIO_OPERATOR__WEB_HOOK_URL: this.radioOperatorUrl.valueAsString,
            };
        }
    }
}
