# デプロイメントガイド

このドキュメントでは、TerraformとGitHub Actionsを使用してAWS LightsailにDiscord Botをデプロイする手順を説明します。

## 概要

- **インフラ管理**: Terraform
- **CI/CD**: GitHub Actions（OIDC認証）
- **デプロイ先**: AWS Lightsail（最小プラン: 512MB RAM, 1 vCPU）
- **コンテナ**: Docker Compose

## 前提条件

- AWSアカウント
- AWS CLIがインストール・設定済み
- Terraform 1.5.0以上がインストール済み
- GitHubリポジトリへのアクセス権限

## 初回セットアップ

### 1. S3バケットとDynamoDBテーブルの作成

Terraformのバックエンド用に、S3バケットとDynamoDBテーブルを手動で作成します。

```bash
# S3バケット作成（グローバルで一意な名前を指定）
aws s3 mb s3://your-terraform-state-bucket-name --region ap-northeast-1

# バージョニング有効化
aws s3api put-bucket-versioning \
  --bucket your-terraform-state-bucket-name \
  --versioning-configuration Status=Enabled

# 暗号化設定
aws s3api put-bucket-encryption \
  --bucket your-terraform-state-bucket-name \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "AES256"
      }
    }]
  }'

# DynamoDBテーブル作成
aws dynamodb create-table \
  --table-name terraform-state-lock \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region ap-northeast-1
```

### 2. GitHub OIDCプロバイダーの設定

GitHub ActionsでOIDC認証を使用するため、AWSにOIDCプロバイダーを設定します。

```bash
aws iam create-open-id-connect-provider \
  --url https://token.actions.githubusercontent.com \
  --client-id-list sts.amazonaws.com \
  --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1
```

> 注意: 既にOIDCプロバイダーが存在する場合は、この手順はスキップしてください。

### 3. Terraform変数の設定

`terraform/terraform.tfvars`ファイルを作成します。

```hcl
aws_region         = "ap-northeast-1"
instance_name      = "discalendar-bot"
bundle_id          = "nano_2_0"
blueprint_id       = "ubuntu_22_04"
github_repository  = "your-username/discalendar-next-bot"
s3_bucket_name     = "your-terraform-state-bucket-name"
dynamodb_table_name = "terraform-state-lock"
```

### 4. Terraformバックエンドの設定

`terraform/backend.tf`ファイルのコメントを解除し、S3バケット名を設定します。

```hcl
terraform {
  backend "s3" {
    bucket         = "your-terraform-state-bucket-name"
    key            = "discalendar-bot/terraform.tfstate"
    region         = "ap-northeast-1"
    dynamodb_table = "terraform-state-lock"
    encrypt        = true
  }
}
```

### 5. 初回Terraform Apply

ローカルでTerraformを実行してリソースを作成します。

```bash
cd terraform

# 初期化
terraform init

# 実行計画の確認
terraform plan

# 適用
terraform apply
```

適用後、以下の出力が表示されます：

- `iam_role_arn`: GitHub Actionsで使用するIAMロールのARN
- `lightsail_instance_public_ip`: LightsailインスタンスのパブリックIP

### 6. GitHub Secretsの設定

GitHubリポジトリのSettings > Secrets and variables > Actionsで以下のSecretsを設定します。

#### 必須Secrets

| Secret名 | 説明 | 取得方法 |
|---------|------|---------|
| `AWS_ROLE_ARN` | IAMロールのARN | Terraform出力の`iam_role_arn` |
| `TF_STATE_BUCKET_NAME` | Terraformステート用S3バケット名 | 手動作成したS3バケット名 |
| `LIGHTSAIL_SSH_PRIVATE_KEY` | Lightsail SSH秘密鍵 | AWS Lightsailコンソールからダウンロード |
| `BOT_TOKEN` | Discord Bot Token | Discord Developer Portal |
| `APPLICATION_ID` | Discord Application ID | Discord Developer Portal |
| `INVITATION_URL` | Bot招待URL | Discord Developer Portal |
| `SUPABASE_URL` | SupabaseプロジェクトURL | Supabase Dashboard |
| `SUPABASE_SERVICE_KEY` | Supabase Service Role Key | Supabase Dashboard |

