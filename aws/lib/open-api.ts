import { Construct } from 'constructs';
import { aws_secretsmanager as secretmanager, CfnParameter, aws_iam as iam } from 'aws-cdk-lib';

interface OpenApiProps {
    readonly openApiKey: CfnParameter;
}

export class OpenApi extends Construct {
    private readonly openApiKey: CfnParameter;
    private readonly openApiKeySecret: secretmanager.ISecret;

    constructor(scope: Construct, id: string, props: OpenApiProps) {
        super(scope, id);

        this.openApiKeySecret = secretmanager.Secret.fromSecretNameV2(
            this,
            'OpenApiKeySecret',
            'wet-toast-talk-radio/scriptwriter/openai-api-key',
        );
        this.openApiKey = props.openApiKey;
    }

    key(): string {
        return this.openApiKey.valueAsString;
    }

    grantReadKeySecret(grantee: iam.IGrantable) {
        this.openApiKeySecret.grantRead(grantee);
    }
}