#### オプションSecrets

| Secret名 | 説明 | デフォルト値 |
|---------|------|------------|
| `LOG_LEVEL` | ログレベル | `INFO` |
| `SENTRY_DSN` | Sentry DSN | 空文字列 |

### 7. Lightsail SSH鍵の取得

LightsailインスタンスにSSH接続するための鍵を取得します。

```bash
# AWS CLIでデフォルト鍵ペアをダウンロード
aws lightsail download-default-key-pair --region ap-northeast-1

# または、Lightsailコンソールから鍵をダウンロード
# 1. Lightsailコンソールにアクセス
# 2. インスタンスを選択
# 3. "Connect using SSH" をクリック
# 4. "Download default key" をクリック
```

ダウンロードした秘密鍵の内容を`LIGHTSAIL_SSH_PRIVATE_KEY`としてGitHub Secretsに設定します。

## デプロイフロー

### 自動デプロイ

`main`ブランチにマージされると、GitHub Actionsワークフローが自動的に実行されます。

1. **Terraform Plan**: 変更内容を確認
2. **Terraform Apply**: リソースを更新
3. **デプロイスクリプト実行**: LightsailインスタンスにSSH接続し、アプリケーションをデプロイ

### 手動デプロイ

GitHub Actionsのワークフローを手動で実行することもできます。

1. GitHubリポジトリの「Actions」タブを開く
2. 「Terraform Apply」ワークフローを選択
3. 「Run workflow」をクリック

### ローカルデプロイ

ローカルから直接デプロイする場合：

```bash
# Terraformでリソース情報を取得
cd terraform
INSTANCE_IP=$(terraform output -raw lightsail_instance_public_ip)
INSTANCE_NAME=$(terraform output -raw lightsail_instance_name)

# デプロイスクリプトを実行
cd ..
export BOT_TOKEN="your-token"
export APPLICATION_ID="your-app-id"
# ... その他の環境変数を設定

./scripts/deploy.sh $INSTANCE_IP $INSTANCE_NAME
```

## トラブルシューティング

### Terraform Applyが失敗する

- S3バケットとDynamoDBテーブルが正しく作成されているか確認
- `terraform/backend.tf`の設定が正しいか確認
- IAM権限が適切に設定されているか確認

### GitHub Actionsが失敗する

- GitHub Secretsが正しく設定されているか確認
- OIDCプロバイダーが正しく設定されているか確認
- IAMロールの信頼ポリシーが正しいか確認

### デプロイが失敗する

- Lightsailインスタンスが起動しているか確認
- SSH鍵が正しく設定されているか確認
- 環境変数が正しく設定されているか確認
- Docker/Docker Composeがインスタンスにインストールされているか確認

### Botが起動しない

- LightsailインスタンスにSSH接続してログを確認
  ```bash
  ssh ubuntu@<public-ip>
  cd /opt/discalendar-bot
  docker compose logs
  ```
- 環境変数が正しく設定されているか確認
- `.env`ファイルの内容を確認

## リソースの削除

Terraformで作成したリソースを削除する場合：

```bash
cd terraform
terraform destroy
```

> 注意: この操作は元に戻せません。すべてのリソースが削除されます。

## コスト見積もり

- **Lightsailインスタンス（最小プラン）**: 約$3.50/月
- **S3バケット（Terraformステート）**: ほぼ無料（使用量に応じて）
- **DynamoDBテーブル（ステートロック）**: ほぼ無料（使用量に応じて）

合計: 約**$3.50/月**

## 参考リンク

- [AWS Lightsail Documentation](https://docs.aws.amazon.com/lightsail/)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [GitHub Actions OIDC](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services)
